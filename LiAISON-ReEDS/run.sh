
ENVPATH="/Users/tghosh/Desktop/Dynamic-LCA-with-LiAISON/env"
CODEDIR="/Users/tghosh/Desktop/hipster/code/"
DATADIR="/Users/tghosh/Desktop/hipster/data"
yaml="midcase2020_small"

SECONDS=0
mkdir $ENVPATH
mkdir $RESDIR
cd $CODEDIR
python __main__.py --datapath=$DATADIR --envpath=$ENVPATH --lca_config_file=$DATADIR/$yaml.yaml
date


duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
