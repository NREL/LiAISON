
ENVPATH="/Users/tghosh/Desktop/env/env/"
CODEDIR="/Users/tghosh/Library/CloudStorage/OneDrive-NREL/work_NREL/liaison/LiAISON/LiAISON-ReEDS/code/"
DATADIR="/Users/tghosh/Library/CloudStorage/OneDrive-NREL/work_NREL/liaison/LiAISON/LiAISON-ReEDS/data/"
yaml="Mid_Case_NoNascent2050"

SECONDS=0
mkdir $ENVPATH
mkdir $RESDIR
cd $CODEDIR
python __main__.py --datapath=$DATADIR --envpath=$ENVPATH --lca_config_file=$DATADIR/$yaml.yaml
date


duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
