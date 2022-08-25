import requests
from requests.auth import HTTPBasicAuth
from dotenv import dotenv_values
import os
import time

#DEPRECATED

def scrape_all_ba_locations(watttime_token):
    ba_locations_url = 'https://api2.watttime.org/v2/ba-access'
    headers = {'Authorization': 'Bearer {}'.format(watttime_token)}
    parameters = {'all': 'false'}
    list_of_regions = requests.get(url=ba_locations_url, params=parameters, headers=headers).json()
    all_regions_ba = list(map(lambda x: x['ba'], list_of_regions))
    return all_regions_ba

def scrape_real_time_emissions_given_locations(watttime_token, ba_locations):
    real_time_timestamp_emissions = {}
    time_stamp = time.time()
    for location in ba_locations:
        index_and_moer_emissions_url = 'https://api2.watttime.org/index'
        headers = {'Authorization': 'Bearer {}'.format(watttime_token)}
        parameters = {'ba': '{}'.format(location)}
        emission_results = requests.get(index_and_moer_emissions_url, headers=headers, params=parameters).json()
        if time_stamp not in real_time_timestamp_emissions.keys():
            real_time_timestamp_emissions[time_stamp] = []
        real_time_timestamp_emissions[time_stamp].append({'moer': emission_results['moer'], 'percent': emission_results['percent'], 'time_of_data': emission_results['point_time'], 'ba': emission_results['ba']})
    return real_time_timestamp_emissions

if __name__ == "__main__":
    start_time = time.time()
    dirname = os.path.dirname
    config = dotenv_values(os.path.join(dirname(dirname(__file__)), '.env'))
    watttime_token = requests.get(config["LOGIN_URL_WATTTIME"], auth=HTTPBasicAuth(config["WATTTIME_USERNAME"], config["WATTTIME_PASSWORD"])).json()['token']
    end_time = time.time()
    while True:
        if ((end_time - start_time) / 60) >= 30: 
            watttime_token = requests.get(config["LOGIN_URL_WATTTIME"], auth=HTTPBasicAuth(config["WATTTIME_USERNAME"], config["WATTTIME_PASSWORD"])).json()['token']
        all_regions_ba = scrape_all_ba_locations(watttime_token)
        emissions = scrape_real_time_emissions_given_locations(watttime_token, all_regions_ba)
        print(emissions)
        #time.sleep(10)
        end_time = time.time()

