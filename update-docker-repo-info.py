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
import codecs
import yaml
import traceback
from slack_notifier import slack_notifier


assert sys.version_info >= (3, 9), "Script compatible with python 3.9 and higher only"

VERIFY_SSL = True
OLD_TAG_THRESHOLD_IN_MONTHS = 6
DOCKERFILES_DIR = os.path.abspath(os.getenv('DOCKERFILES_DIR', '.dockerfiles'))
CONTENT_DIR = os.path.abspath(os.getenv('CONTENT_DIR', '.content'))
DOCKER_IMAGES_METADATA = "docker_images_metadata.json"
DOCKER_IMAGE_REGEX_PATTERN = r'^demisto/([^\s:]+):(\d+(\.\d+)*)$'
DOCKERHUB_ACCESS_TOKEN = ''
DOCKERHUB_USER = ''
DOCKERHUB_PASSWORD = ''
CONTENT_DOCKER_IMAGES = {}
ADDED_IMAGES = []
REMOVED_IMAGES = []
FAILED_INSPECT_IMAGES = []


try:
    with codecs.open(DOCKER_IMAGES_METADATA, encoding="utf-8-sig") as f:
        DOCKER_IMAGES_METADATA_FILE_CONTENT = json.load(f)
except json.JSONDecodeError:
    print(f'Could not load {DOCKER_IMAGES_METADATA_FILE_CONTENT}')
    DOCKER_IMAGES_METADATA_FILE_CONTENT = {}


def http_get(url, **kwargs):
    """wrapper function around requests.get which set verify to what we got in the args

    Arguments:
        url {string} -- url to get

    Returns:
        requests.Response -- response from reqeusts.get§
    """
    return requests.get(url, verify=VERIFY_SSL, **kwargs)

def create_access_token():
    """this method creates access token for dockerhub API requests

    Returns:
        The created access token
    """
    global DOCKERHUB_USER
    global DOCKERHUB_PASSWORD
    global DOCKERHUB_ACCESS_TOKEN

    payload = json.dumps({
        "identifier": DOCKERHUB_USER,
        "secret": DOCKERHUB_PASSWORD
    })
    res =  requests.post('https://registry.hub.docker.com/v2/auth/token', verify=VERIFY_SSL,data=payload)
    if res.status_code != 200:
        raise Exception(f'Failed to create access token, status code: {res.status_code}, response: {res.text}')
        
    DOCKERHUB_ACCESS_TOKEN = res.json().get('access_token')
    print('access token for dockerhub api created')


def http_dockerhub_get(url, **kwargs):
    """this method allow to make get requests to dockerhub api with access token

    Arguments:
        url {string} -- url to get

    Returns:
        requests.Response -- response from reqeusts.get§
    """
    global DOCKERHUB_ACCESS_TOKEN
    
    if not DOCKERHUB_ACCESS_TOKEN:
        create_access_token()
    
    res =  requests.get(url, verify=VERIFY_SSL,headers= {'Authorization': f'Bearer {DOCKERHUB_ACCESS_TOKEN}'}, **kwargs)
    if res.status_code == 401:
        create_access_token()
        res =  requests.get(url, verify=VERIFY_SSL,headers= {'Authorization': f'Bearer {DOCKERHUB_ACCESS_TOKEN}'}, **kwargs)
    if res.status_code == 429:
        print(f'Client Error: Too Many Requests for url {url}, response headers: {str(res.headers)}, sleeping one minute')
        time.sleep(60)
        res =  requests.get(url, verify=VERIFY_SSL,headers= {'Authorization': f'Bearer {DOCKERHUB_ACCESS_TOKEN}'}, **kwargs)
    return res        

def get_docker_image_size(docker_image):
    """Get the size of the image form docker hub
    Arguments:
        docker_image {string} -- the full name of the image
    """
    size = "failed querying size"
    for i in (1, 2, 3):
        try:
            name, tag = docker_image.split(':')
            res = http_dockerhub_get('https://hub.docker.com/v2/repositories/{}/tags/{}/'.format(name, tag))
            res.raise_for_status()
            size_bytes = res.json()['images'][0]['size']
            size = '{0:.2f} MB'.format(float(size_bytes)/1024/1024)
        except Exception as ex:
            print("[{}] failed getting image size for image: {}. Err: {}".format(i, docker_image, ex))
            if i != 3:
                print("Sleeping 5 seconds and trying again...")
                time.sleep(5)
    return size


def get_latest_and_old_tags(image_name):
    old_tags = []
    last_tag = None
    last_date = None
    url = "https://registry.hub.docker.com/v2/repositories/{}/tags/?page_size=25".format(image_name)
    
    current_date = datetime.datetime.now()
    old_tags_threshold = current_date - datetime.timedelta(days=OLD_TAG_THRESHOLD_IN_MONTHS*30)
        
    while True:
        print("Querying docker hub url: {}".format(url))
        res = http_dockerhub_get(url)
        res.raise_for_status()
        obj = res.json()
        for result in obj['results']:
            name = result['name']
            if len(name) >= 20 and all(c in string.hexdigits for c in name):  # skip git sha revisions
                continue
            date = datetime.datetime.strptime(result['last_updated'], "%Y-%m-%dT%H:%M:%S.%fZ")
            
            if date < old_tags_threshold:
                old_tags.append(result['name'])
            
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
    
    if last_tag in old_tags:
        old_tags.remove(last_tag)        
    
    return last_tag, old_tags


def get_os_release(image_name):
    res = subprocess.run(["docker", "run", "--rm", image_name, "cat", "/etc/os-release"], text=True, capture_output=True)
    if res.returncode != 0:
        print("failed getting os release for: {} stderr: {}".format(image_name, res.stderr))
        return []
    return res.stdout.splitlines()


def get_python_version(docker_info: str) -> str:
    return python_version.group(1) if (
        python_version := re.search(r'PYTHON_VERSION=(\d+\.\d+\.\d+)', docker_info)
    ) else ''


def add_python_version_to_dockerfiles_metadata(image_name: str, docker_info: str):
    try:
        if match := re.match(DOCKER_IMAGE_REGEX_PATTERN, image_name):
            docker_name, tag = match.group(1), match.group(2)
            docker_images_metadata_content = DOCKER_IMAGES_METADATA_FILE_CONTENT.get("docker_images") or {}

            if python_version := get_python_version(docker_info):
                print(f'Found python version {python_version} for {image_name=}')
                if not docker_images_metadata_content.get(docker_name):
                    docker_images_metadata_content[docker_name] = {}
                tags = docker_images_metadata_content.get(docker_name)
                if not tags.get(tag):
                    tags[tag] = {"python_version": python_version}
            else:
                print(f'Could not find python version for {image_name=}')
        else:
            print(f"Could not extract docker name and tag from {image_name}")

    except Exception as error:
        print(f'Could not add python version to {image_name} because of error: {error}')


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
- Labels:{{{{ range $key, $value := .Config.Labels }}}}{{{{ "\\n" }}}}  - `{{{{ $key }}}}:{{{{ $value }}}}`{{{{ end }}}}
'''
    docker_info = subprocess.check_output(["docker", "inspect", "-f", inspect_format, image_name], text=True)

    out_file.write(docker_info)

    # get python version and add it to the docker images metadata file
    if DOCKER_IMAGES_METADATA_FILE_CONTENT:
        add_python_version_to_dockerfiles_metadata(image_name, docker_info)
    else:
        print(f'{DOCKER_IMAGES_METADATA_FILE_CONTENT=} is empty, to avoid overriding the file, python version will not be added')

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


def inspect_image_tag(image_name, image_tag, force=False, is_last_tag=False):
    full_name = "{}:{}".format(image_name, image_tag)
    dir = "{}/{}".format(sys.path[0], image_name)
    if not os.path.exists(dir):
        os.makedirs(dir)
    info_file = "{}/{}.md".format(dir, image_tag)

    if not force and os.path.exists(info_file):
        print("Info file: {} exists skipping image".format(info_file))
        return
    print("Downloading docker image: {}...".format(full_name))
    subprocess.call(["docker", "pull", full_name])
    temp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
    print("Using temp file: " + temp_file.name)
    try:
        temp_file.write("# `{}:{}`\n".format(image_name, image_tag))
        inspect_image(full_name, temp_file)
        docker_trust(full_name, temp_file)
        temp_file.write("## `Python Packages`\n\n")
        generate_pkg_data(full_name, temp_file)
        temp_file.write("\n## `OS Packages`\n\n")
        list_os_packages(full_name, temp_file)
        temp_file.close()
        shutil.move(temp_file.name, info_file)
        ADDED_IMAGES.append(full_name)
        if is_last_tag:
            last_file = "{}/last.md".format(dir)
            shutil.copy(info_file, last_file)
    except Exception as e:
        print("Error: {}".format(e))
        if isinstance(e, subprocess.CalledProcessError):
            print("Stderr: {}".format(e.stderr))
        os.remove(temp_file.name)
        raise
    finally:
        print(f"Removing Docker image from local runner: {full_name}")
        subprocess.call(["docker", "rmi", full_name])


def process_image(image_name: str, force: bool):
    global REMOVED_IMAGES
    global ADDED_IMAGES
    global FAILED_INSPECT_IMAGES
    global CONTENT_DOCKER_IMAGES

    print("=================\nProcessing: " + image_name)
    master_dir = f'docker/{image_name.split("/")[1]}'
    master_date = subprocess.check_output(['git', '--no-pager', 'log', '-1', '--format=%ct', 'origin/master', '--', master_dir], text=True, cwd=DOCKERFILES_DIR).strip()
    if not master_date:
        print(f"Skipping image: {image_name} as it is not in our master repository")
        return

    print(f"Checking last tag and old tags for: {image_name}")
    try:
        last_tag, old_tags = get_latest_and_old_tags(image_name)
    except Exception as e:
            print(f'Failed to get image tags for {image_name} error: {e}')
            print(traceback.format_exc())
            FAILED_INSPECT_IMAGES.append(image_name)
            return
    
    # get all the image tags for this image from docker_images_metadata.json
    docker_images_metadata = DOCKER_IMAGES_METADATA_FILE_CONTENT.get("docker_images", {}).get(image_name.replace('demisto/', ''))
    
    # get the image tags we use in content repo that not exists in docker_images_metadata.json
    tags_need_to_add = []
    
    if docker_images_metadata:
        if last_tag not in docker_images_metadata.keys():
            tags_need_to_add.append(last_tag)
    else:
        tags_need_to_add.append(last_tag)
        

    
    content_images = CONTENT_DOCKER_IMAGES.get(image_name, [])
    for tag in content_images:
        if docker_images_metadata:
            if tag not in docker_images_metadata.keys():
                tags_need_to_add.append(tag)
        else:
            tags_need_to_add.append(tag)

    # remove old dockers from docker_images_metadata.json
    if docker_images_metadata:
        for tag in old_tags:
            if tag in docker_images_metadata.keys() and tag not in tags_need_to_add and tag not in content_images:
                del docker_images_metadata[tag]
                tag_md_file = os.path.join(sys.path[0], image_name, f'{tag}.md')
                if os.path.exists(tag_md_file):
                    os.remove(tag_md_file)
                REMOVED_IMAGES.append(f"{image_name}:{tag}")


    # inspect image tags and create the info files
    for tag_to_add in tags_need_to_add:
        try:
            inspect_image_tag(image_name,tag_to_add, force, last_tag == tag_to_add)
        except Exception as e:
            print(f'Failed to inspect {f"{image_name}:{tag}"} error: {e}')
            print(traceback.format_exc())
            FAILED_INSPECT_IMAGES.append(f"{image_name}:{tag}")


def process_org(org_name, force):
    url = "https://registry.hub.docker.com/v2/repositories/{}/?page_size=100".format(org_name)
    with open("{}/images_ignore.txt".format(sys.path[0])) as f:
        ignore_list = list(filter(lambda x: not x.startswith('#'), f.read().splitlines()))
        print("ignore list: {}".format(ignore_list))
    while True:
        print("Querying docker hub url: {}".format(url))
        res = http_dockerhub_get(url)
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


def save_to_docker_files_metadata_json_file():
    if not DOCKER_IMAGES_METADATA_FILE_CONTENT:
        print(
            f'{DOCKER_IMAGES_METADATA_FILE_CONTENT=} is empty, to avoid overriding the file, python version will not be added'
        )
        return
    # Remove empty docker image entries (where the value is an empty dict)
    docker_images: dict = DOCKER_IMAGES_METADATA_FILE_CONTENT["docker_images"]
    docker_images = {k: v for k, v in docker_images.items() if v}
    DOCKER_IMAGES_METADATA_FILE_CONTENT["docker_images"] = docker_images

    with open("docker_images_metadata.json", "w") as fp:
        fp.write(json.dumps(DOCKER_IMAGES_METADATA_FILE_CONTENT, indent=4, sort_keys=True))
    print("Successfully saved to 'docker_images_metadata.json'.")


def checkout_dockerfiles_repo():
    if os.path.exists(DOCKERFILES_DIR):
        print(f'dockerfiles dir {DOCKERFILES_DIR} exists. Skipping checkout!')
        return
    print(f'checking out dockerfiles project to: {DOCKERFILES_DIR}'
          ' (Note: for local testing you can set the  env var DOCKERFILES_DIR to your dockerfiles repo to avoid this checkout) ....')
    os.mkdir(DOCKERFILES_DIR)
    subprocess.check_call(['git', 'clone', 'https://github.com/demisto/dockerfiles', DOCKERFILES_DIR])


def checkout_content_repo():
    if os.path.exists(CONTENT_DIR):
        print(f'content dir {CONTENT_DIR} exists. Skipping checkout!')
        return
    print(f'checking out content project to: {CONTENT_DIR}'
          ' (Note: for local testing you can set the  env var CONTENT_DIR to your content repo to avoid this checkout) ....')
    os.mkdir(CONTENT_DIR)
    subprocess.check_call(['git', 'clone', 'https://github.com/demisto/content', CONTENT_DIR])


def get_yaml_files_in_directory(directory):
    """Recursively fetches all .yml files in content repo"""
    yml_files = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if 'playbook' not in d.lower()
                   and 'rules' not in d.lower() and 'template' not in d.lower()]
        for file in files:
            if file.endswith('.yml') or file.endswith('.yaml'):
                yml_files.append(os.path.join(root, file))

    return yml_files

def read_dockers_from_all_yml_files(directory):
    """Get the docker images from yml files"""
    yml_files = get_yaml_files_in_directory(directory)
    all_docker_image = {}
    for file_path in yml_files:
        try:
            with open(file_path, 'r') as file:
                data = yaml.safe_load(file)  # Load the YAML file

                if data.get('type') != 'javascript':
                    docker_images = set()
                    script_value = data.get('script', {})
                    
                    # get the alt_dockerimages value
                    if data.get('alt_dockerimages'):
                        docker_images.update(data.get('alt_dockerimages'))
                    elif script_value and isinstance(script_value,dict) and script_value.get('alt_dockerimages'):
                        docker_images.update(data.get('script').get('alt_dockerimages'))

                    # get the docker image
                    if data.get('dockerimage'):
                        docker_images.add(data.get('dockerimage'))
                    elif script_value and isinstance(script_value,dict) and script_value.get('dockerimage'):
                        docker_images.add(data.get('script').get('dockerimage'))

                    # update all_docker_image dict
                    for docker_image in docker_images:
                        image_name, tag = docker_image.split(':')
                        
                        # add the tag to the dictionary, ensuring the list of tags is distinct
                        if image_name not in all_docker_image:
                            all_docker_image[image_name] = {tag}
                        else:
                            all_docker_image[image_name].add(tag)  # add tag if it's not already present
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    # Convert sets to lists (for the final output)
    for key in all_docker_image:
        all_docker_image[key] = list(all_docker_image[key])
            
    return all_docker_image


def main():
    parser = argparse.ArgumentParser(description='Fetch docker repo info. Will fetch the docker image and then generate license info',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--docker-image", help="The docker image name to use (ie: demisto/python). Optional." +
                        "If not specified will scan all images in the demisto organization.", nargs="?")
    parser.add_argument("--force", help="Force refetch even if license data already exists", action='store_true')
    parser.add_argument("--no-verify-ssl", help="Don't verify ssl certs for requests (for testing behind corp firewall)", action='store_true')
    parser.add_argument("--slack-token", help="The token for slack.")
    parser.add_argument("--slack-channel", help="The slack channel in which to send the notification.")
    parser.add_argument("--dockerhub-user", help="The dockerhub username to use.")
    parser.add_argument("--dockerhub-password", help="The dockerhub password to use.")
    args = parser.parse_args()
    global VERIFY_SSL
    global DOCKERHUB_USER
    global DOCKERHUB_PASSWORD
    VERIFY_SSL = not args.no_verify_ssl
    DOCKERHUB_USER = args.dockerhub_user
    DOCKERHUB_PASSWORD = args.dockerhub_password
    if not VERIFY_SSL:
        requests.packages.urllib3.disable_warnings()
    global USED_PACKAGES
    checkout_dockerfiles_repo()

    # set CONTENT_DOCKER_IMAGES value with all the docker images we use in content repo
    checkout_content_repo()
    all_content_dockers = read_dockers_from_all_yml_files(f'{CONTENT_DIR}/Packs')
    global CONTENT_DOCKER_IMAGES
    CONTENT_DOCKER_IMAGES = all_content_dockers
    
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
    save_to_docker_files_metadata_json_file()
    
    # send Slack notification
    global REMOVED_IMAGES
    global ADDED_IMAGES
    global FAILED_INSPECT_IMAGES
    slack_notifier(args.slack_token, args.slack_channel, REMOVED_IMAGES, ADDED_IMAGES, FAILED_INSPECT_IMAGES)


if __name__ == "__main__":
    main()
