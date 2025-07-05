# Please change according to your directories

# ENVPATH="/Users/tghosh/Desktop/env/"
# CODEDIR="/Users/tghosh/Desktop/LiAISON-ReEDS/code/"
# DATADIR="/Users/tghosh/Desktop/LiAISON-ReEDS/data/"
# Please change according to your scenario
yaml="midcase2024_reedscreation"

SECONDS=0
mkdir $ENVPATH
mkdir $RESDIR
cd $CODEDIR
python __main__.py --datapath=$DATADIR --envpath=$ENVPATH --lca_config_file=$DATADIR/$yaml.yaml
date


duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
