#!/usr/bin/env bash
#
# The following environment variables are supposed to be set by users
#
# - KALDIALIGN_CONDA_TOKEN
#     If not set, auto upload to anaconda.org is disabled.
#
#     Its value is from https://anaconda.org/kaldialign/settings/access
#      (You need to login as user kaldialign to see its value)
#
set -e
export CONDA_BUILD=1

cur_dir=$(cd $(dirname $BASH_SOURCE) && pwd)
kaldialign_dir=$(cd $cur_dir/.. && pwd)

cd $kaldialign_dir

export KALDIALIGN_ROOT_DIR=$kaldialign_dir
echo "KALDIALIGN_DIR: $KALDIALIGN_ROOT_DIR"

KALDIALIGN_PYTHON_VERSION=$(python -c "import sys; print('.'.join(sys.version.split('.')[:2]))")

# Example value: 3.8
export KALDIALIGN_PYTHON_VERSION

if [ -z $KALDIALIGN_CONDA_TOKEN ]; then
  echo "Auto upload to anaconda.org is disabled since KALDIALIGN_CONDA_TOKEN is not set"
  conda build --no-test --no-anaconda-upload ./scripts/conda/kaldialign
else
  conda build --no-test --token $KALDIALIGN_CONDA_TOKEN ./scripts/conda/kaldialign
fi
