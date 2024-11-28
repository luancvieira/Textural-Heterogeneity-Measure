#!/bin/bash
# Name of the partition
#SBATCH --partition cpu
# Name of the account
#SBATCH -A tcr_ext
# Name of the job
#SBATCH -J run_sample
# Number of nodes
#SBATCH --nodes=1
# Number of tasks per node
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=40
#SBATCH --output=./logs/Result-%x.%j.out
#SBATCH --error=./logs/Result-%x.%j.err
# Runtime of this job
#SBATCH --time=250:00:00
# Array
#SBATCH --array=0

sif="/nethome/drp/ia-drp/singularity/lab2m_ubu_11.10_cuda_11.8.0_devel_tensorflow_2.11.sif"
python="/home/PetrophysicsFeatures/function/run_sample.py"

# Ensure the path to the .nc file is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <path_to_nc> [z_ini] [z_fin]"
    exit 1
fi

NC_PATH=$1  # Get the path to the .nc file from the first argument

# Optional arguments: z_ini and z_fin
Z_INI=${2:-None}  # Use 'None' if not provided
Z_FIN=${3:-None}  # Use 'None' if not provided

# Construct the command with optional z_ini and z_fin parameters
CMD="singularity exec -B /nethome/drp/ia-drp/julio_workspace:/home -B /nethome/drp/ia-drp/data/ncs:/data $sif \
python /home/PetrophysicsFeatures/function/run_sample.py \
-sample_path \"$NC_PATH\" \
-features_folder '/home/PetrophysicsFeatures/features' \
-output_folder '/home/PetrophysicsFeatures/function/output' \
-division_list 2,3,4,5,6,7,8,9,10 \
-contrast_adjustment_options true \
-feature_list mean,std,kurtosis,'variation coefficient' \
-data_rank_path '/home/PetrophysicsFeatures/function/input/entropy_rank_results.csv' \
-data_entropy_path '/home/PetrophysicsFeatures/function/input/entropy_results.csv' \
-z_ini $Z_INI \
-z_fin $Z_FIN"

# Execute the constructed command
eval $CMD