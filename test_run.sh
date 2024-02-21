#!/usr/bin/env bash
PATH_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo $PATH_DIR
CODEDIR=$PATH_DIR"/code"
DATADIR=$PATH_DIR"/data"
yaml="test_run"


SECONDS=0
cd $CODEDIR
python __main__.py --datapath=$DATADIR --lca_config_file=$DATADIR/$yaml.yaml
date


duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
