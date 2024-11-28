# run_sample.py

import os
import pandas as pd
from multiprocessing import Pool, Manager, cpu_count
from functools import partial
import itertools
import argparse
import time
from datetime import datetime
import subprocess

from views_plot import plot_views_from_sample
from parser_utils import str2bool, list_of_bools, list_of_ints, list_of_strings, int_or_none
from image_preprocessing_utils import (
    load_and_preprocess_image, generate_expanded_dataset, get_rectangle_bounds, get_info, get_contrast_adjustments_values, check_image_dtype
)
from feature_calculation_utils import generate_pool_dict, compute_image_statistics, export_features
from rank_calculation_utils import (
    entropy, calculate_sample_entropy, process_adjustment_division_feature, 
    generate_entropy_df, calculate_sample_rank
)

def heterogeneity_rank(sample_path, features_folder, output_folder, data_rank_path, data_entropy_path, division_list, contrast_adjustment_options, feature_list, z_ini, z_fin):
    start = time.time()

    # check if specified path is a 16bit image, else stops execution
    check_image_dtype(sample_path)
        
    # load entropy and rank data for previously calculated samples
    data_entropy = pd.read_csv(data_entropy_path)

    # get sample name from sample_path
    sample_name = sample_path.split('/')[-1].split('.')[0]

    print(f'Sample: {sample_name}', flush = True)

    # process image, calculate features, calculate entropy and recalculate rank for new samples
    # get cropped image bounds
    cuts_start = time.time()
    print('Image cuts definition began.', flush = True)
    bounds_result = get_rectangle_bounds(sample_path, z_ini, z_fin)
    bounds_df = pd.DataFrame([bounds_result], columns=['dataset', 'z_ini', 'z_fin', 'x_ini', 'x_fin', 'y_ini', 'y_fin'])
    cuts_end = time.time()
    print(f'Image cuts definition ended. Time elapsed (seconds): {cuts_end - cuts_start}', flush = True)

    # get voidmean and rockmedian
    voidmean_rockmedian_start = time.time()
    print('Voidmean and rockmedian calculation began.', flush = True)
    info = get_info(sample_path, bounds_result[1], bounds_result[2])
    contrast_results = [get_contrast_adjustments_values(i) for i in info]
    contrast_df = pd.DataFrame(contrast_results, columns=['dataset', 'voidmean', 'rockmedian']).groupby(by=['dataset']).median().reset_index()
    voidmean_rockmedian_end = time.time()
    print(f'Voidmean and rockmedian calculation ended. Time elapsed (seconds): {voidmean_rockmedian_end - voidmean_rockmedian_start}', flush = True)

    # store sample dataframe (memory) with info needed for rank calculation
    dfdataset = pd.merge(contrast_df, bounds_df, on='dataset')
    print('Sample dataset created.', flush = True)
    
    # Define the output folder path with sample name and timestamp
    timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
    output_folder = os.path.join(output_folder, f'{sample_name}_{timestamp}')
    os.makedirs(output_folder, exist_ok=True)
    
    #Plot views
    plot_start = time.time()
    print('Started plotting views', flush = True)
    plot_views_from_sample(dfdataset, output_folder)
    plot_end = time.time()
    print(f'Plotting views ended. Time elapsed (seconds): {plot_end - plot_start}', flush=True)
    
    # begin feature calculation
    feature_start = time.time()
    print('Feature calculation started.', flush=True)
    
    # Consider different options of contrast adjustment
    dfcrops_expanded = generate_expanded_dataset(dfdataset, contrast_adjustment_options)
    sample_info_path = os.path.join(output_folder,f'info_{sample_name}.csv')
    dfcrops_expanded.to_csv(sample_info_path, index = False)
    print(f'Sample info saved to {sample_info_path}')
                                
    if dfcrops_expanded.shape[0] == 1:
        row = dfcrops_expanded.iloc[0]
        sample_images = [load_and_preprocess_image((0, row))]
    else:
        with Pool(2) as pool:
            sample_images = pool.map(
                partial(load_and_preprocess_image), dfcrops_expanded.iterrows()
            )
        
    # create dictionary with images and different grid choices
    pool_dict = generate_pool_dict(sample_images, division_list)

    prepared_dict_items = [((key[0], key[1], key[2]), value) for key, value in pool_dict.items()]
    
    with Pool(min(len(pool_dict), cpu_count())) as pool:
        features_results = pool.map(
            partial(compute_image_statistics, feature_list=feature_list),
            prepared_dict_items
    )
    feature_end = time.time()
    print(f'Feature calculation ended. Time elapsed (seconds): {feature_end - feature_start}', flush=True)

    # store sample features for each subcube
    df_sample_features = export_features(features_results, sample_name, feature_list)
    features_output_path = os.path.join(output_folder, f'features_{sample_name}.csv')
    df_sample_features.to_csv(features_output_path, index=False)
    print(f'Features for sample {sample_name} saved to {features_output_path}.', flush = True)

    # begin entropy calculation
    entropy_start = time.time()
    print('Entropy calculation began.', flush = True)

    # create list with chosen options of contrast adjustment, grid values, and features
    combinations_entropy = list(itertools.product(contrast_adjustment_options, division_list, feature_list))

    # calculate sample entropy
    pool_size = min(len(combinations_entropy), cpu_count())
    with Pool(pool_size) as pool:
        entropy_results = pool.map(partial(process_adjustment_division_feature, features_folder = features_folder, df_sample_features = df_sample_features, sample = sample_name), combinations_entropy)
    entropy_end = time.time()
    print(f'Entropy calculation ended. Time elapsed (seconds): {entropy_end - entropy_start}.', flush = True)
    
    # store sample entropy in a dataframe (memory)
    entropy_sample_df = generate_entropy_df(entropy_results)
    entropy_output_path = os.path.join(output_folder, f'entropy_{sample_name}.csv')
    entropy_sample_df.to_csv(entropy_output_path, index = False)
    print(f'Entropy file saved to {entropy_output_path}', flush = True)

    rank_start = time.time()
    print(f'Rank calculation for sample {sample_name} began.', flush = True)
    
    # recalculate rank considering new sample       
    entropy_sample_rank_df = calculate_sample_rank(data_entropy, entropy_sample_df, feature_list, output_folder)
    rank_end = time.time()
    print(f'Rank calculation for sample {sample_name} ended. Time elapsed: {rank_end - rank_start}', flush = True)

    # save sample rank
    rank_output_path = os.path.join(output_folder, f'rank_{sample_name}.csv')
    entropy_sample_rank_df.to_csv(rank_output_path, index = False)
    print(f'Rank file saved to {rank_output_path}', flush = True)
    
    end = time.time()
    print(f'Total time (seconds): {end - start}', flush = True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-sample_path", type=str, required=True)
    parser.add_argument("-features_folder", type=str)
    parser.add_argument("-output_folder", type=str)
    parser.add_argument("-data_entropy_path", type=str)
    parser.add_argument("-data_rank_path", type=str)
    parser.add_argument("-division_list", type=list_of_ints, default='2,3,4,5,6,7,8,9,10')
    parser.add_argument("-contrast_adjustment_options", type=list_of_bools, default='True, False')
    parser.add_argument("-feature_list", type=list_of_strings, default='mean,std,min,max,skewness,kurtosis,"variation coefficient",median')
    parser.add_argument("-z_ini", type=int_or_none, default= None)
    parser.add_argument("-z_fin", type=int_or_none, default= None)

    args = parser.parse_args()
    heterogeneity_rank(sample_path = args.sample_path,
                       features_folder = args.features_folder,
                       output_folder = args.output_folder,
                       data_entropy_path = args.data_entropy_path,
                       data_rank_path = args.data_rank_path,
                       division_list = args.division_list,
                       contrast_adjustment_options = args.contrast_adjustment_options,
                       feature_list = args.feature_list,
                       z_ini = args.z_ini,
                       z_fin = args.z_fin)