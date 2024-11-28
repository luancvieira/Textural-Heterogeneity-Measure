#!/bin/bash
# Name of the partition
#SBATCH --partition cpu
# Name of the account
#SBATCH -A tcr_ext
# Name of the job
#SBATCH -J schedule_jobs
# Number of nodes
#SBATCH --nodes=1
# Number of tasks per node
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=40
#SBATCH --output=./logs/Result-%x.%j.out
#SBATCH --error=./logs/Result-%x.%j.err
# Runtime of this job
#SBATCH --time=250:00:00

# Check if the CSV file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <path_to_csv>"
    exit 1
fi

CSV_FILE=$1

# Ensure the CSV file exists
if [ ! -f "$CSV_FILE" ]; then
    echo "Error: File '$CSV_FILE' not found."
    exit 1
fi

# Read the CSV and schedule jobs
tail -n +2 "$CSV_FILE" | while IFS=, read -r nc_path; do
    if [ -n "$nc_path" ]; then  # Check if the nc_path is not empty
        echo "Scheduling job for: $nc_path"
        sbatch run_sample.sh "$nc_path"
    fi
done
