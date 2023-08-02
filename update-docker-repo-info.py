#!/usr/bin/env python3

import argparse
import sys
import os
import requests
import datetime
import string
import subprocess
import tempfile
import shutil
import json
import random
import glob
import re
import csv
import time


assert sys.version_info >= (3, 9), "Script compatible with python 3.9 and higher only"

VERIFY_SSL = True

DOCKERFILES_DIR = os.path.abspath(os.getenv('DOCKERFILES_DIR', '.dockerfiles'))
try:
    with open("dockerfiles_general_info", "r") as f:
        DOCKERFILES_GENERAL_INFO = json.load(f)
except Exception:
    DOCKERFILES_GENERAL_INFO = {}


def http_get(url, **kwargs):
    """wrapper function around requests.get which set verify to what we got in the args

    Arguments:
        url {string} -- url to get

    Returns:
        requests.Response -- response from reqeusts.get§
    """
    return requests.get(url, verify=VERIFY_SSL, **kwargs)


def get_docker_image_size(docker_image):
    """Get the size of the image form docker hub
    Arguments:
        docker_image {string} -- the full name of hthe image
    """
    size = "failed querying size"
    for i in (1, 2, 3):
        try:
            name, tag = docker_image.split(':')
            res = http_get('https://hub.docker.com/v2/repositories/{}/tags/{}/'.format(name, tag))
            res.raise_for_status()
            size_bytes = res.json()['images'][0]['size']
            size = '{0:.2f} MB'.format(float(size_bytes)/1024/1024)
        except Exception as ex:
            print("[{}] failed getting image size for image: {}. Err: {}".format(i, docker_image, ex))
            if i != 3:
                print("Sleeping 5 seconds and trying again...")
                time.sleep(5)
    return size


def get_latest_tag(image_name):
    last_tag = None
    last_date = None
    url = "https://registry.hub.docker.com/v2/repositories/{}/tags/?page_size=25".format(image_name)
    while True:
        print("Querying docker hub url: {}".format(url))
        res = http_get(url)
        res.raise_for_status()
        obj = res.json()
        for result in obj['results']:
            name = result['name']
            if len(name) >= 20 and all(c in string.hexdigits for c in name):  # skip git sha revisions
                continue
            date = datetime.datetime.strptime(result['last_updated'], "%Y-%m-%dT%H:%M:%S.%fZ")
            if not last_date or date > last_date:
                last_date = date
                last_tag = result['name']
        if obj['next']:
            url = obj['next']
        else:
            break
    print("last tag: {}, date: {}".format(last_tag, last_date))
    if not last_tag:
        raise Exception('No tag found for image: {}'.format(image_name))
    return (last_tag, last_date)


def get_os_release(image_name):
    res = subprocess.run(["docker", "run", "--rm", image_name, "cat", "/etc/os-release"], text=True, capture_output=True)
    if res.returncode != 0:
        print("failed getting os release for: {} stderr: {}".format(image_name, res.stderr))
        return []
    return res.stdout.splitlines()


def get_python_version(docker_info: str) -> str:
    if python_version := re.search(r'PYTHON_VERSION=(\d+\.\d+\.\d+)', docker_info):
        return python_version.group(1)
    return ''


def inspect_image(image_name, out_file):
    inspect_format = f'''{{{{ range $env := .Config.Env }}}}{{{{ if eq $env "DEPRECATED_IMAGE=true" }}}}## 🔴 IMPORTANT: This image is deprecated 🔴{{{{ end }}}}{{{{ end }}}}
## Docker Metadata
- Image Size: {get_docker_image_size(image_name)}
- Image ID: `{{{{ .Id }}}}`
- Created: `{{{{ .Created }}}}`
- Arch: `{{{{ .Os }}}}`/`{{{{ .Architecture }}}}`
{{{{ if .Config.Entrypoint }}}}- Entrypoint: `{{{{ json .Config.Entrypoint }}}}`
{{{{ end }}}}{{{{ if .Config.Cmd }}}}- Command: `{{{{ json .Config.Cmd }}}}`
{{{{ end }}}}- Environment:{{{{ range .Config.Env }}}}{{{{ "\\n" }}}}  - `{{{{ . }}}}`{{{{ end }}}}
- Labels:{{{{ range $key, $value := .ContainerConfig.Labels }}}}{{{{ "\\n" }}}}  - `{{{{ $key }}}}:{{{{ $value }}}}`{{{{ end }}}}
'''
    docker_info = subprocess.check_output(["docker", "inspect", "-f", inspect_format, image_name], text=True)

    out_file.write(docker_info)
    if not DOCKERFILES_GENERAL_INFO.get(image_name) and (python_version := get_python_version(docker_info)):
        DOCKERFILES_GENERAL_INFO[image_name] = {"python_version": python_version}
    os_info = '- OS Release:'
    release_info = get_os_release(image_name)
    if not release_info:
        os_info += ' `Failed getting os release info`'
    for l in release_info:
        os_info += '\n  - `{}`'.format(l)
    # out_file.write(os_info + '\n\n')


def docker_trust(image_name, out_file):
    try:
        trust_info = subprocess.check_output(["docker", "trust", "inspect", "--pretty", image_name], text=True)
    except Exception:
        trust_info = "No trust data is available"
    out_file.write('## Docker Trust\n```\n{}\n```\n\n'.format(trust_info))


PKG_INFO = '''
### `{name}`

* Summary: {summary}
* Version: {version}
* Pypi: {pypi_url}
* Homepage: {home_page}
* Author: {author}
'''

USED_PACKAGES_FILE = "used_packages.json"
USED_PACKAGES = {}


def clear_image_from_used(base_image):
    """
    Remove the image from all packages referencing this image. Should be called at the
    start of processing of an image
    """
    to_remove = []
    for name, package in USED_PACKAGES.items():
        if base_image in package["docker_images"]:
            package["docker_images"].remove(base_image)
            if len(package["docker_images"]) == 0:
                to_remove.append(name)
    for name in to_remove:
        USED_PACKAGES.pop(name)


def add_package_used(package_name, base_image, licenses, home_page, pypi_url, summary, author):
    package = USED_PACKAGES.get(package_name)
    if package:
        if base_image not in package["docker_images"]:
            package["docker_images"].append(base_image)
    else:
        USED_PACKAGES[package_name] = {
            "docker_images": [base_image],
            "home_page": home_page,
            "pypi_url": pypi_url,
            "author": author,
            "summary": summary,
            "licenses": licenses
        }


def generate_pkg_data(image_name, out_file):
    if not hasattr(generate_pkg_data, "cache"):
        generate_pkg_data.cache = {}
        res = http_get(
            'https://raw.githubusercontent.com/demisto/dockerfiles/master/docker/known_licenses.json?{}'.format(random.randint(1, 1000)))
        res.raise_for_status()
        generate_pkg_data.known_licenses = res.json()["packages"]
        with open("{}/packages_ignore.json".format(sys.path[0])) as f:
            generate_pkg_data.ignore_packages = json.load(f)["packages"]
        # get the licenses exclude from dockerfiles
        res = http_get(
            'https://raw.githubusercontent.com/demisto/dockerfiles/master/docker/packages_license_check_exclude.json?{}'.format(random.randint(1, 1000)))
        res.raise_for_status()
        lic_exclude = res.json()["packages"]
        for k in lic_exclude:
            p = generate_pkg_data.ignore_packages.get(k, {})
            docker_images = p.get('docker_images', [])
            for img in lic_exclude[k].get('docker_images', []):
                if not img.startswith('demisto/'):
                    img = 'demisto/' + img
                docker_images.append(img)
            p['docker_images'] = docker_images
            generate_pkg_data.ignore_packages[k] = p  # could be that we got a key that is not in ignore_packages that we need to set
        print(f'\nknown licenses: {generate_pkg_data.known_licenses}\n')
        print(f'\nignore packages: {generate_pkg_data.ignore_packages}\n')
    # check this image is python
    try:
        subprocess.check_output(["docker", "run", "--rm", image_name, "which", "python"], text=True)
    except subprocess.CalledProcessError as err:
        if err.returncode == 1:
            print(f"{image_name} doesn't seem to have python. Skipping python package check. {err.output}")
            return
        raise
    pip_cmd = 'pip'
    py_cmd = 'python'
    try:
        subprocess.check_output(["docker", "run", "--rm", image_name, "which", "python3"], text=True)
        print("Found python3. Will use python3 and pip3 commands.")
        pip_cmd = 'pip3'
        py_cmd = 'python3'
    except Exception as err:
        print(f'Ignoring `which python3` err: {err}. Assuming we are using python2')
    base_image = image_name.split(":")[0]
    clear_image_from_used(base_image)
    pip_list_json = subprocess.check_output(["docker", "run", "--rm", image_name, "sh", "-c",
                                            f"{pip_cmd} install --upgrade pip > /dev/null; {py_cmd} -m pip list --format=json"], text=True)
    pip_list = json.loads(pip_list_json)
    for pkg in pip_list:
        name = pkg["name"]
        if (name in generate_pkg_data.ignore_packages and
                ((not generate_pkg_data.ignore_packages[name].get("docker_images")) or
                    base_image in generate_pkg_data.ignore_packages[name].get("docker_images"))):
            print("Ignoring package: " + name)
            continue
        print("Getting license for package: {} ...".format(name))
        pip_info = generate_pkg_data.cache.get(name)
        pip_show = None
        if not pip_info:
            try:
                res = http_get("https://pypi.org/pypi/{}/json".format(name))
                res.raise_for_status()
                pip_info = res.json()
                generate_pkg_data.cache[name] = pip_info
            except Exception as ex:
                print("Failed getting info from pypi (will try pip): " + str(ex))
                pip_show = subprocess.check_output(["docker", "run", "--rm", image_name, pip_cmd, "show", name], text=True)
                inner_info = {}
                for line in pip_show.splitlines():
                    values = line.split(":", 1)
                    if len(values) > 1:
                        line_name, val = values
                        inner_info[line_name.lower().replace('-', '_').strip()] = val.strip()
                pip_info = {"info": inner_info}
        else:
            print("Using cache for license data of package: " + name)
        home_page = pip_info["info"].get("home_page")
        author = pip_info["info"].get("author")
        author_email = pip_info["info"].get("author_email")
        if author_email and author_email.lower() != 'unknown':
            if not author:
                author = author_email
            else:
                author = author + ' ' + author_email
        summary = pip_info["info"].get("summary")
        pypi_url = pip_info["info"].get("package_url")
        out_file.write(PKG_INFO.format(name=name, summary=summary, version=pkg["version"],
                       pypi_url=pypi_url, home_page=home_page, author=author))
        classifier_found = False
        classifier_list = None
        if name in generate_pkg_data.known_licenses:
            classifier_list = [generate_pkg_data.known_licenses[name]["license"]]
        else:
            classifier_list = pip_info["info"].get("classifiers")
        found_licenses = []
        if classifier_list:
            for classifier in classifier_list:
                if classifier.startswith("License ::") and classifier != "License :: OSI Approved":
                    classifier_found = True
                    found_licenses.append(classifier)
                    out_file.write("* {}\n".format(classifier))
        if not classifier_found:
            # try getting license via pip show
            if not pip_show:
                pip_show = subprocess.check_output(["docker", "run", "--rm", image_name, pip_cmd, "show", name], text=True)
            for line in pip_show.splitlines():
                if line.startswith("License:"):
                    out_file.write("* {}\n".format(line))
                    found_licenses.append(line)
        add_package_used(name, base_image, found_licenses, home_page, pypi_url, summary, author)


def list_os_packages(image_name, out_file):
    res = subprocess.run(["docker", "run", "--rm", image_name, "sh", "-c", "grep -i alpine /etc/issue"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # noqa
    if res.returncode == 0:  # alpine
        output = subprocess.check_output(["docker", "run", "--rm", image_name, "sh", "-c",
            "apk list -I | sort"], text=True, stderr=subprocess.DEVNULL)  # noqa
        os_pkgs = [" ".join(l.split()[0:3]) for l in output.splitlines()]
    else:
        output = subprocess.check_output(["docker", "run", "--rm", image_name, "sh", "-c",
            "dpkg-query --show | sort"], text=True)  # noqa
        os_pkgs = output.splitlines()
    md_lines = ["* " + x for x in os_pkgs]
    out_file.write("\n".join(md_lines))
    out_file.write("\n")


def process_image(image_name, force):
    print("=================\nProcessing: " + image_name)
    master_dir = f'docker/{image_name.split("/")[1]}'
    # master_date = subprocess.check_output(['git', '--no-pager', 'log', '-1', '--format=%ct', 'origin/master', '--', master_dir], text=True, cwd=DOCKERFILES_DIR).strip()
    # if not master_date:
    #     print(f"Skipping image: {image_name} as it is not in our master repository")
    #     return
    # info_date = subprocess.check_output(['git', '--no-pager', 'log', '-1', '--format=%ct', '--', image_name], text=True).strip()
    # if info_date and int(info_date) > int(master_date):
    #     print(f"Skipping image: {image_name} as info modify date: {info_date} is greater than master date: {master_date}")
    #     return
    # print(f"Checking last tag for: {image_name}. master date: [{master_date}]. info date: [{info_date}]")
    last_tag, last_date = get_latest_tag(image_name)
    full_name = "{}:{}".format(image_name, last_tag)
    dir = "{}/{}".format(sys.path[0], image_name)
    if not os.path.exists(dir):
        os.makedirs(dir)
    info_file = "{}/{}.md".format(dir, last_tag)
    last_file = "{}/last.md".format(dir)
    # if not force and os.path.exists(info_file):
    #     print("Info file: {} exists skipping image".format(info_file))
    #     return
    print("Downloading docker image: {}...".format(full_name))
    subprocess.call(["docker", "pull", full_name])
    temp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
    print("Using temp file: " + temp_file.name)
    try:
        temp_file.write("# `{}:{}`\n".format(image_name, last_tag))
        inspect_image(full_name, temp_file)
        docker_trust(full_name, temp_file)
        temp_file.write("## `Python Packages`\n\n")
        generate_pkg_data(full_name, temp_file)
        temp_file.write("\n## `OS Packages`\n\n")
        list_os_packages(full_name, temp_file)
        temp_file.close()
        shutil.move(temp_file.name, info_file)
        shutil.copy(info_file, last_file)
    except Exception as e:
        print("Error: {}".format(e))
        if isinstance(e, subprocess.CalledProcessError):
            print("Stderr: {}".format(e.stderr))
        os.remove(temp_file.name)
        raise


def process_org(org_name, force):
    url = "https://registry.hub.docker.com/v2/repositories/{}/?page_size=100".format(org_name)
    with open("{}/images_ignore.txt".format(sys.path[0])) as f:
        ignore_list = list(filter(lambda x: not x.startswith('#'), f.read().splitlines()))
        print("ingore list: {}".format(ignore_list))
    while True:
        print("Querying docker hub url: {}".format(url))
        res = http_get(url)
        res.raise_for_status()
        obj = res.json()
        for result in obj['results']:
            name = "{}/{}".format(org_name, result['name'])
            if name not in ignore_list:
                process_image(name, force)
        if obj['next']:
            url = obj['next']
        else:
            break


def generate_readme_listing():
    with open('README.md', "r") as f:
        readme_lines = f.readlines()
    list_title_indx = readme_lines.index('## Docker Image List\n')
    trunc_readme = readme_lines[0:list_title_indx+1]
    with open('README.md', 'w') as f:
        f.writelines(trunc_readme)
        last_files = sorted(glob.glob('*/*/last.md'), key=lambda path: "/".join(path.split('/')[0:2]))
        for last_f in last_files:
            docker_image = "/".join(last_f.split('/')[0:2])
            f.write("* [{}]({})\n".format(docker_image, last_f))
        f.write("\n---\nLast updated: {}".format(datetime.datetime.now()))


def short_license(full_license):
    res = re.sub(r'License :: OSI Approved ::\s*', "", full_license, flags=re.I)
    return re.sub(r'License\s*:+\s*', "", res, flags=re.I)


def generate_csv():
    with open('used_packages.csv', "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['Package Name', 'License', 'Homepage', 'Pypi Link', 'Author', 'Summary', 'Docker images'])
        for name, value in sorted(USED_PACKAGES.items(), key=lambda name_val: name_val[0].lower()):
            lic = ", ".join(map(short_license, value.get('licenses')))
            csv_writer.writerow([name, lic, value.get('home_page'), value.get('pypi_url'),
                                value.get('author'), value.get('summary'), ", ".join(value.get('docker_images'))])


def generate_dockers_info_json():
    with open("dockerfiles_content_info", "w") as fp:
        fp.write(json.dumps(DOCKERFILES_GENERAL_INFO, indent=4))


def checkout_dockerfiles_repo():
    if os.path.exists(DOCKERFILES_DIR):
        print(f'dockerfiles dir {DOCKERFILES_DIR} exists. Skipping checkout!')
        return
    print(f'checking out dockerfiles project to: {DOCKERFILES_DIR}'
          ' (Note: for local testing you can set the  env var DOCKERFILES_DIR to your dockerfiles repo to avoid this checkout) ....')
    os.mkdir(DOCKERFILES_DIR)
    subprocess.check_call(['git', 'clone', 'https://github.com/demisto/dockerfiles', DOCKERFILES_DIR])


def get_python_ver():
    docker_images = [
       "demisto/python3:3.10.12.63474",
       "demisto/crypto:1.0.0.66562",
       "demisto/pyjwt3:1.0.0.48806",
       "demisto/python3:3.10.12.66339",
       "demisto/python_pancloud_v2:1.0.0.64955",
       "demisto/py3-tools:1.0.0.49475",
       "demisto/python3:3.10.12.65389",
       "demisto/google-api-py3:1.0.0.64100",
       "demisto/glpi:1.0.0.65890",
       "demisto/fastapi:1.0.0.36992",
       "demisto/fastapi:1.0.0.64153",
       "demisto/boto3py3:1.0.0.67319",
       "demisto/lxml:1.0.0.66590",
       "demisto/polyswarm:1.0.0.18926",
       "demisto/pymisp2:1.0.0.66985",
       "demisto/fp-smc:1.0.22.66577",
       "demisto/py3-tools:1.0.0.67011",
       "demisto/py3-tools:1.0.0.67089",
       "demisto/fastapi:1.0.0.27446",
       "demisto/taxii2:1.0.0.66032",
       "demisto/crypto:1.0.0.63672",
       "demisto/netutils:1.0.0.24101",
       "demisto/chromium:1.0.0.56296",
       "demisto/py42:1.0.0.66909",
       "demisto/ansible-runner:1.0.0.24037",
       "demisto/python_pancloud:1.0.0.66801",
       "demisto/akamai:1.0.0.63810",
       "demisto/btfl-soup:1.0.1.45563",
       "demisto/hashicorp:1.0.0.65633",
       "demisto/blueliv:1.0.0.52588",
       "demisto/taxii:1.0.0.45815",
       "demisto/taxii2:1.0.0.61540",
       "demisto/syslog:1.0.0.61542",
       "demisto/syslog:1.0.0.48738",
       "demisto/pydantic-jwt3:1.0.0.64406",
       "demisto/pyjwt3:1.0.0.63826",
       "demisto/devo:1.0.0.66471",
       "demisto/boto3py3:1.0.0.38849",
       "demisto/python3:3.10.5.31928",
       "demisto/google-cloud-storage:1.0.0.25839",
       "demisto/fastapi:1.0.0.61475",
       "demisto/google-cloud-translate:1.0.0.63615",
       "demisto/pycountry:1.0.0.65943",
       "demisto/bottle:1.0.0.32745",
       "demisto/boto3py3:1.0.0.52713",
       "demisto/googleapi-python3:1.0.0.65068",
       "demisto/py3-tools:0.0.1.25751",
       "demisto/pyjwt3:1.0.0.66845",
       "demisto/boto3py3:1.0.0.45936",
       "demisto/boto3py3:1.0.0.66174",
       "demisto/ntlm:1.0.0.44693",
       "demisto/googleapi-python3:1.0.0.66918",
       "demisto/googleapi-python3:1.0.0.63869",
       "demisto/winrm:1.0.0.13142",
       "demisto/teams:1.0.0.14902",
       "demisto/powershell-ubuntu:7.2.2.29705",
       "demisto/py3-tools:1.0.0.49572",
       "demisto/google-api-py3:1.0.0.65791",
       "demisto/taxii-server:1.0.0.66858",
       "demisto/py3-tools:1.0.0.31193",
       "demisto/pyjwt3:1.0.0.23674",
       "demisto/googleapi-python3:1.0.0.67173",
       "demisto/py3-tools:1.0.0.65317",
       "demisto/boto3py3:1.0.0.41082",
       "demisto/pyotrs:1.0.0.44880",
       "demisto/btfl-soup:1.0.1.46582",
       "demisto/pwsh-exchangev3:1.0.0.49863",
       "demisto/xml-feed:1.0.0.63829",
       "demisto/taxii2:1.0.0.63768",
       "demisto/datadog-api-client:1.0.0.65877",
       "demisto/py3-tools:1.0.0.56465",
       "demisto/netmiko:1.0.0.67498",
       "demisto/google-api-py3:1.0.0.55175",
       "demisto/cloudshare:1.0.0.14120",
       "demisto/rubrik-polaris-sdk-py3:1.0.0.66039",
       "demisto/py3ews:1.0.0.66850",
       "demisto/pwsh-exchangev3:1.0.0.67228",
       "demisto/powershell-ubuntu:7.3.0.49844",
       "demisto/netmiko:1.0.0.65807",
       "demisto/opencti-v4:1.0.0.46493",
       "demisto/reversinglabs-sdk-py3:2.0.0.64132",
       "demisto/pan-os-python:1.0.0.66894",
       "demisto/py3-tools:1.0.0.44868",
       "demisto/reversinglabs-sdk-py3:2.0.0.40822",
       "demisto/btfl-soup:1.0.1.63668",
       "demisto/accessdata:1.1.0.33872",
       "demisto/dxl:1.0.0.63890",
       "demisto/py3-tools:1.0.0.63856",
       "demisto/dxl:1.0.0.35274",
       "demisto/pydantic-jwt3:1.0.0.63835",
       "demisto/splunksdk:1.0.0.49073",
       "demisto/paho-mqtt:1.0.0.19143",
       "demisto/boto3py3:1.0.0.63019",
       "demisto/py-ews:5.0.2.63879",
       "demisto/cymruwhois:1.0.0.65875",
       "demisto/boto3py3:1.0.0.63655",
       "demisto/py3-tools:1.0.0.66127",
       "demisto/snowflake:1.0.0.2505",
       "demisto/googleapi-python3:1.0.0.62073",
       "demisto/akamai:1.0.0.65229",
       "demisto/pydantic-jwt3:1.0.0.45851",
       "demisto/argus-toolbelt:2.0.0.29288",
       "demisto/ippysocks-py3:1.0.0.63627",
       "demisto/pycountry:1.0.0.66907",
       "demisto/py3-tools:1.0.0.49703",
       "demisto/py3-tools:1.0.0.45685",
       "demisto/yolo-coco:1.0.0.15530",
       "demisto/dnstwist:1.0.0.46433",
       "demisto/xml-feed:1.0.0.29458",
       "demisto/opencti-v4:1.0.0.61509",
       "demisto/python3-deb:3.9.1.15758",
       "demisto/carbon-black-cloud:1.0.0.64437",
       "demisto/akamai:1.0.0.34769",
       "demisto/octoxlabs:1.0.0.65919",
       "demisto/boto3py3:1.0.0.67266",
       "demisto/illumio:1.0.0.65903",
       "demisto/oauthlib:1.0.0.38743",
       "demisto/fastapi:1.0.0.63688",
       "demisto/xsoar-tools:1.0.0.25075",
       "demisto/oci:1.0.0.65918",
       "demisto/powershell-ubuntu:7.1.3.22304",
       "demisto/bigquery:1.0.0.61798",
       "demisto/graphql:1.0.0.65897",
       "demisto/flask-nginx:1.0.0.65013",
       "demisto/boto3py3:1.0.0.41926",
       "demisto/oauthlib:1.0.0.63821",
       "demisto/tidy:1.0.0.62989",
       "demisto/minio:1.0.0.19143",
       "demisto/fastapi:1.0.0.64474",
       "demisto/m2crypto:1.0.0.65914",
       "demisto/py3-tools:1.0.0.64131",
       "demisto/resilient:2.0.0.45701",
       "demisto/duoadmin3:1.0.0.65621",
       "demisto/googleapi-python3:1.0.0.65453",
       "demisto/joe-security:1.0.0.46413",
       "demisto/confluent-kafka:1.0.0.65871",
       "demisto/graphql:1.0.0.45620",
       "demisto/bs4-py3:1.0.0.48637",
       "demisto/netmiko:1.0.0.62777",
       "demisto/google-k8s-engine:1.0.0.64696",
       "demisto/taxii:1.0.0.43208",
       "demisto/py3-tools:1.0.0.66062",
       "demisto/fastapi:1.0.0.56647",
       "demisto/fastapi:1.0.0.65888",
       "demisto/keeper-ksm:1.0.0.67054",
       "demisto/greynoise:1.0.0.65909",
       "demisto/greynoise:1.0.0.61972",
       "demisto/exodusintelligence:1.0.0.34185",
       "demisto/pyjwt3:1.0.0.27257",
       "demisto/python3-deb:3.10.12.63475",
       "demisto/pyjwt3:1.0.0.55864",
       "demisto/pyjwt3:1.0.0.67573",
       "demisto/smbprotocol:1.0.0.63639",
       "demisto/google-vision-api:1.0.0.63870",
       "demisto/ntlm:1.0.0.64630",
       "demisto/bs4:1.0.0.24033",
       "demisto/uptycs:1.0.0.63766",
       "demisto/boto3py3:1.0.0.48955",
       "demisto/py3-tools:1.0.0.45904",
       "demisto/google-kms:1.0.0.62005",
       "demisto/slackv3:1.0.0.63762",
       "demisto/py3-tools:1.0.0.47376",
       "demisto/taxii-server:1.0.0.32901",
       "demisto/flask-nginx:1.0.0.66841",
       "demisto/sixgill:1.0.0.66910",
       "demisto/ibm-db2:1.0.0.27972",
       "demisto/armorblox:1.0.0.65856",
       "demisto/lacework:1.0.0.47313",
       "demisto/genericsql:1.1.0.62758",
       "demisto/py3-tools:1.0.0.47433",
       "demisto/pycef:1.0.0.61516",
       "demisto/pwsh-infocyte:1.1.0.23036",
       "demisto/crypto:1.0.0.61689",
       "demisto/fastapi:1.0.0.32142",
       "demisto/axonius:1.0.0.40908",
       "demisto/cloaken:1.0.0.44754",
       "demisto/ntlm:1.0.0.31381",
       "demisto/google-cloud-storage:1.0.0.63865",
       "demisto/nmap:1.0.0.46402",
       "demisto/py3-tools:1.0.0.49159",
       "demisto/py3-tools:1.0.0.66616",
       "demisto/splunksdk-py3:1.0.0.66897",
       "demisto/boto3py3:1.0.0.64969",
       "demisto/boto3py3:1.0.0.67091",
       "demisto/tesseract:1.0.0.62842",
       "demisto/googleapi-python3:1.0.0.40612",
       "demisto/opnsense:1.0.0.65922",
       "demisto/faker3:1.0.0.17991",
       "demisto/azure-kusto-data:1.0.0.66840",
       "demisto/googleapi-python3:1.0.0.64742",
       "demisto/taxii2:1.0.0.57584",
       "demisto/crypto:1.0.0.58095",
       "demisto/py3-tools:0.0.1.30715",
       "demisto/trustar:20.2.0.65839",
       "demisto/boto3:2.0.0.52592",
       "demisto/bottle:1.0.0.65861",
       "demisto/boto3py3:1.0.0.33827",
       "demisto/google-api-py3:1.0.0.64930",
       "demisto/netutils:1.0.0.46652",
       "demisto/googleapi-python3:1.0.0.62767",
       "demisto/netmiko:1.0.0.61830",
       "demisto/feed-performance-test:1.0.46565",
       "demisto/dxl:1.0.0.65407",
       "demisto/py3-tools:1.0.0.61931",
       "demisto/gdetect:1.0.0.29628",
       "demisto/googleapi-python3:1.0.0.64222",
       "demisto/teams:1.0.0.66853",
       "demisto/sixgill:1.0.0.20925",
       "demisto/sixgill:1.0.0.23434",
       "demisto/vmware:2.0.0.43555",
       "demisto/unifi-video:1.0.0.16705",
       "demisto/py3-tools:1.0.0.49929",
       "demisto/python3:3.10.11.58677",
       "demisto/python3:3.9.7.24076",
       "demisto/python3:3.10.10.48392",
       "demisto/python3:3.10.6.33415",
       "demisto/python3:3.8.6.13358",
       "demisto/etl2pcap:1.0.0.19032",
       "demisto/python3:3.10.9.45313",
       "demisto/bs4-py3:1.0.0.30051",
       "demisto/powershell:7.2.1.26295",
       "demisto/python-phash:1.0.0.25389",
       "demisto/sane-doc-reports:1.0.0.27897",
       "demisto/jq:1.0.0.24037",
       "demisto/py3-tools:1.0.0.38394",
       "demisto/ssl-analyze:1.0.0.14890",
       "demisto/python3:3.10.8.36650",
       "demisto/python3:3.10.10.51930",
       "demisto/python3:3.10.4.27798",
       "demisto/python3:3.10.11.61265",
       "demisto/py3-tools:1.0.0.45198",
       "demisto/python3:3.10.10.49934",
       "demisto/crypto:1.0.0.65874",
       "demisto/stringsifter:3.20230711.65151",
       "demisto/python3:3.10.9.40422",
       "demisto/python3:3.10.4.30607",
       "demisto/unzip:1.0.0.19258",
       "demisto/python3:3.10.4.29342",
       "demisto/python3:3.10.9.42476",
       "demisto/python3:3.10.9.46032",
       "demisto/python3:3.10.8.37753",
       "demisto/python3:3.10.9.46807",
       "demisto/pwsh-exchange:1.0.0.34118",
       "demisto/bs4-py3:1.0.0.24176",
       "demisto/python3:3.9.9.25564",
       "demisto/python3:3.10.5.31797",
       "demisto/yarapy:1.0.0.10928",
       "demisto/bs4-tld:1.0.0.63807",
       "demisto/ansible-runner:1.0.0.47562",
       "demisto/pycountry:1.0.0.36195",
       "demisto/python3:3.9.8.24399",
       "demisto/mlurlphishing:1.0.0.28347",
       "demisto/xsoar-tools:1.0.0.36076",
       "demisto/xsoar-tools:1.0.0.42327",
       "demisto/xsoar-tools:1.0.0.62936",
       "demisto/xsoar-tools:1.0.0.40869",
       "demisto/xsoar-tools:1.0.0.19258",
       "demisto/parse-emails:1.0.0.63730",
       "demisto/ml:1.0.0.45981",
       "demisto/ml:1.0.0.32340",
       "demisto/python3:3.9.5.20070",
       "demisto/python:2.7.18.10627",
       "demisto/ml:1.0.0.20606",
       "demisto/python3:3.10.9.44472",
       "demisto/python3:3.8.3.9324",
       "demisto/pandas:1.0.0.31117",
       "demisto/sklearn:1.0.0.64885",
       "demisto/py3-tools:1.0.0.50499",
       "demisto/python3:3.10.11.56082",
       "demisto/python3:3.10.8.37233",
       "demisto/bs4-py3:1.0.0.63660",
       "demisto/sklearn:1.0.0.29944",
       "demisto/pcap-miner:1.0.0.32154",
       "demisto/pcap-miner:1.0.0.10664",
       "demisto/pcap-miner:1.0.0.9769",
       "demisto/pcap-miner:1.0.0.30520",
       "demisto/python3:3.10.11.54132",
       "demisto/python3:3.8.6.12176",
       "demisto/ansible-runner:1.0.0.20884",
       "demisto/python3:3.10.1.27636",
       "demisto/flask-nginx:1.0.0.20328",
       "demisto/pyjwt3:1.0.0.49643",
       "demisto/python3:3.9.5.21272",
       "demisto/crypto:1.0.0.52480",
       "demisto/googleapi-python3:1.0.0.12698",
       "demisto/fastapi:1.0.0.28667",
       "demisto/taxii2:1.0.0.23423",
       "demisto/python3:3.10.1.25933",
       "demisto/teams:1.0.0.43500",
       "demisto/readpdf:1.0.0.43274",
       "demisto/readpdf:1.0.0.50963",
       "demisto/mlurlphishing:1.0.0.61412",
       "demisto/iputils:1.0.0.4663",
       "demisto/dnspython:1.0.0.12410",
       "demisto/powershell:7.1.3.22028",
       "demisto/parse-emails:1.0.0.67069",
       "demisto/pandas:1.0.0.26289",
       "demisto/processing-image-file:1.0.0.66515",
       "demisto/bs4-tld:1.0.0.21999",
       "demisto/xml-feed:1.0.0.65027",
       "demisto/office-utils:2.0.0.54910",
       "demisto/aquatone:2.0.0.36846",
       "demisto/office-utils:2.0.0.49835",
       "demisto/netutils:1.0.0.43061",
       "demisto/pcap-http-extractor:1.0.0.32113",
       "demisto/py3-tools:1.0.0.58222",
       "demisto/nltk:2.0.0.19143",
       "demisto/xsoar-tools:1.0.0.46482",
       "demisto/docxpy:1.0.0.40261",
       "demisto/ssdeep:1.0.0.23743",
       "demisto/python3-deb:3.10.10.49238",
       "demisto/unzip:1.0.0.61858",
       "demisto/xslxwriter:1.0.0.45070",
       "demisto/py3-tools:1.0.0.46591",
       "demisto/btfl-soup:1.0.1.6233",
       "demisto/ml:1.0.0.62124",
       "demisto/taxii:1.0.0.48109",
       "demisto/ml:1.0.0.23334",
       "demisto/xsoar-tools:1.0.0.58259",
       "demisto/mlclustering:1.0.0.23151",
       "demisto/sklearn:1.0.0.49796",
       "demisto/sane-pdf-reports:1.0.0.62999",
       "demisto/ml:1.0.0.30541",
       "demisto/ml:1.0.0.57750",
       "demisto/python:2.7.18.63476",
       "demisto/python3:3.9.1.14969",
       "demisto/rakyll-hey:1.0.0.49364",
       "demisto/python:2.7.18.9326",
       "demisto/docxpy:1.0.0.33689",
       "demisto/python:2.7.18.27799",
       "demisto/python3:3.7.4.977",
       "demisto/python3:3.10.8.35482",
       "demisto/python3:3.7.4.2245",
       "demisto/archer:1.0.0.270",
       "demisto/faker3:1.0.0.247",
       "demisto/sixgill:1.0.0.28665",
       "demisto/powershell-teams:1.0.0.22275"
    ]

    def get_python_version_from_md(folder_name, tag):
        from pathlib import Path
        if Path(f"demisto/{folder_name}/{tag}.md").exists():
            with open(f"demisto/{folder_name}/{tag}.md") as fp:
                python_ver = get_python_version(fp.read())
                # print(f'python version for docker image: demisto/{folder_name}/{tag} is {python_ver=}')
                return python_ver
        print(f'demisto/{folder_name}/{tag}.md do not exist')
        return ''

    DOCKERFILES_GENERAL_INFO["docker_images"] = {}

    for di in docker_images:
        folder_name, tag = di.replace("demisto/", "").split(":")
        if folder_name not in DOCKERFILES_GENERAL_INFO["docker_images"]:
            DOCKERFILES_GENERAL_INFO['docker_images'][folder_name] = {}
        if tag in DOCKERFILES_GENERAL_INFO["docker_images"][folder_name]:
            continue
        else:
            DOCKERFILES_GENERAL_INFO["docker_images"][folder_name][tag] = {
                "python_version": get_python_version_from_md(folder_name, tag)
            }

    print(DOCKERFILES_GENERAL_INFO)


def get_docker_images_content():
    import io
    with io.open('records.json', 'r', encoding='utf-8-sig') as fp:
        docker_images = json.load(fp)

    l = []

    for d in docker_images:
        l.append(d["n.docker_image"])

    print(l)

def main():
    parser = argparse.ArgumentParser(description='Fetch docker repo info. Will fetch the docker image and then generate license info',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("docker_image", help="The docker image name to use (ie: demisto/python). Optional." +
                        "If not specified will scan all images in the demisto organization", nargs="?")
    parser.add_argument("--force", help="Force refetch even if license data already exists", action='store_true')
    parser.add_argument("--no-verify-ssl", help="Don't verify ssl certs for requests (for testing behind corp firewall)", action='store_true')
    args = parser.parse_args()
    # get_docker_images_content()
    get_python_ver()
    global VERIFY_SSL
    VERIFY_SSL = not args.no_verify_ssl
    if not VERIFY_SSL:
        requests.packages.urllib3.disable_warnings()
    global USED_PACKAGES
    # checkout_dockerfiles_repo()
    used_packages_path = "{}/{}".format(sys.path[0], USED_PACKAGES_FILE)
    if os.path.isfile(used_packages_path):
        with open(used_packages_path) as f:
            USED_PACKAGES = json.load(f)
    try:
        if args.docker_image:
            process_image(args.docker_image, args.force)
        else:
            process_org("demisto", args.force)
    finally:
        with open(used_packages_path, "w") as f:
            json.dump(USED_PACKAGES, f, sort_keys=True,
                      indent=4, separators=(',', ': '))
    generate_readme_listing()
    generate_csv()
    generate_dockers_info_json()


if __name__ == "__main__":
    main()
