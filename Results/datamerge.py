import pandas as pd
import numpy as np
import datetime
from datetime import datetime
import matplotlib.dates as mdates
import os
import os.path

#Direcotries to the result files
moddir = '/dir/to/RSLE/Results/Modis/'
sscadir = '/dir/to/RSLE/Results/Senorgesca/'
sendir = '/dir/to/RSLE/Results/Senorge/'
sqdir = '/dir/to/RSLE/Results/Senorgeq/'
finresdir = '/dir/to/RSLE/Results/comb_results/'

#The endfix for the output csv files.
fix = '.csv'
#The prefixes for the different parameters.
modisfix = 'm_sca_'
sscafix = 's_sca_'
senorgefix = 's_cli_'
sqfix = 's_run_'

#Now we loop the the result documents and organize and filter them.
for res in os.listdir(sscadir):
	res = res[6:-4]

	#Get the files needed for as input.
	modis_filename = modisfix+res+fix
	modis_file = os.path.join(moddir, modis_filename)
	ssca_filename = sscafix+res+fix
	ssca_file = os.path.join(sscadir, ssca_filename)
	seno_filename = senorgefix+res+fix
	seno_file = os.path.join(sendir, seno_filename)
	sq_filename = sqfix+res+fix
	sq_file = os.path.join(sqdir, sq_filename)
 
	#Import seNorge SCA RSLE results and set them up in a dataframe
	senorge_snowline = pd.read_csv(ssca_file, header=0, sep=',',  index_col  = [0])
	senorge_snowline  = senorge_snowline.rename(columns={'seNorge': 'Date','RSLE': 'S_RSLE', 'Snow': 'S_Snow', 'Land': 'S_Land'})
	senorge_snowline  = senorge_snowline.sort_values(by="Date")
	senorge_snowline.set_index(['Date'])

	#Import MODIS  RSLE results and set them up in a dataframe
	modis_snowline = pd.read_csv(modis_file, header=0, sep=',',  index_col  = [0])
	modis_snowline = modis_snowline.rename(columns={'MODIS': 'Date','RSLE': 'M_RSLE', 'Snow': 'M_Snow', 'Land': 'M_Land', 'Cloud': 'M_Cloud'})
	modis_snowline = modis_snowline.sort_values(by="Date")
	modis_snowline.set_index(['Date'])

	#Import seNorge tm, swe and rrsc and set them up in a dataframe
	senorge_met = pd.read_csv(seno_file, header=0, sep=',',  index_col  = [0])
	senorge_met  = senorge_met.rename(columns={'file': 'Date','tm': 'S_temp', 'swe': 'S_swe', 'rrsc': 'S_rrsc', 'rrl': 'S_rrl', 'rr': 'S_rr'})
	senorge_met  = senorge_met.sort_values(by="Date")
	senorge_met.set_index(['Date'])

	#Import seNorge runoff data
	senorge_gwbq = pd.read_csv(sq_file, header=0, sep=',',  index_col  = [0])
	senorge_gwbq  = senorge_gwbq.rename(columns={'file': 'Date','gwb_q': 'gwb_q', 'cathm_size': 'Pix_Nr'})
	senorge_gwbq  = senorge_gwbq.sort_values(by="Date")
	senorge_gwbq.set_index(['Date'])


	#Merge the result dataframes into one data frame incoroporating all the data
	merge1 = senorge_snowline.merge(right=senorge_met, how='left', on='Date')
	merge2 = merge1.merge(right=modis_snowline, how='left', on='Date')
	merge3 = merge2.merge(right=senorge_gwbq, how='left', on='Date')

	#Remove days where there is more then 70% cloud cover and set up a column with RSLE on those days only
	nyM_RSLE = np.array([])
	cloud30p = (merge3['M_Cloud'].max())*(0.3)

	for row in merge3['M_Cloud']:
	    if row > cloud30p:
	        nyM_RSLE =  np.append(nyM_RSLE, [0.0])
	    else:
	        nyM_RSLE =  np.append(nyM_RSLE, [1.0])

	#Remove days where there is n Modis data.
	nodM_RSLE = np.array([])
	for c,s,l in zip(merge3['M_Cloud'], merge3['M_Snow'], merge3['M_Land']):
		if c == 0  and s == 0 and l ==0:
			nodM_RSLE = np.append(nodM_RSLE, [0.0])
		else:
			nodM_RSLE = np.append(nodM_RSLE, [1.0])

	M_RSLE_70pC = nyM_RSLE * merge3['M_RSLE'].values

	M_RSLE_70pCl = pd.DataFrame(data=M_RSLE_70pC, columns=['M_RSLE_70pC'])

	M_RSLE_70pC2 = nodM_RSLE * M_RSLE_70pCl['M_RSLE_70pC'].values

	M_RSLE_70pCnd = pd.DataFrame(data=M_RSLE_70pC2, columns=['M_RSLE_70pC'])
	print(M_RSLE_70pCnd)
	merge4 = merge3.join(M_RSLE_70pCnd)
	merge4['M_RSLE_70pC'] = merge4['M_RSLE_70pC'].replace({0.0: np.nan})
	merge4['S_rrsc'] = merge4['S_rrsc'].fillna(0.0)
	merge4['Date'] = merge4['Date'].astype(str).str[:-4]
	date = merge4['Date'].tolist()
	datetime_index = [datetime.strptime(x, '%Y.%m.%d') for x in date]
	rng = pd.date_range('1/1/2000', periods=6084, freq='D')
	merge4 = merge4.set_index(rng)

	merge4['S_RSLE70pC'] = np.where(merge4['M_RSLE_70pC']>0, merge4['S_RSLE'], np.nan)

	years = mdates.YearLocator()
	months = mdates.MonthLocator(bymonth=9, bymonthday=1, interval=1, tz=None)

	#Save the result as a csv
	resultcsvname = res+fix
	resultcsv = os.path.join(finresdir, resultcsvname)
	merge4.to_csv(path_or_buf=resultcsv, sep=',')