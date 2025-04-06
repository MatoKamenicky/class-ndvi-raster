import rasterio as rio
import numpy as np
import matplotlib.pyplot as plt
import glob
from rasterio.plot import show
import os


def get_thresholds(data):
    percentile20 = np.percentile(data, 20)
    percentile40 = np.percentile(data, 40)
    percentile60 = np.percentile(data, 60)
    percentile80 = np.percentile(data, 80)
    percentile100 = np.max(data)
    return [percentile20, percentile40, percentile60, percentile80, percentile100]


def reclassify_raster(raster_data, valid_data):
    thresholds = get_thresholds(valid_data)
    target_values = [1, 2, 3, 4, 5]

    result_data = np.zeros(np.shape(raster_data))
    result_data[raster_data == -998] = -998

    for i, threshold in enumerate(thresholds):
        mask = np.logical_and(result_data == 0, raster_data <= threshold)
        result_data[mask] = target_values[i]

    return result_data

def plot_input_file(input_rasters, filenames, cmap='Greens'):
    # Show input raster files
    for i in range(len(input_rasters)):
        show(input_rasters[i], cmap=cmap, title=filenames[i], vmin=0, vmax=1)
        plt.show()
    return


def plot_reclass_file(reclass_rasters, filenames, cmap='Greens'):
    # Show reclass raster files
    for i in range(len(reclass_rasters)):
        fig, ax = plt.subplots()
        im = ax.imshow(reclass_rasters[i], cmap=cmap, vmin=0, vmax=5)
        ax.set_title(filenames[i])
        plt.colorbar(im, ax=ax)
        plt.show() 

def plot_average_file(average, cmap='Greens'):
    plt.imshow(average, cmap=cmap, vmin=0, vmax=5)
    cbar = plt.colorbar(ticks=[1, 2, 3, 4, 5])
    cbar.set_label('Class')
    plt.title('Average EVI raster')
    plt.show()
    return

def save_geotiff(src, average):
    with rio.open(
        'average.tiff',
        'w',
        driver=src.driver,
        height=src.height,
        width=src.width,
        count=src.count,
        dtype=average.dtype,
        crs=src.crs,
        transform=src.transform,
    ) as dst:
        dst.write(average, 1)
    return


if __name__ == '__main__':
    folder = 'EVI/'
    files = glob.glob(folder + '*.tiff')
    filenames = []
    input_rasters = []

    # Open and read raster files
    reclass_rasters = []
    for f in files:
        filenames.append(os.path.basename(f))        
        src = rio.open(f)
        data = src.read(1)
        input_rasters.append(data)
        data_mask = src.read(1, masked=True)
        masked_data = np.ma.masked_invalid(data_mask)
        valid_data = masked_data.compressed()

        reclass = reclassify_raster(data, valid_data)
        reclass_rasters.append(reclass)

    average = np.round(np.mean(reclass_rasters, axis=0), 0)


    # Plot input files
    plot_input_file(input_rasters, filenames)


    # Plot reclass files
    plot_reclass_file(reclass_rasters, filenames)
        
    # Plot average file
    plot_average_file(average)

    # Save average file
    save_geotiff(src, average)














