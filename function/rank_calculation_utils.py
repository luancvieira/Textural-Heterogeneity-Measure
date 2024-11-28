# rank_calculation_utils.py

import numpy as np
import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KernelDensity

def entropy(values):
    """
    Computes the entropy of a given feature.

    Parameters:
    values (pd.Series): A pandas Series representing feature values to compute entropy.

    Returns:
    float: The calculated entropy value. For discrete features (max, min, median), 
           it uses Shannon entropy on value counts. For continuous features, 
           it estimates entropy using Kernel Density Estimation (KDE) and numerical integration.
    """
    feature_name = values.name
    discrete_features = ['max', 'min', 'median']
    
    if feature_name in discrete_features:
        value_counts = values.value_counts(normalize=True)
        entropy = -np.sum(value_counts * np.log2(value_counts))
    else:
        values = np.array(values).reshape(-1, 1)
        kde = KernelDensity(kernel='gaussian').fit(values)
        range_min = values.min() - np.std(values)
        range_max = values.max() + np.std(values)
        x = np.linspace(range_min, range_max, 1000)
        log_pdf = kde.score_samples(x.reshape(-1, 1))
        pdf = np.exp(log_pdf)
        entropy_integral = -pdf * (log_pdf / np.log(2))
        entropy = np.trapz(entropy_integral, x)

    return entropy

def calculate_sample_entropy(df, adjustment, division, feature, sample):
    """
    Calculates the entropy for a specific feature across a sample.

    Parameters:
    df (pd.DataFrame): DataFrame containing feature data.
    adjustment (str): Type of contrast adjustment ('True' or 'False').
    division (int): Division factor applied to the sample.
    feature (str): Feature name for which entropy is calculated.
    sample (str): Name of the sample being processed.

    Returns:
    list: A list containing a dictionary with the entropy result, including 
          sample name, division, adjustment type, and entropy value.
    """
    entropy_results = []
    entropy_value = entropy(df[feature])
    entropy_results.append({
        'sample': sample,
        'division': division,
        'contrast_adjustment': adjustment,
        feature: entropy_value
    })

    return entropy_results

def process_adjustment_division_feature(combination, features_folder, df_sample_features, sample, scale_features=True):
    """
    Processes a combination of contrast adjustment, division, and feature to compute entropy.

    Parameters:
    combination (tuple): Tuple containing adjustment type, division factor, and feature name.
    features_folder (str): Path to the folder containing all feature grids.
    data_entropy (str): Path to the file with pre-computed entropy data.
    output_folder (str): Path to the folder for output results.
    sample (str): Name of the sample being processed.
    scale_features (bool): Whether to apply feature scaling (default is True).

    Returns:
    list: A list of entropy results for the given combination.
    """
    adjustment, division, feature = combination

    df_sample_features = df_sample_features.loc[
        (df_sample_features['division'] == division) & 
        (df_sample_features['contrast_adjustment'] == adjustment)
    ]
    df_sample_features = df_sample_features.dropna()

    adjustment_folder = 'ajuste_surmas' if adjustment else 'sem_ajuste'
    df_features_all = pd.read_csv(os.path.join(features_folder, f'grid_features_{adjustment_folder}_{division}.csv'))
 
    if scale_features:
        scaler = StandardScaler()
        scaler.fit(df_features_all[feature].values.reshape(-1, 1))
        df_sample_features[feature] = scaler.transform(df_sample_features[feature].values.reshape(-1, 1))

    entropy = calculate_sample_entropy(df_sample_features, adjustment, division, feature, sample)
    return entropy

def generate_entropy_df(results):
    """
    Generates a DataFrame from the list of entropy calculation results.

    Parameters:
    results (list): List of entropy results, each containing dictionaries with 
                    sample name, division, contrast adjustment, and entropy values.

    Returns:
    pd.DataFrame: A DataFrame structured to show entropy results, pivoted by 
                  sample, division, and contrast adjustment.
    """
    flattened_results = [item for sublist in results for item in sublist]
    results_df = pd.DataFrame(flattened_results)
    df_entropy_sample = results_df.pivot_table(index=['sample', 'division', 'contrast_adjustment']).reset_index()
    return df_entropy_sample

def calculate_sample_rank(entropy_dataframe, entropy_sample, feature_list, output_folder):
    """
    Adds a new sample's entropy data to the rank DataFrame and recalculates feature ranks.

    Parameters:
    entropy_dataframe (pd.DataFrame): DataFrame containing existing entropy values and ranks.
    entropy_sample (pd.DataFrame): DataFrame with the entropy values of the new sample.
    feature_list (list of str): List of feature names to be ranked.
    output_folder (str): Path to the folder where the updated rank DataFrame will be saved.

    Returns:
    pd.DataFrame: DataFrame containing the updated ranks for the new sample only.
    """
    features = feature_list
    sample_name = entropy_sample['sample'].unique()[0]

    if sample_name in entropy_dataframe['sample'].unique():
        entropy_dataframe = entropy_dataframe[entropy_dataframe['sample'] != sample_name]
        
    entropy_dataframe = pd.concat([entropy_dataframe, entropy_sample])

    entropy_dataframe = entropy_dataframe[['sample', 'division', 'contrast_adjustment'] + feature_list]

    entropy_rank_dataframe = entropy_dataframe.copy()

    for feature in features:
        entropy_rank_dataframe[f'{feature}_rank'] = (
            entropy_rank_dataframe.groupby(['division', 'contrast_adjustment'])[feature]
            .rank(pct=True) * 100
        )

    columns_to_drop = [
        col for col in entropy_rank_dataframe.columns 
        if col not in ['sample', 'division', 'contrast_adjustment'] + 
           [col for col in entropy_rank_dataframe.columns if 'rank' in col]
    ]
    entropy_rank_dataframe.drop(columns=columns_to_drop, inplace=True)

    entropy_rank_sample_df = entropy_rank_dataframe[entropy_rank_dataframe['sample'] == sample_name]
    return entropy_rank_sample_df
