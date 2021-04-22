#!/usr/bin/env bash

# exit on errors
set -e

if [ -z "$CI" ]; then
    echo "This script is meant to be run in CI environment. If you really want to run it set env variable CI=true"
    exit 1
fi

if [[ ! $(which pyenv) ]] && [[ -n "${CIRCLECI}" ]]; then 
    echo "pyenv not found. setting up necessary env for pyenv on circle ci";\
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
fi

git config --global user.email "dc-builder@users.noreply.github.com"
git config --global user.name "dc-builder"


echo ""
echo "====== `date`: Starting docker repository update ====="
echo ""

pipenv install

pipenv run ./update-docker-repo-info.py

if [[ "$(uname)" == Linux ]]; then
    CP_PARENTS="--parents"
else
    CP_PARENTS=""
fi

if [[ $(git status --short) ]]; then
    echo "found modified/new files to commit"
    git status --short
    mkdir -p artifacts
    # use sed 's:/*$::' to trim trailing slashes from dirs
    git status --short | awk '{print $2}' | sed 's:/*$::' | xargs -I {} cp -rf $CP_PARENTS {} artifacts/. || echo "cp failed for some reason. continue..."    
    if [[ "$CIRCLE_BRANCH" == "master" ]]; then
        echo "commit generated data to: $CIRCLE_BRANCH"
        git add . 
        git commit -m "`date`: auto repo info update [skip ci]"
        git push
    else
        echo "Skipping commit as we are NOT on master. Check the generated artifacts of the build to verify."
    fi
else
    echo "No new files to commit!"
fi

echo ""
echo "====== `date`: Done docker repository update ====="
echo ""
