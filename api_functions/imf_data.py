# SOURCE DATA QUERY: IMF api in python: http://www.bd-econ.com/imfapi1.html
# SOURCE: https://briandew.wordpress.com/2016/05/01/machine-reading-imf-data-data-retrieval-with-python/
# SOURCE METADATA QUERY: http://www.bd-econ.com/imfapi3.html
# SOURCE: https://datahelp.imf.org/knowledgebase/articles/667681-json-restful-web-service

#BASE_URL = "http://dataservices.imf.org/REST/SDMX_JSON.svc/"
#url="http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/PGCS/A..rnna.?"
#url_metadata = "http://dataservices.imf.org/REST/SDMX_JSON.svc/GenericMetadata/PGCS/A..rnna."
#url_countries = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CodeList/CL_REF_AREA"
## url if start and end year included: http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/PGCS/A..rnna.?startPeriod=2015&endPeriod=2020

import requests 
import pandas as pd
import urllib.request
import json
#--------------------------------------IMF PARAMETERS---------------------------------------------

# Here you define the indicators you want to retrieve and assign them a name that shows up in the dataset

# featureMap_indicators = {
#     'rnna': 'Capital stock (in bil. 2011US$)',
#     'rnna_pch': 'Growth rate in total capital (%)'
# }

# # Data is currently only available between 1961-2017 (August 2023)
# START_YEAR= 2016
# END_YEAR= 2017

# # Dataset used (currently only works for one dataset at a time)
# DATASET = "PGCS"


#--------------------------------------FUNCTION---------------------------------------------

def get_imf_data(feature_map_input, start_year_input, end_year_input, dataset_input):

  # Define base url (only for PGCS dataset!)
  BASE_URL = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/"
  
  ######################### Prepare indicators and country names ############################

  country_code_list = requests.get(f"http://dataservices.imf.org/REST/SDMX_JSON.svc/CodeList/CL_Country_{dataset_input}").json()\
      ['Structure']['CodeLists']['CodeList']['Code']

  featureMap_countries = {code['@value']: code['Description']['#text'] for code in country_code_list}

  ################################### Define function ####################################

  # Define function to retrieve individual indicator from website
  def access_imf_data(indicator_id): 

    """
    Functions that takes an indicator ID as an input, accesses the indicator data from IMF 
    through the API and returns a dataframe with the data for the indicator as an output. 
    
    """
  
    # Get data from the above URL using the requests package
    data = requests.get(f"{BASE_URL}{dataset_input}/A..{indicator_id}.?startPeriod={str(start_year_input)}&endPeriod={str(end_year_input)}").json()

    # Load data into a pandas dataframe
    auxp = pd.DataFrame(data['CompactData']['DataSet']['Series'])

    # Explode the lists of dictionaries into separate rows
    auxp = auxp.explode('Obs', ignore_index=True)

    # Normalize the dictionaries into separate columns
    obs_normalized = pd.json_normalize(auxp['Obs'])

    # Merge the normalized data with the original DataFrame and drop the original list column
    df = pd.concat([auxp.drop('Obs', axis=1), obs_normalized], axis=1)
    
    return df 
  
  ##################################### Get data #######################################

  # Create an empty dataframe to store the data 
  df_full = pd.DataFrame()

  # Loop through each indicator in the dictionary and access data
  for key, value in feature_map_input.items(): 

    df_id = access_imf_data(key)

    # Attach data to dataframe 
    df_full = pd.concat([df_full, df_id])

  
  ##################################### Process data #######################################

  # Drop, rename and reorder columns columns 
  df_full.drop(columns={'@FREQ', '@UNIT_MULT', '@TIME_FORMAT'}, inplace=True)
  df_full.rename(columns={'@REF_AREA': 'WEO Country Code', '@INDICATOR': 'Indicator Code', '@TIME_PERIOD': 'Year', '@OBS_VALUE': 'Value'}, inplace=True)
  df_full.to_csv('temp1.csv')
  # Add country name column
  df_full['Country'] = df_full['WEO Country Code'].map(featureMap_countries)

  # Drop all rows where the country code cannot be converted into int (those are regions)
  df_full = df_full[df_full['WEO Country Code'].apply(lambda x: isinstance(x, (int, float)) or (isinstance(x, str) and x.isnumeric()))]
  df_full.to_csv('temp2.csv')
  # Make sure all columns are the right data type and rounded
  df_full[['WEO Country Code', 'Year']] = df_full[['WEO Country Code', 'Year']].astype(int)
  df_full['Value'] = df_full['Value'].astype(float).round(2)

  # Add column of indicator names
  df_full['Indicator'] = df_full['Indicator Code'].map(feature_map_input)

  # Reorder columns
  df_full = df_full[['WEO Country Code', 'Year', 'Indicator Code', 'Indicator', 'Value']]

  # Add country and region columns
  df_country_codes = pd.read_csv('country_classifications/country_codes.csv')
  df_country_codes.rename(columns={'ISO-alpha3 Code': 'Country Code', 'Region Name': 'Region', 'Sub-region Name': 'Sub-region'}, inplace=True)
  df_full = pd.merge(df_full, df_country_codes, on=['WEO Country Code'], how="left")
  
  # Drop all regions and entries that are not countries
  df_full = df_full.dropna(subset=['Country'])

  # Rearrange and drop unnecessary columns
  df_full = df_full[['Country Code', 'Country', 'Indicator Code', 
                       'Indicator', 'Year', 'Value', 'Region', 'Sub-region', 'Income Group',
                       'Least Developed Countries (LDC)', 'Land Locked Developing Countries (LLDC)',
                       'Small Island Developing States (SIDS)']]
  
  # Save dataframe as csv file 
  # Specify decimal because otherwise German Excel gets confused
  #df_full.to_excel('data/imf_data.xlsx',index=False)

  return df_full


def get_imf_indicator_data(dimension_map_input, start_year_input, end_year_input):
  """This is to get particular indicator data from IMF"""

  # Define base url and extract all params from dimesnion 
  BASE_URL = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/"
  area_code_name = list(dimension_map_input.keys())[2]
  area_codeID = dimension_map_input[area_code_name]  
  datasetID = dimension_map_input['datasetID']
  indicatorID = dimension_map_input[f'CL_INDICATOR_{datasetID}']
  freq = dimension_map_input['CL_FREQ']
  
  ######################### Prepare indicators and country names ############################

  area_code_list = requests.get(f"http://dataservices.imf.org/REST/SDMX_JSON.svc/CodeList/{area_code_name}").json()\
      ['Structure']['CodeLists']['CodeList']['Code']

  featureMap_areas = {code['@value']: code['Description']['#text'] for code in area_code_list}
  ##### prepare URL and get data #########

  url = f"{BASE_URL}{datasetID}/{freq}.{area_codeID}.{indicatorID}.?startPeriod={str(start_year_input)}&endPeriod={str(end_year_input)}"
  data = requests.get(url).json()
  # Load data into a pandas dataframe
  auxp = pd.DataFrame(data['CompactData']['DataSet']['Series'])
  # Explode the lists of dictionaries into separate rows
  auxp = auxp.explode('Obs', ignore_index=True)

  # Normalize the dictionaries into separate columns
  obs_normalized = pd.json_normalize(auxp['Obs'])
  # Merge the normalized data with the original DataFrame and drop the original list column
  df = pd.concat([auxp.drop('Obs', axis=1), obs_normalized], axis=1)

  # Drop, rename and reorder columns columns 
  # df.drop(columns={'@FREQ', '@UNIT_MULT', '@TIME_FORMAT'}, inplace=True)
  df.rename(columns={'@REF_AREA': 'WEO Country Code', '@INDICATOR': 'Indicator Code', '@TIME_PERIOD': 'Year', '@OBS_VALUE': 'Value'}, inplace=True)
  # Add country name column
  df['Country'] = df['WEO Country Code'].map(featureMap_areas)

    # Add country and region columns
  df_country_codes = pd.read_csv('country_classifications/country_codes.csv')
  df_country_codes.rename(columns={'ISO-alpha3 Code': 'Country Code', 'Region Name': 'Region', 'Sub-region Name': 'Sub-region'}, inplace=True)
  df = pd.merge(df, df_country_codes, on=['WEO Country Code'], how="left")
  
  temp = get_dataset_structure(datasetID)
  if temp:
    out_file = open(f"country_classification/{datasetID}.json", "w")
    json.dump(temp, out_file, indent = 6)
    out_file.close()

    
  return df 


def get_dataset_structure(datasetID):
    # we try first requests library, if json decoding fails we try urllib
    # if urllib also fails we try just report the error, rememeber this is not
    # time determinsitic thing, as due to internet issue or server issue we can 
    # get bad request repsonse or any other server error.
    try:
    # response  = urllib.request.urlopen(f"http://dataservices.imf.org/REST/SDMX_JSON.svc/DataStructure/{code}").read()
        schema_structure = requests.get(f"http://dataservices.imf.org/REST/SDMX_JSON.svc/DataStructure/{datasetID}").json()
    except:
        print(datasetID, 'Request failed, trying urllib')
        try:
            response  = urllib.request.urlopen(f"http://dataservices.imf.org/REST/SDMX_JSON.svc/DataStructure/{datasetID}").read()
            schema_structure = json.loads(response.decode('utf-8'))
        except Exception as e:
            print(e)
            return None

def get_imf_data_updated(indicators_map):

  ##################################### Get all IMF data #######################################

  # Create an empty dataframe to store the data 
  df_full = pd.DataFrame()

  # Loop through each indicator in the dictionary and access data
  for key, value in indicators_map.items(): 

    df_id = get_imf_indicator_data(value)
    df_id['indicator_name'] = key

    # Attach data to dataframe 
    df_full = pd.concat([df_full, df_id])

  
  # ##################################### Process data #######################################

  # # Drop, rename and reorder columns columns 
  # df_full.drop(columns={'@FREQ', '@UNIT_MULT', '@TIME_FORMAT'}, inplace=True)
  # df_full.rename(columns={'@REF_AREA': 'WEO Country Code', '@INDICATOR': 'Indicator Code', '@TIME_PERIOD': 'Year', '@OBS_VALUE': 'Value'}, inplace=True)
  
  # # Add country name column
  # df_full['Country'] = df_full['WEO Country Code'].map(featureMap_areas)

  # # Drop all rows where the country code cannot be converted into int (those are regions)
  # df_full = df_full[df_full['WEO Country Code'].apply(lambda x: isinstance(x, (int, float)) or (isinstance(x, str) and x.isnumeric()))]

  # # Make sure all columns are the right data type and rounded
  # df_full[['WEO Country Code', 'Year']] = df_full[['WEO Country Code', 'Year']].astype(int)
  # df_full['Value'] = df_full['Value'].astype(float).round(2)

  # # Add column of indicator names
  # df_full['Indicator'] = df_full['Indicator Code'].map(feature_map_input)

  # # Reorder columns
  # df_full = df_full[['WEO Country Code', 'Year', 'Indicator Code', 'Indicator', 'Value']]

  # # Add country and region columns
  # df_country_codes = pd.read_csv('country_classifications/country_codes.csv')
  # df_country_codes.rename(columns={'ISO-alpha3 Code': 'Country Code', 'Region Name': 'Region', 'Sub-region Name': 'Sub-region'}, inplace=True)
  # df_full = pd.merge(df_full, df_country_codes, on=['WEO Country Code'], how="left")
  
  # # Drop all regions and entries that are not countries
  # df_full = df_full.dropna(subset=['Country'])

  # # Rearrange and drop unnecessary columns
  # df_full = df_full[['Country Code', 'Country', 'Indicator Code', 
  #                      'Indicator', 'Year', 'Value', 'Region', 'Sub-region', 'Income Group',
  #                      'Least Developed Countries (LDC)', 'Land Locked Developing Countries (LLDC)',
  #                      'Small Island Developing States (SIDS)']]
  
  # # Save dataframe as csv file 
  # # Specify decimal because otherwise German Excel gets confused
  # #df_full.to_excel('data/imf_data.xlsx',index=False)

  return df_full

#print(get_imf_data(featureMap_indicators, START_YEAR, END_YEAR, DATASET))
