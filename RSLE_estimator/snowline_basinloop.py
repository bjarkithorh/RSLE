import subprocess
import os
import os.path
import numpy as np
import gdal
import numpy.ma as ma
import csv
import pandas as pd
import time
import shutil
start = time.time()

scriptpath = os.path.dirname(os.path.abspath(__file__))

#Paths to input and output data.
shapedir = '/dir/to/catchment/shape/files/'
shpfinish = '/dir/to/used/catchment/shape/files'
indem = '/path/to/dem/covering/cathments.tif' #DEM tif input
outdem = os.path.join(scriptpath, 'temporary_catchm.tif')
modisdir = '/dir/to/modis/snow/cover/tif/files'
outmodis = os.path.join(scriptpath, 'buffer_mod.tif')
result_path = '/dir/to/where/result/files/are/saved/'

#Make shure all files, shape, dem and modis are in the same projection.

#Make a list of shape files
shpfiles = os.listdir(shapedir)

#Loop through basin shape files.
for shapef in os.listdir(shapedir):
    if shapef.endswith(".shp"):
        basinshape = shapef
        shape = os.path.join(shapedir, shapef)
        #Create empty arrays to store results in.
        rsle_list = np.array([])
        modis_list = np.array([])
        snow_list = np.array([])
        land_list = np.array([])
        cloud_list = np.array([])
        #Here we cut the DEM by the catchment shapefile mask.
        if os.path.exists(outdem):
            os.remove(outdem)
        subprocess.call(['gdalwarp','-cutline', shape, '-crop_to_cutline','-dstnodata','"-9999.0"', indem, outdem])

        #Here we read the dem  into a numpy array.
        cdme = gdal.Open(outdem)
        srcband = cdme.GetRasterBand(1)
        stats = srcband.GetStatistics(True, True)
        elev = np.array(cdme.GetRasterBand(1).ReadAsArray())

        #Calculate min and max elevation of the cathment.
        minelev = elev[elev>0]
        minelev = minelev.min()
        minelev = minelev.astype(int)
        maxelev = elev.max()
        maxelev = maxelev.astype(int)
        print('Max: ', maxelev, 'Min: ', minelev)
        print(shapef)

        #Here we will start the loop that loops through the modis images.
        for inmodis in os.listdir(modisdir):
            if inmodis.endswith(".tif"):
                modisname = inmodis
                inmodis = os.path.join(modisdir, inmodis)
                #We cut the MODIS tiff by the catchment shapefile mask.
                if os.path.exists(outmodis):
                    os.remove(outmodis)
                subprocess.call(['gdalwarp','-cutline', shape, '-crop_to_cutline','-dstnodata','"-9999.0"', inmodis, outmodis])

                #Read the modis and dem as numpy arrays.
                cmod = gdal.Open(outmodis)
                modis = np.array(cmod.GetRasterBand(1).ReadAsArray())

                #Count number of pixels of certain types in the MODIS
                snow = (modis == 200).sum()     #freq of snow pixels
                cloud = (modis == 50).sum()     #freq of cloud pixels
                land = (modis == 25).sum()      #freq of land pixels
                night = (modis == 11).sum()     #freq of night pixels
                misda = (modis == 0).sum()      #freq of missing data pixels
                nodec = (modis == 1).sum()      #freq of no decision pixels

                #Create elevation steps.
                elevb = list(range(minelev, maxelev, 10))

                #Create an empty dictionary for results to be appended into.
                nidurst = {}

                #Loop through elevation steps of the catchment to estimate snow line elevation.
                for i in elevb:
                    #Create matrix with only values above the elevation band being tested.
                    elevtvo = elev > i
                    elevtvo = elevtvo.astype(int)
                    elevbe = elev < i
                    elevbe = elevbe.astype(int)
                    above = np.multiply(elevtvo, modis)
                    below = np.multiply(elevbe, modis)
                    sumpix_above = above.sum()
                    #Estimate the number of snow pixels above and belove elevation being tested.
                    snon = (below == 200).sum()
                    #Estimate numner of land pixels above and below elevation being tested.
                    lanu = (above == 25).sum()
                    #Calculate ratios of snow and land pixels above and below the elveation being tested.
                    snolanrat = snon + lanu#/sumpix_above
                    nidurst[snolanrat] = i
                    #Get the elevation with minimum snow pixels below and land pixels above.
                    rsle = min(nidurst.items(), key=lambda x: x[0])
                    rsle = rsle[1]
                    #Print results
                rsle_list = np.append(rsle_list, rsle)
                modis_list = np.append(modis_list, modisname)
                snow_list = np.append(snow_list, snow)
                land_list = np.append(land_list, land)
                cloud_list = np.append(cloud_list, cloud)
                #print('RSLE: ', rsle, 'mas, Snow: ', snow, ', Clouds: ', cloud, ', Land: ', land, ', Night: ', night, ', Missing data: ', misda, ', No decision: ', nodec, 'MODIS: ', inmodis)
        #Collect results into a pandas dataframe and write them to a csv file.
        nidur_rsle = pd.DataFrame(data=rsle_list, columns=['RSLE'])
        nidur_modis = pd.DataFrame(data=modis_list, columns=['MODIS'])
        nidur_snow = pd.DataFrame(data=snow_list, columns=['Snow'])
        nidur_land = pd.DataFrame(data=land_list, columns=['Land'])
        nidur_cloud = pd.DataFrame(data=cloud_list, columns=['Cloud'])
        nidurst = [nidur_modis, nidur_rsle, nidur_snow, nidur_land, nidur_cloud]
        fin_nid = pd.concat(nidurst, axis=1)
        print(fin_nid)
        resultcsv = result_path + basinshape + '.csv' #Name of the outputfile
        fin_nid.to_csv(path_or_buf=resultcsv, sep=',')
        shp_move = basinshape[:-4]
        for f in shpfiles:
            if f.startswith(shp_move):
                shpmove = os.path.join(shapedir, f)
                shpmoveto = os.path.join(shpfinish, f)
                shutil.move(shpmove, shpmoveto)
end = time.time()-start
endcomment = "Script has finished running! Hurraaa! It took the script ", end, "second to run!"
print(endcomment)
