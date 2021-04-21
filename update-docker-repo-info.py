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


assert sys.version_info >= (3, 7), "Script compatible with python 3.7 and higher only"

VERIFY_SSL = True


def http_get(url, **kwargs):
    """wrapper function around reqeusts.get which set verfiy to what we got in the args

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


def inspect_image(image_name, out_file):
    inspect_format = '''- Image ID: `{{ .Id }}`
- Created: `{{ .Created }}`
- Arch: `{{ .Os }}`/`{{ .Architecture }}`
{{ if .Config.Entrypoint }}- Entrypoint: `{{ json .Config.Entrypoint }}`
{{ end }}{{ if .Config.Cmd }}- Command: `{{ json .Config.Cmd }}`
{{ end }}- Environment:{{ range .Config.Env }}{{ "\\n" }}  - `{{ . }}`{{ end }}
- Labels:{{ range $key, $value := .ContainerConfig.Labels }}{{ "\\n" }}  - `{{ $key }}:{{ $value }}`{{ end }}
'''
    docker_info = subprocess.check_output(["docker", "inspect", "-f", inspect_format, image_name], text=True)
    out_file.write('## Docker Metadata\n- Image Size: `{}`\n{}'.format(get_docker_image_size(image_name), docker_info))
    os_info = '- OS Release:'
    release_info = get_os_release(image_name)
    if not release_info:
        os_info += ' `Failed getting os release info`'
    for l in release_info:
        os_info += '\n  - `{}`'.format(l)
    out_file.write(os_info + '\n\n')


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
    # check this image is python
    try:
        subprocess.check_output(["docker", "run", "--rm", image_name, "which", "python"], text=True)
    except subprocess.CalledProcessError as err:
        if err.returncode == 1:
            print("{} doesn't seem to have python. Skipping python package check. {}".format(image_name, err.output))
            return
        raise
    base_image = image_name.split(":")[0]
    clear_image_from_used(base_image)
    pip_list_json = subprocess.check_output(["docker", "run", "--rm", image_name, "sh", "-c",
                                            "pip install --upgrade pip > /dev/null; python -m pip list --format=json"], text=True)
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
                pip_show = subprocess.check_output(["docker", "run", "--rm", image_name, "pip", "show", name], text=True)
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
                pip_show = subprocess.check_output(["docker", "run", "--rm", image_name, "pip", "show", name], text=True)
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
    master_date = subprocess.check_output(['git', '--no-pager', 'log', '-1', '--format=%ct', 'origin/master', '--', master_dir], text=True).strip()
    if not master_date:
        print(f"Skipping image: {image_name} as it is not in our master repository")
        return
    info_date = subprocess.check_output(['git', '--no-pager', 'log', '-1', '--format=%ct', '--', image_name], text=True).strip()
    if info_date and int(info_date) > int(master_date):
        print(f"Skipping image: {image_name} as info modify date: {info_date} is greater than master date: {master_date}")
        return
    print(f"Checking last tag for: {image_name}. master date: [{master_date}]. info date: [{info_date}]")
    last_tag, last_date = get_latest_tag(image_name)
    full_name = "{}:{}".format(image_name, last_tag)
    dir = "{}/{}".format(sys.path[0], image_name)
    if not os.path.exists(dir):
        os.makedirs(dir)
    info_file = "{}/{}.md".format(dir, last_tag)
    last_file = "{}/last.md".format(dir)
    if not force and os.path.exists(info_file):
        print("Info file: {} exists skipping image".format(info_file))
        return
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


def main():
    parser = argparse.ArgumentParser(description='Fetch docker repo info. Will fetch the docker image and then generate license info',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("docker_image", help="The docker image name to use (ie: demisto/python). Optional." +
                        "If not specified will scan all images in the demisto organization", nargs="?")
    parser.add_argument("--force", help="Force refetch even if license data already exists", action='store_true')
    parser.add_argument("--no-verify-ssl", help="Don't verify ssl certs for requests (for testing behind corp firewall)", action='store_true')
    args = parser.parse_args()
    global VERIFY_SSL
    VERIFY_SSL = not args.no_verify_ssl
    global USED_PACKAGES
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


if __name__ == "__main__":
    main()
