# image_preprocessing_utils.py

import os
import pandas as pd
import numpy as np
import xarray as xr
import cv2
from shapely.geometry import box
import sys

def check_image_dtype(filepath):
    """
    Checks if the given image file is of dtype uint16.
    
    Parameters:
    filepath (str): Path to the image file.
    
    Returns:
    None
    """
    try:
        with xr.open_dataset(filepath) as db:
            im = db['microtom']
            if im.dtype not in [np.uint16, 'uint16']:
                print('Chosen file is not a 16-bit image.', flush=True)
                sys.exit(1)
    except (IOError, KeyError) as e:
        print(f'Error opening file: {e}', flush=True)
        sys.exit(1)
        
def load_and_preprocess_image(data):
    """
    Loads and preprocesses a microtom image based on given parameters.
    
    Parameters:
    data (tuple): Tuple containing index and row of DataFrame with sample and adjustment info.
    
    Returns:
    tuple: Contains sample name, processed image array, and contrast_adjustment flag.
    """
    ix, row = data
    sample = row['dataset'].split('/')[-1][:-3]
    nc_path = row['dataset']
    contrast_adjustment = row['contrast_adjustment']

    if os.path.exists(nc_path):
        with xr.open_dataset(nc_path) as db:
            im = db['microtom'][int(row['z_ini']):int(row['z_fin']), int(row['x_ini']):int(row['x_fin']), int(row['y_ini']):int(row['y_fin'])]
            im = np.array(im)

            if contrast_adjustment:
                im = im - float(row['voidmean'])
                im = im * 32768 / float(row['rockmedian'])
                im = np.clip(im, 0, 65535)

        return sample, im, contrast_adjustment

def generate_expanded_dataset(dfdataset, contrast_adjustment_options):
    """
    Generates an expanded dataset by applying different contrast adjustments.
    
    Parameters:
    dfdataset (DataFrame): The original dataset.
    contrast_adjustment_options (list of bool): List of contrast adjustment flags.
    
    Returns:
    DataFrame: Expanded dataset with additional contrast adjustment values.
    """
    dfcrops_list = []
    for contrast_adjustment in contrast_adjustment_options:
        temp_df = dfdataset.copy()
        temp_df['contrast_adjustment'] = contrast_adjustment
        dfcrops_list.append(temp_df)

    dfcrops_expanded = pd.concat(dfcrops_list, ignore_index=True)
    
    return dfcrops_expanded

def get_rectangle_bounds(filename, z_ini, z_fin, slices_for_bound_detectation=50, stride_for_bound_detectation=10, maintain_z_percentual=None, tol=10):
    """
    Calculates the bounding rectangle for a given microtom image.

    Parameters:
    filename (str): Path to the image file.
    slices_for_bound_detectation (int): Number of slices for bound detection.
    stride_for_bound_detectation (int): Stride for bound detection.
    maintain_z_percentual (list of float): Z axis bounds.
    tol (int): Tolerance for bounds.

    Returns:
    tuple: Contains filename and calculated bounds.
    """
    plug_rectangles = []
    with xr.open_dataset(filename) as db:
        middle_point = db.microtom.values.shape[0] // 2
        if slices_for_bound_detectation is None:
            slices_for_bound_detectation = middle_point

        if maintain_z_percentual is not None:
            if len(maintain_z_percentual) == 1:
                z_i_cut = z_f_cut = int(middle_point * maintain_z_percentual[0])
            elif len(maintain_z_percentual) == 2:
                z_i_cut = int(middle_point * maintain_z_percentual[0])
                z_f_cut = int(middle_point * maintain_z_percentual[1])
            z_i, z_f = middle_point - z_i_cut, middle_point + z_f_cut
        else:
            z_i, z_f = 0, db.microtom.values.shape[0]

        interval_indexes = [middle_point - slices_for_bound_detectation, middle_point + slices_for_bound_detectation]
        for img in db.microtom.values[interval_indexes[0]:interval_indexes[1]:stride_for_bound_detectation]:
            try:
                img[np.where(img > img.mean() + img.std())] = img.mean() + img.std()
                img[np.where(img < img.mean() - img.std())] = img.mean() - img.std()
                img[np.where(img < 0)] = 0
                img2 = np.array(img).copy()

                if img.dtype != np.uint8:
                    img2 = img2 // 255
                    img2 = img2.astype(np.uint8)

                ret, thresh1 = cv2.threshold(img2, (0), 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                kernel = np.ones((2, 2), np.uint8)
                thresh1 = cv2.dilate(thresh1, kernel, iterations=7)

                minRadius = int(min(thresh1.shape) / 3)
                maxRadius = int(max(thresh1.shape) / 2)

                circles = cv2.HoughCircles(thresh1, cv2.HOUGH_GRADIENT, 2, minDist=min(thresh1.shape), param1=50, param2=30, minRadius=minRadius, maxRadius=maxRadius)[0]
                circles = circles.flatten()

                x_i = int(circles[0] - circles[2] / (np.sqrt(2)))
                x_f = int(circles[0] + circles[2] / (np.sqrt(2)))
                y_i = int(circles[1] - circles[2] / (np.sqrt(2)))
                y_f = int(circles[1] + circles[2] / (np.sqrt(2)))
                plug_rectangles.append(box(x_i, y_i, x_f, y_f))
            except:
                continue

    rectangle = plug_rectangles[0]
    for rect in plug_rectangles[1:]:
        rectangle = rectangle.intersection(rect)
    bounds = np.array(rectangle.bounds).astype(int)
    y_i, y_f = bounds[0] + tol, bounds[2] - tol
    x_i, x_f = bounds[1] + tol, bounds[3] - tol
    
    ydif = y_f - y_i
    xdif = x_f - x_i
    mindif = min(y_f - y_i, x_f - x_i)

    x_i = x_i + np.floor((xdif-mindif)/2)
    x_f = x_f - np.ceil((xdif-mindif)/2)
    y_i = y_i + np.floor((ydif-mindif)/2)
    y_f = y_f - np.ceil((ydif-mindif)/2)

    halfdif = mindif // 2

    if mindif % 2 == 0:
        z_i = middle_point - halfdif
        z_f = middle_point + halfdif
    else:
        z_i = middle_point - halfdif 
        z_f = middle_point + halfdif + 1

    x_dif = x_f - x_i

    # If z_ini and z_fin informed are lower then x and y dimensions, execution stops.
    if z_ini is not None and z_fin is not None:
        if z_fin - z_ini < x_dif:
            print(f'z_ini: {z_ini},z_fin: {z_fin}', flush = True)
            print(f"ERROR: Sample is too small, bounds cannot be calculated. Minimum z dimension is {x_f - x_i}", flush=True)
            sys.exit(1)
        return filename, z_ini, z_fin, x_i, x_f, y_i, y_f
        
    print('z_ini and z_fin guessed automatically.', flush = True)

    # If automatically calculated z_ini and z_fin calculated with the goal of achieving x and y dimensions (cubic region) fails, execution stops.
    if z_f - z_i < x_dif:
        print(f'z_ini: {z_ini},z_fin: {z_fin}', flush = True)
        print(f"ERROR: Sample is too small, bounds cannot be calculated. Minimum z dimension is {x_dif}", flush=True)
        sys.exit(1)

    # Automatic cropping
    z_ini = 0.1*db.microtom.values.shape[0]
    z_fin = 0.9*db.microtom.values.shape[0]

    # If cubic region calculated z_i or z_f result in a bigger ROI, choose them over automatic cropped z_ini and z_fin.
    if z_i <= z_ini:
        z_ini = z_i
    if z_f >= z_fin:
        z_fin = z_f

    if z_fin - z_ini < x_dif:
        print(f"ERROR: Sample is too small, bounds cannot be calculated. Minimum z dimension is {x_f - x_i}", flush=True)
        sys.exit(1)
    return filename, z_ini, z_fin, x_i, x_f, y_i, y_f

def get_info(filename, z_i, z_f):
    """
    Extracts information from a specific range of a microtom image.

    Parameters:
    filename (str): Path to the image file.
    z_i (int): Starting index for the Z-axis.
    z_f (int): Ending index for the Z-axis.

    Returns:
    list: List of tuples with filename and selected positions.
    """
    with xr.open_dataset(filename) as db:
        im = np.array(db['microtom'])
    selection = np.random.choice(range(int(z_i), int(z_f) + 1), 100, replace=False)
    selected_data = [filename] * len(selection)
    return list(zip(selected_data, selection))

def get_contrast_adjustments_values(info):
    """
    Gets voidmean and rockmedian values for the image.

    Parameters:
    info (tuple): A tuple containing the filename (str) and position (int) of the image.

    Returns:
    tuple: A tuple containing:
        - filename (str): The name of the file.
        - voidmean (float): The mean value of the void areas in the image after adjustment.
        - rockmedian (float): The median value of the rock areas in the image after adjustment.
    """
    
    filename, position = info
    with xr.open_dataset(filename) as db:
        im = np.array(db['microtom'][position])

    img = im.copy()
    avg, std = np.mean(img), np.std(img)
    typing = img.dtype
    img[np.where(img > avg + std)] = avg + std
    img[np.where(img < avg - std)] = avg - std
    img[np.where(img < 0)] = 0
    if typing != np.uint8:
        img = (img // 255).astype(np.uint8)

    ret, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((2, 2), np.uint8)
    thresh = cv2.dilate(thresh, kernel, iterations=7)
    thresh = thresh.astype(np.bool_)
    thresh = ~thresh

    voidmean = np.mean(im[thresh])
    im = im - voidmean
    im[np.where(im < 0)] = 0
    rockmedian = np.median(im[~thresh])

    return filename, voidmean, rockmedian
