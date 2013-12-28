#!/bin/bash

author="Brian Wiborg"
mail="baccenfutter@c-base.org"
pn="net_conf"
description="Commandline-based network manager"

p="$(echo ${pn} | tr '[:upper:]' '[:lower:]' | tr '-' '_')"
v="$1"
pv="${p}-${v}"
workdir=$(mktemp -d --tmpdir=/tmp ${p}-build.XXXXXX)
projectdir="$workdir/${p}"
sourcedir="$projectdir/${p}"

if grep / <(echo $0) &>/dev/null; then
echo 'Please run this script from its directory.'
fi

if [[ -z $v ]]; then
echo "Please provide version tag, e.g. '$0 0.1.0'"
    exit 1
fi

if not grep ${v} "CHANGELOG.txt" &>/dev/null; then
echo 'You forgot to update the changelog!'
    exit 1
fi

read -n 1 -p "Can haz package: ${pv} [y|N]: " answer
echo
if [[ ! "$answer" == y ]]; then
echo "Bailing out by user request."
    exit 0
fi

cleanup() {
    rm -rf "$workdir"
}

# bootstrap working directory
trap cleanup QUIT
echo $workdir

mkdir -p "$sourcedir"
mkdir -p "$sourcedir/bin"

# copy source to working directory
cp ../*.py "$sourcedir"
cp ../netconf.sh "$projectdir/bin/"

# copy meta-files to working directory
cp *.txt "$projectdir"
cp *.in "$projectdir"
cp ../README.md "$projectdir/README.txt"

# create setup.py
setup_stanza="from setuptools import setup

setup(
name='${pn}',
version='${v}',
author='${author}',
author_email='${mail}',
packages=['${p}'],
scripts=[],
url='http://pypi.python.org/pypi/${pn}/',
license='LICENSE.txt',
description='${description}',
long_description=open('README.txt').read(),
install_requires=[],
)
"

echo "$setup_stanza" > "$projectdir/setup.py"

# run setup.py
cd "$projectdir"
python setup.py sdist

# install to local environment
read -n 1 -p "Can haz install: ${pv} [y|N]: " answer
echo
if [[ "$answer" == y ]]; then
    python setup.py develop
fi

# register and upload
read -n 1 -p "Can haz upload: ${pv} [y|N]: " answer
echo
if [[ "$answer" == y ]]; then
    python setup.py sdist upload
fi
