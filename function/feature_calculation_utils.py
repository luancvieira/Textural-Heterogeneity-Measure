## feature_calculation_utils.py

import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis, variation
from multiprocessing import Manager
import os

def generate_pool_dict(sample_images, division_list):
    """
    Generates a shared dictionary for multiprocessing, containing images grouped 
    by sample name, contrast adjustment, and division value.

    Parameters:
    sample_images (list of tuples): A list where each element is a tuple containing 
                                    (sample name, image, contrast adjustment).
    division_list (list of int): List of division values used to segment the images.

    Returns:
    Manager.dict: A multiprocessing-safe dictionary where keys are tuples 
                  (sample, contrast_adjustment, division), and values are the 
                  corresponding images.
    """
    image_dict = {}
    for division in division_list:
        for sample, im, contrast_adjustment in sample_images:
            key = (sample, contrast_adjustment, division)
            image_dict[key] = im
        
    manager = Manager()
    pool_dict = manager.dict(image_dict)
    return pool_dict

def compute_image_statistics(dictionary_items, feature_list):
    """
    Computes statistical features for 3D image subcubes based on the given feature list.

    Parameters:
    dictionary_items (tuple): A tuple containing ((sample, contrast_adjustment, division), image), 
                              where the image is a 3D numpy array.
    feature_list (list of str): List of feature names to compute for each subcube, such as 
                                'mean', 'std', 'min', 'max', 'skewness', 'kurtosis', etc.

    Returns:
    list: A list of computed features for all subcubes in the form of nested lists. 
          Each inner list contains [sample, contrast_adjustment, division, subcube_index, features...].
    """
    (sample, contrast_adjustment, division), im = dictionary_items
    
    z, x, y = im.shape
    segment_size = min(x, y) // division
    divisions_z = z // segment_size
    statistics = []

    for i in range(divisions_z):
        for j in range(division):
            for k in range(division):
                part = im[i * segment_size:(i + 1) * segment_size, 
                          j * segment_size:(j + 1) * segment_size, 
                          k * segment_size:(k + 1) * segment_size].flatten()
                subcube_index = i * (division ** 2) + j * division + k
                                
                stats = [subcube_index]

                feature_operations = {
                    'mean': lambda part: np.mean(part),
                    'std': lambda part: np.std(part),
                    'min': lambda part: np.min(part),
                    'max': lambda part: np.max(part),
                    'skewness': lambda part: skew(part),
                    'kurtosis': lambda part: kurtosis(part),
                    'variation coefficient': lambda part: variation(part),
                    'median': lambda part: np.median(part)
                }

                for feature in feature_list:
                    if feature in feature_operations:
                        stats.append(feature_operations[feature](part))
                
                statistics.append(stats)
                
    rows = []
    for stats in statistics:
        rows.append([sample, contrast_adjustment, division] + stats)
        
    return rows

def export_features(results, sample, feature_list):
    """
    Exports the computed statistical features to a CSV file and returns the DataFrame.

    Parameters:
    results (list): A nested list containing computed feature values for each subcube.
                    Each inner list should have the structure:
                    [sample, contrast_adjustment, division, subcube_index, features...].
    sample (str): Name of the sample for which features were computed.
    feature_list (list of str): List of feature names to be used as column headers in the CSV file.

    Returns:
    pd.DataFrame: A DataFrame containing the computed features, with columns:
                  ['sample', 'contrast_adjustment', 'division', 'subcube'] + feature_list.
    """
    # Flatten the nested list of results
    flattened_results = [item for sublist in results for item in sublist]

    # Create a DataFrame from the flattened results
    df_sample = pd.DataFrame(
        flattened_results, 
        columns=['sample', 'contrast_adjustment', 'division', 'subcube'] + feature_list
    )
    # Return the DataFrame
    return df_sample

