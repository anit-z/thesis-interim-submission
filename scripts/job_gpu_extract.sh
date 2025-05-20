#!/bin/bash
#SBATCH --job-name=extract_features          # Job name
#SBATCH --output=log_extract_features.%j.out # Standard output log
#SBATCH --error=log_extract_features.%j.err  # Standard error log
#SBATCH --partition=gpu                      # Use the GPU partition
#SBATCH --gpus-per-node=1                    # Request 1 GPU
#SBATCH --time=06:00:00                      # Maximum runtime (adjust as needed)
#SBATCH --mem=16G                            # Memory allocation (adjust as needed)
#SBATCH --cpus-per-task=4                    # CPU cores per task (adjust for your workload)

# Load necessary modules (adjust based on your environment)
module load Python/3.9.0 CUDA/12.6

# Activate your virtual environment
source /scratch/s6055702/ser_credit_rating/venv39/bin/activate

# Run your Python script
python /scratch/s6055702/ser_credit_rating/scripts/extract_acoustic_features.py