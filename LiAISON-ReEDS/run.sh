# Please change these paths to your PC address for the code to run properply
ENVPATH="/Users/tghosh/Desktop/env"
CODEDIR="/Users/tghosh/Desktop/LiAISON-ReEDS/code/"
DATADIR="/Users/tghosh/Desktop/LiAISON-ReEDS/data"

# Please choose the proper name of the yaml file for scenario creation and LCA
yaml="Mid_Case2024_reedscreation"


SECONDS=0
mkdir $ENVPATH
mkdir $RESDIR
cd $CODEDIR
python __main__.py --datapath=$DATADIR --envpath=$ENVPATH --lca_config_file=$yaml.yaml
date


duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
