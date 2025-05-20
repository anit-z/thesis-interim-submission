#!/bin/bash
#SBATCH --job-name=extract_llds                 # Job name
#SBATCH --output=log_extract_llds.%j.out        # Standard output log
#SBATCH --error=log_extract_llds.%j.err         # Standard error log
#SBATCH --partition=gpu                         # Partition (can be changed to 'short' or 'cpu' if GPU not needed)
#SBATCH --gpus-per-node=1                       # GPU requested (can be removed if not using GPU)
#SBATCH --time=06:00:00                         # Max runtime
#SBATCH --mem=16G                               # Memory allocation
#SBATCH --cpus-per-task=4                       # CPU cores per task

# Load modules (adjust based on your cluster's environment)
module load Python/3.9.0 CUDA/12.6

# Activate your conda or virtual environment
source /scratch/s6055702/ser_credit_rating/venv39/bin/activate

# Change to project directory
cd /scratch/s6055702/ser_credit_rating

# Run the feature extraction shell script
bash scripts/extract_llds.sh