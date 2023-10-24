import pandas as pd 
from api_functions.wb_data import get_wb_data
from api_functions.ilo_data import get_ilo_data
from api_functions.imf_data import get_imf_data_updated

########################### SPECIFY START AND END YEAR ###############################

START_YEAR = 2000
END_YEAR = 2023

########################### SPECIFY THE WB INDICATORS NEEDED ##########################

featureMap_indicators={
    'SP.POP.TOTL': 'Population',
    'NY.GDP.PCAP.PP.KD': 'GDP per capita',
    'NY.GNP.PCAP.PP.KD': 'GNI per capita',
    'NY.GDP.MKTP.PP.KD': 'GDP, PPP (constant 2017 international $)',
    'SP.POP.GROW': 'Population Growth Rate',
    'SI.POV.GINI': 'Gini index',
}

########################### SPECIFY THE ILO INDICATORS NEEDED ##########################

# Initialize an empty dictionary to store indicators and their parameters

INDICATORS_ILO = {}

# Adding parameters for indicators (Note: online there is always an '_A' added at the end of each indicator, needs to be taken out to work)
# Indicator ids can be found here: https://ilostat.ilo.org/data/


INDICATORS_ILO['Employment'] = {'indicator': 'EMP_TEMP_SEX_AGE_NB', 'SEX': 'SEX_T', 'FREQ': 'A', 'AGE': 'AGE_YTHADULT_YGE15'}
INDICATORS_ILO['Labour force participation rate'] = {'indicator': 'EAP_DWAP_SEX_AGE_RT', 'SEX': 'SEX_T', 'FREQ': 'A', 'AGE': 'AGE_YTHADULT_YGE15'}
INDICATORS_ILO['Unemployment rate'] = {'indicator': 'UNE_DEAP_SEX_AGE_RT', 'SEX': 'SEX_T', 'FREQ': 'A', 'AGE': 'AGE_YTHADULT_YGE15'}
INDICATORS_ILO['Population in working age, female share'] = {'indicator': 'POP_2POP_SEX_AGE_NB', 'SEX': 'SEX_F', 'FREQ': 'A', 'AGE': 'AGE_YTHADULT_YGE15'}
INDICATORS_ILO['Labour force, female share'] = {'indicator': 'EAP_TEAP_SEX_AGE_NB', 'SEX': 'SEX_F', 'FREQ': 'A', 'AGE': 'AGE_YTHADULT_YGE15'}
INDICATORS_ILO['Employment, female share'] = {'indicator': 'EMP_TEMP_SEX_AGE_NB', 'SEX': 'SEX_F', 'FREQ': 'A', 'AGE': 'AGE_YTHADULT_YGE15'}
INDICATORS_ILO['Employment Public administration and defence'] = {'indicator': 'EMP_TEMP_SEX_ECO_NB', 'SEX': 'SEX_T', 'FREQ': 'A', 'ECO': 'ECO_ISIC4_O'}

# Parameters 
# Define featureMap for parameters 
featureMap_params = {
    'SEX_T': 'Total',
    'SEX_F': 'Female',
    'AGE_YTHADULT_Y15-64': 'Age (Youth, adults): 15+',
    'AGE_YTHADULT_Y15-24': 'Age (Youth, adults): 15-24', 
    'ECO_ISIC4_A': 'Economic activity (Detailed): Agriculture; forestry and fishing ~ISIC rev.4 A',
    'ECO_ISIC4_B': 'Economic activity (Detailed): Mining and quarrying ~ISIC rev.4 B',
    'ECO_ISIC4_C': 'Economic activity (Detailed): Manufacturing ~ISIC rev.4 C',
    'ECO_ISIC4_D': 'Economic activity (Detailed): Utilities ~ISIC rev.4 D; E',
    'ECO_ISIC4_F': 'Economic activity (Detailed): Construction ~ISIC rev.4 F',
    'ECO_ISIC4_G': 'Economic activity (Detailed): Wholesale and retail trade; repair of motor vehicles and motorcycles ~ISIC rev.4 G',
    'ECO_ISIC4_H': 'Economic activity (Detailed): Transport; storage and communication ~ISIC rev.4 H; J',
    'ECO_ISIC4_I': 'Economic activity (Detailed): Accommodation and food service activities ~ISIC rev.4 I',
    'ECO_ISIC4_K': 'Economic activity (Detailed): Financial and insurance activities ~ISIC rev.4 K',
    'ECO_ISIC4_L': 'Economic activity (Detailed): Real estate; business and administrative activities ~ISIC rev.4 L; M; N',
    'ECO_ISIC4_O': 'Economic activity (Detailed): Public administration and defence; compulsory social security ~ISIC rev.4 O',
    'ECO_ISIC4_P': 'Economic activity (Detailed): Education ~ISIC rev.4 P',
    'ECO_ISIC4_Q': 'Economic activity (Detailed): Human health and social work activities ~ISIC rev.4 Q',
    'ECO_ISIC4_S': 'Economic activity (Detailed): Other services ~ISIC rev.4 R; S; T; U',

}

########################### SPECIFY THE IMF INDICATORS NEEDED #########################

INDICATORS_IMF = {}
INDICATORS_IMF['Gross Domestic Product, Nominal, Domestic Currency'] = {'datasetID':'IFS','CL_FREQ':'A',
                                                                        'CL_AREA_IFS':'','CL_INDICATOR_IFS':'NGDP_XDC',
                                                                        }
INDICATORS_IMF['Exports of Goods and Services, Nominal, Domestic Currency'] = {'datasetID':'IFS','CL_FREQ':'A','CL_AREA_IFS':'',
                                                                        'CL_INDICATOR_IFS':'NX_XDC',
                                                                        }
INDICATORS_IMF['Imports of Goods and Services, Nominal, Domestic Currency'] = {'datasetID':'IFS','CL_FREQ':'A','CL_AREA_IFS':'',
                                                                        'CL_INDICATOR_IFS':'NM_XDC',
                                                                        }
INDICATORS_IMF['Prices, Consumer Price Index, All items, Index'] = {'datasetID':'IFS','CL_FREQ':'A','CL_AREA_IFS':'',
                                                                        'CL_INDICATOR_IFS':'PCPI_IX',
                                                                        }
INDICATORS_IMF['Fiscal, General Government, Revenue, 2001 Manual, Domestic Currency'] = {'datasetID':'IFS','CL_FREQ':'A',
                                                                        'CL_AREA_IFS':'','CL_INDICATOR_IFS':'GG_GR_G01_XDC',
                                                                        }
INDICATORS_IMF['Fiscal, General Government, Revenue, Tax, 2001 Manual, Domestic Currency'] = {'datasetID':'IFS','CL_FREQ':'A',
                                                                        'CL_AREA_IFS':'','CL_INDICATOR_IFS':'GG_GRT_G01_XDC',
                                                                        }
INDICATORS_IMF['Fiscal, General Government, Expense, 2001 Manual, Domestic Currency'] = {'datasetID':'IFS','CL_FREQ':'A',
                                                                        'CL_AREA_IFS':'','CL_INDICATOR_IFS':'GG_GE_G01_XDC',
                                                                        }
INDICATORS_IMF['Fiscal, General Government, Assets and Liabilities, Net Worth'] = {'datasetID':'IFS','CL_FREQ':'A',
                                                                        'CL_AREA_IFS':'','CL_INDICATOR_IFS':'GG_GANW_G01_XDC',
                                                                        }                                                                                                                                                                                                                          
INDICATORS_IMF['Current Account, Goods and Services, Net, National Currency'] = {'datasetID':'BOP','CL_FREQ':'A','CL_AREA_BOP':'',
                                                                        'CL_INDICATOR_BOP':'BGS_BP6_XDC',
                                                                        }
INDICATORS_IMF['Debt to GDP Ratio'] = {'datasetID':'HPDD','CL_FREQ':'A','CL_AREA_HPDD':'','CL_INDICATOR_HPDD':'GGXWDG_GDP',
                                                                        }




########################### RETRIEVE WB DATA ##########################

# # World Bank 
# wb_data = get_wb_data(featureMap_indicators, START_YEAR, END_YEAR)


# # ########################### MANUALLY CALCULATE GDP GROWTH ##########################

# # Step 1: Create an empty list to store new rows
# new_rows = []

# # Step 2-3: Iterate through each row in the dataframe
# for index, row in wb_data.iterrows():

#     if row['Indicator Code'] == 'NY.GDP.MKTP.PP.KD':  # Check if indicators column has the desired value
#         country = row['Country Code']
#         year = row['Year']
#         prev_year = year - 1

#         # Find the corresponding row from the previous year
#         prev_year_row = wb_data[(wb_data['Country Code'] == country) & 
#                                 (wb_data['Year'] == prev_year) & 
#                                 (wb_data['Indicator Code'] == 'NY.GDP.MKTP.PP.KD')]

#         if not prev_year_row.empty:
#                 prev_year_value = prev_year_row['Value'].values[0]
#                 current_value = row['Value']

#                 # Calculate the new value based on the formula
#                 new_value =((current_value / prev_year_value) - 1) * 100
#                 new_value = round(new_value, 2)

#                 # Create a new row with the calculated value and all other columns from the current year's row
#                 new_row = row.copy()  # Copy all columns
#                 new_row['Year'] = year
#                 new_row['Value'] = new_value
#                 new_row['Indicator'] = 'GDP Growth'
#                 new_row['Indicator Code'] = 'GDP Growth'
#                 new_rows.append(new_row)

# # Step 4-5: Append new rows to the original dataframe
# wb_data = wb_data.append(new_rows, ignore_index=True)
# # Calculate region values for the indicators and attach to df

# selected_cols  = ['Region', 'Income Group', 'Least Developed Countries (LDC)', 
#                   'Land Locked Developing Countries (LLDC)', 
#                   'Small Island Developing States (SIDS)']

# for ele in selected_cols: 
#     mean_values = wb_data.groupby([ele , 'Indicator', 'Year'])['Value'].mean().reset_index()
#     mean_values = mean_values[~(mean_values[ele] == 0)]
#     wb_data = pd.concat([wb_data, mean_values])
# wb_data.to_csv('data/pbfinance_wb.csv', index=False)

########################### RETRIEVE ILO DATA ##########################


# # ILOSTAT
# ilo_data = get_ilo_data(INDICATORS_ILO, START_YEAR, END_YEAR, featureMap_params)

# # Multiply all values in ILO dataframe by 1000 to get normal values (except LFR and UER)
# conditions = ~ilo_data['Indicator'].isin(['Labour force participation rate', 'Unemployment rate'])
# ilo_data.loc[conditions, 'Value'] = ilo_data.loc[conditions, 'Value'] * 1000

# # # # Concat dataframes and append country classifications
# # # df_pb_finance = pd.concat([wb_data, ilo_data])
# selected_cols  = ['Region', 'Income Group', 'Least Developed Countries (LDC)', 
#                   'Land Locked Developing Countries (LLDC)', 
#                   'Small Island Developing States (SIDS)']

# for ele in selected_cols: 
#     mean_values = ilo_data.groupby([ele , 'Indicator', 'Year'])['Value'].mean().reset_index()
#     mean_values = mean_values[~(mean_values[ele] == 0)]
#     ilo_data = pd.concat([ilo_data, mean_values])
# ilo_data.to_csv('data/pbfinance_ilo.csv', index=False)

# ########################### RETRIEVE IMF DATA ##########################

# # IMF 
# imf_data = get_imf_data_updated(INDICATORS_IMF)
# imf_data.to_csv('data/pbfinance_imf.csv', index=False)

