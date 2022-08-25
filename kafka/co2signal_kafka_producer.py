import requests
import time
import os
from dotenv import dotenv_values
import confluent_kafka
import json


emissions_producer = confluent_kafka.Producer({'bootstrap.servers':'localhost:9092'})


def retrieve_token():
    dirname = os.path.dirname
    config = dotenv_values(os.path.join(dirname(dirname(__file__)), '.env'))
    return config['CO2SIGNAL_TOKEN']


def scrape_all_country_codes(co2_token):
    country_codes_url = 'http://api.electricitymap.org/v3/zones'
    country_codes = requests.get(url=country_codes_url).json()
    return country_codes


def callback(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        #print("Message produced: %s" % (str(msg)))
        message = 'Produced message on topic {} with value of {}\n'.format(msg.topic(), msg.value().decode('utf-8'))
        print(message)

def scrape_emission_data_given_country_codes(co2_token, country_codes):
    for country_code in country_codes.keys():
        print("Scraping countryCode: {}...\n".format(country_code))
        emissions_url = "https://api.co2signal.com/v1/latest"
        headers = {'auth-token': co2_token}
        parameters = {'countryCode': '{}'.format(country_code)}
        co2_emissions_data = requests.get(url=emissions_url, headers=headers, params=parameters).json()
        if co2_emissions_data['data']['fossilFuelPercentage'] is not None:
            refined_data = {'countryCode': co2_emissions_data['countryCode'], 'data': co2_emissions_data['data'], 'units': co2_emissions_data['units'], 'zoneName': country_codes[country_code]['zoneName']}
            co2_emissions_json_data = json.dumps(refined_data)
            emissions_producer.produce('co2-topic', co2_emissions_json_data.encode('utf-8'), callback=callback)
            emissions_producer.poll(1)
        print("Sleeping...\n")
        time.sleep(120)


if __name__ == "__main__":
    start_time = end_time = time.time()
    co2_token = retrieve_token()
    while True:
        retrieved_countries_and_data = scrape_all_country_codes(co2_token)
        scrape_emission_data_given_country_codes(co2_token, retrieved_countries_and_data)
