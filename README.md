# README

## Overview

Algorithm for executing a method aimed at obtaining an indicator measure of rock heterogeneity. Initially, the process involves systematically dividing rock sample images into subvolumes and subsequently calculating attributes for each subvolume. Entropy is then used as it is a statistical measure that indicates the uncertainty or amount of information contained in a random variable. The methodology includes partitioning the image into subcubes and calculating statistical features directly from grayscale values, exploring the relationship between result variation and the presence of heterogeneity.

## Requirements

- Use the image provided in the [Dockerfile](./Dockerfile) file.

## Files

- `run_sample.py`: Python script for processing images and performing calculations.
- `parser_utils.py`: Utility functions for shell argument parsing.
- `image_preprocessing_utils.py`: Functions for image preprocessing.
- `feature_calculation_utils.py`: Functions for calculating features within each subvolume.
- `rank_calculation_utils.py`: Functions for entropy calculation and heterogeneity ranking.

## Execution

### Arguments for execution

The `run_sample.py` script has the following arguments:

- **`-sample_path`** (str): Path to the `.nc` file of the sample (required).
- **`-features_folder`** (str): Path to the directory where features will be stored.
- **`-output_folder`** (str): Directory where the results will be saved.
- **`-data_entropy_path`** (str): Path to the CSV file with previously calculated entropy data.
- **`-data_rank_path`** (str): Path to the CSV file with ranking data.
- **`-division_list`** (list): List of divisions (default: `[2,3,4,5,6,7,8,9,10]`).
- **`-contrast_adjustment_options`** (list): List of contrast adjustment options (default: `[True, False]`).
- **`-feature_list`** (list): Features to calculate for each subcube (default: `['mean','std','kurtosis','variation coefficient']`).
- **`-z_ini`** (int or None): Starting index on the Z-axis (optional).
- **`-z_fin`** (int or None): Ending index on the Z-axis (optional).

### Execution by importing the function

```python
from run_sample import heterogeneity_rank

heterogeneity_rank(
    sample_path='/path/to/sample_image.nc',
    features_folder='/path/to/features',
    output_folder='/path/to/output_directory',
    division_list=[2, 3, 4, 5, 6, 7, 8, 9, 10],
    contrast_adjustment_options=[True, False],
    feature_list=['mean', 'std', 'kurtosis', 'variation coefficient'],
    data_rank_path='/path/to/entropy_rank_results.csv',
    data_entropy_path='/path/to/entropy_results.csv',
    z_ini=None,
    z_fin=None
)
