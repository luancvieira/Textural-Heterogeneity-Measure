#viewsplot.py

import os
import sys
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import argparse
import time

def plot_views_from_sample(dfdataset, output_folder):
    row = dfdataset.iloc[0]
    sample_path = row['dataset']
    sample_name = row['dataset'].split('/')[-1].split('.')[0]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        with xr.open_dataset(sample_path) as nc:
            microtom = nc['microtom']
            x_central = microtom.shape[1] // 2
            y_central = microtom.shape[2] // 2
            z_central = microtom.shape[0] // 2
            
            microtom = np.array(microtom)

            microtom = microtom - float(row['voidmean'])
            microtom = microtom * 32768 / float(row['rockmedian'])
            microtom = np.clip(microtom, 0, 65535)
            
            fig, ax = plt.subplots(1, 3, figsize=(12, 5))
            titles = ['XY', 'XZ', 'YZ']
            cmap = 'gray'
            slices = [
                np.transpose(microtom[z_central, :, :], (1, 0)),
                microtom[:, :, y_central],
                microtom[:, x_central, :]
            ]
    
            vmin = min(slice.min() for slice in slices)
            vmax = max(slice.max() for slice in slices)

            rects = [
                plt.Rectangle((row['x_ini'], row['y_ini']), row['x_fin'] - row['x_ini'], row['y_fin'] - row['y_ini'], fill=False, linewidth=2, edgecolor='y'),
                plt.Rectangle((row['x_ini'], row['z_ini']), row['x_fin'] - row['x_ini'], row['z_fin'] - row['z_ini'], fill=False, linewidth=2, edgecolor='y'),
                plt.Rectangle((row['y_ini'], row['z_ini']), row['y_fin'] - row['y_ini'], row['z_fin'] - row['z_ini'], fill=False, linewidth=2, edgecolor='y')
            ]
    
            for j, (data, rect) in enumerate(zip(slices, rects)):
                im = ax[j].imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
                ax[j].add_patch(rect)
                ax[j].set_title(titles[j])

            cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
            fig.colorbar(im, cax=cbar_ax).set_label('Intensity')
    
            fig.suptitle(sample_name)
    
            output_path = os.path.join(output_folder, f"plot_views_{sample_name}.jpeg")
            fig.savefig(output_path, bbox_inches='tight', dpi=300)
            plt.close(fig)
            print(f"Saved plot to {output_path}", flush=True)
    
            del microtom
            del nc
            
    except Exception as e:
        print(f"Error plotting views from sample {sample_name}: {e}", flush=True)
