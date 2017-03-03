import numpy as np
import os
import os.path
import subprocess
import gdal
import pandas as pd
import shutil

#Directories to various input and output files.

scriptpath = '/uio/lagringshotell/geofag/projects/hycamp/team/bjarkith/RSLE/senorge/'

indem = '/uio/lagringshotell/geofag/projects/hycamp/team/bjarkith/RSLE/GIS/DEM/norgedem500align33.tif'
outdem =  os.path.join(scriptpath, 'bufferdem.tif')
shapedir = '/uio/lagringshotell/geofag/projects/hycamp/team/bjarkith/RSLE/GIS/basin_shp_senorge/'
shpfinish = '/uio/lagringshotell/geofag/projects/hycamp/team/bjarkith/RSLE/GIS/basin_shp_senorge_finished/'
senorgetmdir = '/uio/lagringshotell/geofag/projects/hycamp/team/bjarkith/RSLE/senorge/tm_1.1/daily/mask/'
senorgetmout =  os.path.join(scriptpath, 'buffersenorgetm.tif')
senorgeswedir = '/uio/lagringshotell/geofag/projects/hycamp/team/bjarkith/RSLE/senorge/swe_1.1.1/daily/mask/'
senorgesweout = os.path.join(scriptpath, 'buffersenorgeswe.tif')
senorgerrscdir = '/uio/lagringshotell/geofag/projects/hycamp/team/bjarkith/RSLE/senorge/rrsc_1.1/daily/mask/'
senorgerrscout = os.path.join(scriptpath, 'buffersenorgerrsc.tif')
senorgerrldir = '/uio/lagringshotell/geofag/projects/hycamp/team/bjarkith/RSLE/senorge/rrl_1.1/daily/mask/'
senorgerrlout = os.path.join(scriptpath, 'buffersenorgerrl.tif')
senorgerrdir = '/uio/lagringshotell/geofag/projects/hycamp/team/bjarkith/RSLE/senorge/rr_1.1/daily/mask/'
senorgerrout = os.path.join(scriptpath, 'buffersenorgerr.tif')
senorgegwbqdir = '/uio/lagringshotell/geofag/projects/hycamp/team/bjarkith/RSLE/senorge/gwb_q_1.1/daily/mask/'
senorgegwbqout = os.path.join(scriptpath, 'buffersenorgegwbq.tif')

result_directory = '/uio/lagringshotell/geofag/projects/hycamp/team/bjarkith/RSLE/Results/Senorge/'

#Here we begin to loop through the catchments.

for shapef in os.listdir(shapedir):
    if shapef.endswith("Reprojected_vassdragNr_022.EZ.shp"):
        basinshape = shapef
        shape = os.path.join(shapedir, shapef)

        #Create empty arrays to store results in.

        day_list = np.array([])
        tm_list = np.array([])
        swe_list = np.array([])
        rrsc_list = np.array([])
        rrl_list = np.array([])
        rr_list = np.array([])
        gwbq_list = np.array([])
        catchment_size = np.array([])

        #Loop through the data

        for intif in os.listdir(senorgetmdir):
                    if intif.endswith('.tif'):

                        senorgetmin = os.path.join(senorgetmdir, intif)
                        senorgeswein = os.path.join(senorgeswedir, intif)
                        senorgerrscin = os.path.join(senorgerrscdir, intif)
                        senorgerrlin = os.path.join(senorgerrldir, intif)
                        senorgerrin = os.path.join(senorgerrdir, intif)
                        senorgegwbqin = os.path.join(senorgegwbqdir, intif)

                        print(senorgetmin)

                        #Here we crop the senorge data files by the catchment areas.

                        if os.path.exists(senorgetmout):
                            os.remove(senorgetmout)
                        subprocess.call(['gdalwarp','-cutline', shape, '-crop_to_cutline','-dstnodata','"-9999.0"', senorgetmin, senorgetmout])

                        if os.path.exists(senorgesweout):
                            os.remove(senorgesweout)
                        subprocess.call(['gdalwarp','-cutline', shape, '-crop_to_cutline','-dstnodata','"-9999.0"', senorgeswein, senorgesweout])

                        if os.path.exists(senorgerrscout):
                            os.remove(senorgerrscout)
                        subprocess.call(['gdalwarp','-cutline', shape, '-crop_to_cutline','-dstnodata','"-9999.0"', senorgerrscin, senorgerrscout])
                       
                        if os.path.exists(senorgerrlout):
                            os.remove(senorgerrlout)
                        subprocess.call(['gdalwarp','-cutline', shape, '-crop_to_cutline','-dstnodata','"-9999.0"', senorgerrlin, senorgerrlout])

                        if os.path.exists(senorgerrout):
                            os.remove(senorgerrout)
                        subprocess.call(['gdalwarp','-cutline', shape, '-crop_to_cutline','-dstnodata','"-9999.0"', senorgerrin, senorgerrout])
                        
                        if os.path.exists(senorgegwbqout):
                            os.remove(senorgegwbqout)
                        subprocess.call(['gdalwarp','-cutline', shape, '-crop_to_cutline','-dstnodata','"-9999.0"', senorgegwbqin, senorgegwbqout])
                        
                        #Read the tm tif and get mean temperature of the catchment.

                        ctm = gdal.Open(senorgetmout)
                        tmmap = np.array(ctm.GetRasterBand(1).ReadAsArray())
                        tmmap = tmmap[tmmap>-150]
                        tm_mean = tmmap.mean()

                        #Read the swe and get mean swe of the catchment.

                        cswe = gdal.Open(senorgesweout)
                        swemap = np.array(cswe.GetRasterBand(1).ReadAsArray())
                        swemap =  swemap[swemap>0]
                        swe_mean = swemap.mean()

                        #Read the rrsc and get the mean of the catchment.

                        crrsc = gdal.Open(senorgerrscout)
                        rrscmap = np.array(crrsc.GetRasterBand(1).ReadAsArray())
                        rrscmap = rrscmap[rrscmap>=0]
                        rrsc_mean = rrscmap.mean()
                        
                        #Read the rrl and get the mean of the cathment.

                        crrl = gdal.Open(senorgerrlout)
                        rrlmap = np.array(crrl.GetRasterBand(1).ReadAsArray())
                        rrlmap = rrlmap[rrlmap>=0]
                        rrl_mean = rrlmap.mean()

                        #Read the rr and get the mean of the catchment.

                        crr = gdal.Open(senorgerrout)
                        rrmap = np.array(crr.GetRasterBand(1).ReadAsArray())
                        rrmap = rrmap[rrmap>=0]
                        rr_mean = rrmap.mean()
                        
                        #Read the runoff and sum it up.

                        cgwbq = gdal.Open(senorgegwbqout)
                        gwbqmap = np.array(cgwbq.GetRasterBand(1).ReadAsArray())
                        gwbqmap_run = gwbqmap[gwbqmap>0]
                        gwbq_sum = np.sum(gwbqmap_run)

                        #Count the number of pixels in the catchment

                        gwbqmap[gwbqmap >= 0] = 1
                        pixel_nr = (gwbqmap == 1).sum()

                        #Divide the runoff sum with the number of pixels to get mm/km2

                        runoff = gwbq_sum / pixel_nr
                        
                        #Gather the results in arrays
                        day_list = np.append(day_list, intif)
                        tm_list = np.append(tm_list, tm_mean)
                        swe_list = np.append(swe_list, swe_mean)
                        rrsc_list = np.append(rrsc_list, rrsc_mean)
                        rrl_list = np.append(rrl_list, rrl_mean)
                        gwbq_list = np.append(gwbq_list, runoff)
                        catchment_size = np.append(catchment_size, pixel_nr)

        #Here we create DataFrames using the data we gathered above and concat it
        #into one dataframe containing all the results.

        nidur_day = pd.DataFrame(data=day_list, columns=['file'])
        nidur_tm = pd.DataFrame(data=tm_list, columns=['tm'])
        nidur_swe = pd.DataFrame(data=swe_list, columns=['swe'])
        nidur_rrsc = pd.DataFrame(data=rrsc_list, columns=['rrsc'])
        nidur_rrl = pd.DataFrame(data=rrl_list, columns=['rrl'])
        nidur_rr = pd.DataFrame(data=rr_list, columns=['rr'])
        nidur_gwbq = pd.DataFrame(data=gwbq_list, columns=['gwb_q'])
        nidur_catchment_size = pd.DataFrame(data=catchment_size, columns=['cathm_size'])

        nidurst = [nidur_day, nidur_tm, nidur_swe, nidur_rrsc, nidur_rrl, nidur_rr, nidur_gwbq, nidur_catchment_size]
        fin_nid = pd.concat(nidurst, axis=1)
        
        #Here we save the output as csv files.

        resultcsv = result_directory + basinshape + '_tm_swe_rrsc.csv'

        fin_nid.to_csv(path_or_buf=resultcsv, sep=',')
        print(fin_nid)

        #Here we move the shapefiles to a new directory so we can pick up from
        #where we were in case the there is a problem with the progress.

        shp_move = basinshape[:-4]
        for f in shapef:
            if f.startswith(shp_move):
                shpmove = os.path.join(shapedir, f)
                shpmoveto = os.path.join(shpfinish, f)
                shutil.move(shpmove, shpmoveto)
print('The end is here...')