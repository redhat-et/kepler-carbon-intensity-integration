from singularity import SingularityAPI, Regions
from dotenv import dotenv_values
import os
import json
import datetime
import pandas as pd
import numpy as np
import time

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY


mock=True

# create a longitude and latitude lookup table
# return longitude and latitude for a region
def get_long_lat(region):
    if region == 'ISONE':
        return -71.5, 42.5
    elif region == 'CAISO':
        return -121.5, 38.5
    elif region == 'PJM':
        return -75.5, 39.5
    elif region == 'MISO':
        return -89.5, 44.5
    elif region == 'NYISO':
        return -75.5, 43.5
    elif region == 'SPP':
        return -100.5, 37.5
    elif region == 'BPA':
        return -122.5, 45.5
    elif region == 'IESO':
        return -80.5, 44.5
    else:
        return 0, 0

# get the data from singularity api and return the data as pandas dataframe
def get_data():
    config = dotenv_values(os.path.join(os.path.dirname(__file__), 'config.env'))

    s_api = SingularityAPI(config["API_KEY"])

    # use Singularity's (incomplete) zip code lookup to find
    #data=s_api.latest_region_events(postal_code='02108', event_type='carbon_intensity', start='2020-01-20T00:00:00Z', end='2023-05-21T00:00:00Z')
    # events for a zip code
    # loop zip code 02108 and 94106, get the event and save to json file
    for region_code in ['ISONE', 'CAISO', 'PJM', 'MISO', 'NYISO', 'SPP', 'BPA', 'IESO']:
        # if the data file is not exist, get the data from singularity api
        if not os.path.isfile('{}.json'.format(region_code)):
            # get current date in iso8601 datetime string format
            curr = datetime.datetime.now().isoformat()
            # get the 7 days before current date
            start = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
            data=s_api.search_region_events(region=region_code, event_type='carbon_intensity', start=start, end=curr)
            print(region_code)
            with open('{}.json'.format(region_code), 'w') as outfile:
                json.dump(data, outfile)

    if mock == True:
        # create a pandas dataframe to store the data
        df = pd.DataFrame(columns=['start_date', 'ISONE', 'CAISO', 'PJM', 'MISO', 'NYISO', 'SPP', 'BPA', 'IESO'])
        # read from region code data
        for region_code in ['ISONE', 'CAISO', 'PJM', 'MISO', 'NYISO', 'SPP', 'BPA', 'IESO']: 
            with open('{}.json'.format(region_code), 'r') as infile:
                # read from infile as json
                data = json.load(infile)
                # the json format is as the following
                # [
                #     [
                #         {
                #             "data": {
                #                 "consumed_rate": 310.00176724456895,
                #                 "generated_rate": 246.27783106713468,
                #                 "marginal_rate": 213.97069661473768
                #             },
                #             "dedup_key": "BPA:carbon_intensity:EGRID_u2019:2023-03-23T16:25:00+00:00",
                #             "event_type": "carbon_intensity",
                #             "meta": {
                #                 "consumed_emissions_source": "EGRID_u2019",
                #                 "consumed_rate_calculated_at": "2023-03-26T21:00:47.961987Z",
                #                 "consumed_source": "generated_fuel_mix:EIA.BPAT:2023-03-23T16:25:00+00:00",
                #                 "generated_emissions_source": "EGRID_u2019",
                #                 "inserted_at": "2023-03-23T16:27:32.069500Z",
                #                 "marginal_emissions_source": "EGRID_u2019",
                #                 "marginal_fuel_mix_source": "INTV_DIFF",
                #                 "marginal_source": "BPA:marginal_fuel_mix:2023-03-23T16:25:00+00:00",
                #                 "raw_start_date": "2023-03-23T16:25:00+00:00",
                #                 "source": "generated_fuel_mix:BPA:2023-03-23T16:25:00+00:00",
                #                 "unit": "lbs/MWh",
                #                 "updated_at": "2023-03-26T21:00:49.167230Z"
                #             },
                #             "region": "BPA",
                #             "start_date": "2023-03-23T16:25:00+00:00"
                #         }
                #     ],
                # ]
                # get the data from json, loop through the data and print the 'generated_rate' and 'start_date'
                # create a numpy array to store the data
                np = []
                for i in data:
                    for j in i:
                        # try print the 'generated_rate' and 'start_date' and ignore all errors
                        try:
                            np.append([j['start_date'], j['data']['generated_rate']])
                        except:
                            pass
                # convert the numpy array to pandas dataframe
                df1 = pd.DataFrame(np, columns=['start_date', region_code])
                # merge the dataframe with the dataframe created before
                df = pd.merge(df, df1, on='start_date', how='outer', suffixes=('_x',None))
        # only keep 'start_date' 'ISONE', 'CAISO', 'PJM', 'MISO', 'NYISO', 'SPP', 'BPA', 'IESO', and save the dataframe to csv file
        df = df[['start_date', 'ISONE', 'CAISO', 'PJM', 'MISO', 'NYISO', 'SPP', 'BPA', 'IESO']]
        #df.to_csv('carbon_intensity.csv', index=False)
        return df

# create a prometheus metric collector
class CarbonIntensityCollector(object):
    def __init__(self, df):
        self.df = df
        # set the current cursor to 0
        self.cursor = 0

    def collect(self):
        # loop through df, for each row, extract the 'start_date' and 'ISONE', 'CAISO', 'PJM', 'MISO', 'NYISO', 'SPP', 'BPA', 'IESO' 
        # create a prometheus metric for each region code
        metric = GaugeMetricFamily('carbon_intensity', 'carbon_intensity', labels=['region', 'longitude', 'latitude'])
        # get the current row using cursor
        row = self.df.iloc[self.cursor]
        # increment the cursor by 1 mod the length of the dataframe
        self.cursor = (self.cursor + 1) % len(self.df)
        # get the start_date
        start_date = row['start_date']
        for region_code in ['ISONE', 'CAISO', 'PJM', 'MISO', 'NYISO', 'SPP', 'BPA', 'IESO']: 
            carbon_intensity = row[region_code]
            longitude, latitude = get_long_lat(region_code)
            longitude = str(longitude)
            latitude = str(latitude)
            # create a prometheus metric for each region code        
            # create a prometheus metric
            metric.add_metric([region_code, longitude, latitude], carbon_intensity)
        print(metric)
        yield metric

if __name__ == '__main__':
    # get the dataframe
    df = get_data()
    # start the prometheus server
    start_http_server(8000)
    # register the prometheus metric
    REGISTRY.register(CarbonIntensityCollector(df))

    while True: 
        #generate_latest(REGISTRY)
        time.sleep(30)
        



            
