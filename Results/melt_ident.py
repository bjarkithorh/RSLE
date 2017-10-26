import pandas as pd
import numpy as np
import datetime
from datetime import datetime
import os
import os.path

#Directories of import files and output files

raw_results = '/dir/to/RSLE/Results/comb_results/'
output_results = '/dir/to/RSLE/Results/melt_periods/'

#Loop through the result files and process each one.

for res in os.listdir(raw_results):
    if res.endswith(".csv"):
        print('Cathchment: ', res)
        catch = res
        res = os.path.join(raw_results, res)
        #Import the result file and set it up as a Pandas dataframe
        result = pd.read_csv(res, header=0, sep=',',  index_col  = [0])
        result.index = pd.to_datetime(result.index)

        #Make an object including only the S_RSLE series

        s_rsle = result['S_RSLE'][::-1]
        s_rsle = s_rsle.shift(-2)

        #Create an empty array to store mask data in.
        melt_mask = []

        #Shift the S_RSLE up by one day
        S_RSLE_p1 = result['S_RSLE'].shift(1)

        #Loop through the S_RSLE and identify where the slope 
        #of the series is positive, negative or constant.

        for a, b in zip(result['S_RSLE'], S_RSLE_p1):
          if a - b > 0:
          	melt_mask.append(a)
          elif a - b < 0:
            melt_mask.append(a)
          else:
            melt_mask.append(0)

        #Make the array a numpy array.

        melt_mask = np.array(melt_mask)

        #Convert the zeros in the array to NaN values.

        melt_mask[melt_mask == 0] = np.nan

		#Convert the Date column into a numpy array and 
		#combine melt and date in a DataFrame.

        melt_mask = pd.DataFrame(data=melt_mask, columns=['MeltP'])
        date = result['Date'].tolist()
        datetime_index = [datetime.strptime(x, '%Y.%m.%d') for x in date]
        rng = pd.date_range('1/1/2000', periods=6084, freq='D')
        melt_mask = melt_mask.set_index(rng)

        #Lets reverse the dataframe.

        melt_mask = melt_mask[::-1]
        melt_mask = melt_mask.shift(-2)

        #Loop through the data and from 31.August find the closest
        #max elevation.

        years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 
                 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]

        #Create a datafram for the resultes (inside catchment loop).

        results = pd.DataFrame()

        #First we loop through each year since we are looking for
        #Yearly events.

        for y in years:

            st = datetime(y, 1, 1, 0, 0)
            en = datetime(y, 12, 31, 0, 0)
            end_aug = datetime(y, 8, 31, 0, 0)
        
            re_year = melt_mask[end_aug:st]
            day_count = 0
            year_count = np.array([y])
            begin = np.array([])
            end = np.array([])

            year_ts = result['S_RSLE']
            year_ts = year_ts[st:en]

            min = year_ts.min()
            max = year_ts.max()

            for i, a in zip(re_year['MeltP'], re_year.index):
                if i == max:
                    end = np.append(end, a)
                    break
            re_year_sec = s_rsle[a:st]
            for i, b in zip(re_year_sec, re_year_sec.index):
                day_count = day_count + 1
                if i == min:
                    begin = np.append(begin, b)
                    break
            day_count_arr = np.array([day_count])
			
            #Calculate the slope
            slope = day_count / (max-min)
            slope = np.array([slope])

            #Insert the results into dataframes
            year_count = pd.DataFrame(data=year_count, columns=['Year'])
            beginning = pd.DataFrame(data=begin, columns=['Beginning'])
            ending = pd.DataFrame(data=end, columns=['End'])
            day_counting = pd.DataFrame(data=day_count_arr, columns=['Days'])
            sloper = pd.DataFrame(data=slope, columns=['Slope'])

            concat_list = [year_count, beginning, ending, day_counting, sloper]
            nidur = pd.concat(concat_list, axis=1)
            nidur.set_index(['Year'])

            results = pd.concat([results, nidur], axis=0)
        print(results)
        resultcsv = output_results + 'melt_' + catch #Name of the outputfile
        results.to_csv(path_or_buf=resultcsv, sep=',')
print('Everything has melted...')