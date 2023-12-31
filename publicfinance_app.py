import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots

# Git checkout
# Use full screen 
st.set_page_config(layout="wide")


#---------------------------------- LOAD DATA AND PARAMETERS ---------------------------------#

# Create import function with cache (cache so data is only loaded once)
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

# Load data 
df_combined = load_data("data/pbfinance.csv")
df_hdr = load_data("data/hdr.csv")

# Get a country, region and indicator list
df_countries = df_combined['Country'].unique().tolist()
df_indicators = df_combined['Indicator'].unique().tolist()
df_regions = df_combined['Region'].unique().tolist()
df_subregion = df_combined['Sub-region'].unique().tolist()
df_sub_region = df_regions + df_subregion

# Turn years into int (str necessary first because Streamlit)
df_combined = df_combined.dropna(subset=['Year'])
df_combined['Year'] = df_combined['Year'].astype(str)
df_combined['Year'] = df_combined['Year'].astype(float).astype(int)

#------------------------------ Functions  ------------------------------------#


# Data Selection 
def get_filtered_data(df,country_selec, start_year_selec, end_year_selec, indicator_selec):

    """
    Function takes the user selection of the dashboard as an input and retrieves the
    corresponding data from the dataset. The output is a filtered dataframe. 

    """

    # Turn country selection into list if not list 
    if isinstance(country_selec, str):
        country_selec = [country_selec]

    # Create a dataframe with all years and indicators first
    ## This is necessary to add the missing years with "None" values
    df_empty = pd.DataFrame([(year, indicator, country) 
                            for year in range(start_year_selec, end_year_selec+1)
                            for indicator in indicator_selec
                            for country in country_selec],
                            columns=['Year', 'Indicator', 'Country'])

    
    # Retrieve the selected data from df
    df_fltr = df[(df['Country'].isin(country_selec)) & 
                       (df['Year'] >= start_year_selec) & 
                       (df['Indicator'].isin(indicator_selec)) &
                       (df['Year'] <= end_year_selec)]
    
    ## Merge 
    df_merged = pd.merge(df_empty, df_fltr, on=['Year', 'Indicator', 'Country'], how='left')

    ## Fill other columns 
    df_merged['Indicator Code'] = df_merged.groupby('Indicator')['Indicator Code'].apply(lambda x: x.fillna(method='ffill').fillna(method='bfill'))

    for col in ['Country Code', 'Region', 'Sub-region', 'Income Group', 'Least Developed Countries (LDC)', 'Land Locked Developing Countries (LLDC)', 'Small Island Developing States (SIDS)']:
        df_merged[col] = df_merged.groupby('Country')[col].apply(lambda x: x.fillna(method='ffill').fillna(method='bfill'))

    # Turn year column into datetime format

    return df_merged

# Year Selection 
def get_years(country_input,df): 

    """
    Takes a country as an input and retrieves the corresponding minimum and maximum year
    available. This can be used to adjust the year slider. 

    """
    if country_input == None:
        return 2000, 2022
    else:
        start_year_country = int(df[df['Country'] == country_input]['Year'].min())
        end_year_country = int(df[df['Country'] == country_input]['Year'].max())
        return start_year_country, end_year_country
    
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')
df_csv = convert_df(df_combined)

# To get HDR and INCOME stats fo countries
def get_peerstats(country_list, end_year):
    
    placeholder = {}
    for country in country_list:
        df1 = df_combined[(df_combined.Country == country) & (df_combined.Year == end_year)]
        placeholder[country] = {}            
        placeholder[country]['Income Group'] = df1['Income Group'].unique()[0]
        df1 = df_hdr[df_hdr.Country == country]
        placeholder[country]['HDI rank (2021)'] = df1['HDI rank (2021)'].values[0]
    return placeholder

#---------------------------------------- SIDEBAR ---------------------------------
with st.sidebar:
    # upload and example doc
    choice = st.sidebar.radio(label = 'Select the Option',
                            help = " If you want to understand what is possible with tool use guided mode \
                            else try explorer mode.", 
                            options = ('Guided','Explorer'), 
                            horizontal = True)
    

    df_countries.remove("Germany")
    df_countries.insert(0,"Germany") 

    selected_country = st.sidebar.selectbox(
            label="Choose country of interest",
            options= df_countries,
            )

    # DESCRIPTION REGIONS/PEER COUNTRIES
    st.sidebar.caption("""If you want to compare the values of the chosen country
                    to peer countries, please make a selection below.""")
    
    # REGION INPUT WIDGET
    selected_peer = st.sidebar.multiselect(
        "Choose countries to compare",
        df_countries
        )
    
    START_YEAR, END_YEAR = get_years(selected_country, df_combined)
    if selected_country != None:
        selected_years = st.sidebar.slider(
            "Select the range",
            START_YEAR, END_YEAR, (START_YEAR,END_YEAR-1),
            )
        selected_start_year = selected_years[0]
        selected_end_year = selected_years[1]
    else:
        selected_start_year = 2000
        selected_end_year = 2022

    if selected_country != None:
        check_competitors = get_peerstats(selected_peer+[selected_country],END_YEAR)

    st.sidebar.download_button(label="Click here to download data as csv",
                        data=df_csv, 
                        file_name='data.csv')
    
    st.sidebar.header("")

    # INFO BOX
    st.sidebar.info("""Please note that this dashboard is a prototype. 
                    Users are advised that the tool may contain errors, 
                    bugs, or limitations and should be used with caution 
                    and awareness of potential risks, and the developers 
                    make no warranties or guarantees regarding its performance, 
                    reliability, or suitability for any specific purpose.""")

# # TITLE
#     add_title = st.sidebar.title("Customize your data")
#     if choice == 'WB':
#         df_countries = df_wb_countries
#     elif choice == 'ILO' :
#         df_countries = df_ilo_countries
#     else:
#         df_countries = df_imf_countries



# df_wb = load_data("data/pbfinance_wb.csv")
# df_ilo = load_data("data/pbfinance_ilo.csv")
# df_imf = load_data("data/pbfinance_imf.csv")

# Get a country, region and indicator list
# df_wb_countries = df_wb['Country'].unique().tolist()
# df_wb_indicators = df_wb['Indicator'].unique().tolist()
# df_wb_regions = df_wb['Region'].unique().tolist()
# df_wb_subregion = df_wb['Sub-region'].unique().tolist()
# df_wb_sub_region = df_wb_regions + df_wb_subregion

# df_ilo_countries = df_ilo['Country'].unique().tolist()
# df_ilo_indicators = df_ilo['Indicator'].unique().tolist()
# df_ilo_regions = df_ilo['Region'].unique().tolist()
# df_ilo_subregion = df_ilo['Sub-region'].unique().tolist()
# df_ilo_sub_region = df_ilo_regions + df_ilo_subregion

# df_imf_countries = df_imf['Country'].unique().tolist()
# df_imf_indicators = df_imf['Indicator'].unique().tolist()
# df_imf_regions = df_imf['Region'].unique().tolist()
# df_imf_subregion = df_imf['Sub-region'].unique().tolist()
# df_imf_sub_region = df_imf_regions + df_imf_subregion




# df_wb['Year'] = df_wb['Year'].astype(str)
# df_wb['Year'] = df_wb['Year'].astype(int)
# df_ilo['Year'] = df_ilo['Year'].astype(str)
# df_ilo['Year'] = df_ilo['Year'].astype(int)
# df_imf = df_imf.dropna(subset=['Year'])
# df_imf['Year'] = df_imf['Year'].astype(str)
# df_imf['Year'] = df_imf['Year'].astype(float).astype(int)
# df_imf['Year'] = df_imf['Year'].astype(int)

# Define start and end year 
# def get_years(df):
#     df = df['Year'].unique().tolist()
#     START_YEAR = min(df)
#     END_YEAR = min(df)
#     return START_YEAR, END_YEAR






# DOWNLOAD WIDGET 

# Create a csv version of the dataframe (cache so it doesn't rerun)


# wb_csv = convert_df(df_wb)
# ilo_csv = convert_df(df_ilo)
# imf_csv = convert_df(df_imf)




#     # PEER COUNTRY INPUT WIDGET
#     #selected_region = st.sidebar.multiselect(
#     #   "Choose regions for comparison",
#     #  df_sub_region
#     #  )

#     # START AND END YEAR SLIDER 

#     # # Update based on data availability for chosen country 
#     if choice == 'WB':
#         START_YEAR, END_YEAR = get_years(selected_country, df_wb)
#     elif choice == 'ILO':
#         START_YEAR, END_YEAR = get_years(selected_country, df_ilo)
#     else:
#         START_YEAR, END_YEAR = get_years(selected_country, df_imf)


#     # Widget
#     selected_years = st.sidebar.slider(
#         "Select the range",
#         START_YEAR, END_YEAR, (START_YEAR,END_YEAR-1),
#         )
    
#     # Add empty space to create some distance 
#     st.sidebar.header("")
#     if choice == 'WB':
#         st.sidebar.download_button(label="Click here to download data as csv",
#                         data=wb_csv, 
#                         file_name='data_wb.csv')
#     elif choice == 'ILO' :
#         st.sidebar.download_button(label="Click here to download data as csv",
#                         data=ilo_csv, 
#                         file_name='data_ilo.csv')
#     else:
#         st.sidebar.download_button(label="Click here to download data as csv",
#                         data=imf_csv, 
#                         file_name='data_imf.csv')



    


# #---------------------------------------- MAIN PAGE --------------------------------------------

# # Add a title and intro text
if choice == 'Guided':
    st.title("Public Finance Dashboard")

    st.write("""
            Explore a comprehensive production dashboard that provides a holistic view of key employment indicators. 
            This interactive platform synthesizes diverse metrics, offering insights into job market trends, labor 
            force participation, and economic vitality. With intuitive visualizations and data-driven analysis, gain 
            a deeper understanding of workforce dynamics and make informed decisions for the future.
            """)
    st.write("")
    if selected_country == None : #len(selected_peer) == 0
        st.warning("Please Select One Country and atleast 1 peer couuntry for better analysis")
    else:
        
        st.header("A. General country context indicators")
        st.caption("Selected Countries")
        c1, c2 = st.columns([1,1])
        with c1:
            st.write('**HDI 2021 Rank**')
            for country in check_competitors.keys():
                st.write('{}: `{}`'.format(country,check_competitors[country]['HDI rank (2021)']))
        with c2:
            st.write('**Income Group**')
            for country in check_competitors.keys():
                st.write('{}: `{}`'.format(country,check_competitors[country]['Income Group']))
                    

    # if len(selected_peer) == 0:
    #     st.warning("Please Select atleast 1 peer country for better analysis")
    # else:
        ############ ROW 1 ###################################################################33
        st.subheader("Population")
        
        #### Explanatory text box 1
        st.markdown("""<div style="text-align: justify;">The population statistic gives the size of the population 
                    of the country and its recent development. The population dynamics (growth rate) are 
                    relevant for economic growth (see GDP per capita below) and are the outcome of mortality, 
                    fertility, migration and underlying factors. </div>""", unsafe_allow_html=True
        )
                
        col1, col2, col3 = st.columns([1,0.02,1])
        with col1:
            chart1_data = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
                                        ['Population'])
            
            chart1_data = chart1_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')

            # Configure plot
            fig = px.line(chart1_data,
                            x="Year", 
                            y="Value",   
                            color='Country',
                            title='Chart 1 - Population',
                            hover_name="Value",
                            color_discrete_sequence=px.colors.qualitative.Plotly
                            )

            # Move legend 
            fig.update_layout(legend=dict(
                # orientation="h",
                yanchor="bottom",
                y=-0.5,
                xanchor="left",
                x=0.01
                ))

            # Display graph
            st.plotly_chart(fig, use_container_width=True)
                
        with col3: 
            
        # Get data
            chart2_data = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
                                    ['Population Growth Rate'])
            chart2_data = chart2_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')

                # Configure plot
            fig = px.line(chart2_data,
                            x="Year", 
                            y="Value",   
                            color='Country',
                            title='Chart 2 - Population Growth Rate',
                            hover_name="Value",
                            color_discrete_sequence=px.colors.qualitative.Plotly
                            )

                # Move legend 
            fig.update_layout(legend=dict(
                # orientation="h",
                yanchor="bottom",
                y=-0.5,
                xanchor="left",
                x=0.01
                ))
                
            st.plotly_chart(fig, use_container_width=True)

        st.caption('Data Sources: World Development Indicators (WDI)')

        st.write("")
    ########### ROW 2 ###################################3
        st.subheader("GDP/GNI Per Capita (nominal)")
        
        #### Explanatory text box 1
        st.markdown("""<div style="text-align: justify;">GDP per capita is a measure 
                    of a country’s total annual domestic output, divided by population 
                    size. In other words, it constitutes a (statistical) average of GDP 
                    per person. Together with the Human Development Index, it 
                    may provide a hint at the country’s average </div>""", unsafe_allow_html=True
                            )

        col1, col2, col3 = st.columns([1,0.02,1])
        with col1:
            chart3_data = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
                                        ['GDP per capita','GNI per capita'])
            chart3_data = chart3_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')

            # Configure plot
            fig = make_subplots()
            subfig1  =  px.line(chart3_data[chart3_data.Indicator == 'GDP per capita'],
                        x="Year", 
                        y="Value",
                        line_group='Country',
                        color='Indicator',
                        title='Chart 3 - GDP and Inequality',
                        hover_name="Value",
                        color_discrete_sequence=px.colors.qualitative.Plotly
                        )
                        
            
            subfig2 =   px.line(chart3_data[chart3_data.Indicator == 'GNI per capita'],
                        x="Year", 
                        y="Value",
                        line_group='Country',
                        color='Indicator',
                        hover_name="Value",
                        color_discrete_sequence=px.colors.qualitative.Plotly
                        )
            # subfig2.update_traces(yaxis="y2")

            fig.add_traces(subfig1.data + subfig2.data)

            fig.update_layout(legend=dict(
                    # orientation="h",
                    yanchor="bottom",
                    y=-0.5,
                    xanchor="left",
                    x=0.01
                    ),
                    title_text = 'Chart 3 - GDP & GNI per capita')
            fig.layout.xaxis.title="Year"
            fig.layout.yaxis.title="Value"

            # fig.update_yaxes(title_text="<b>GDP</b> Indicator Value", secondary_y=False)
            # fig.update_yaxes(title_text="<b>GINI Index</b> value", secondary_y=True)
            fig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))

                
            st.plotly_chart(fig, use_container_width=True)
                
        with col3: 
            
        # Get data
            chart4_data = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
                                    ['GDP, PPP (constant 2017 international $)'])
            chart4_data = chart4_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')

            # Configure plot
            fig = px.line(chart4_data,
                            x="Year", 
                            y="Value",   
                            color='Country',
                            title='Chart 4 - GDP, PPP (constant 2017 international $)',
                            hover_name="Value",
                            color_discrete_sequence=px.colors.qualitative.Plotly
                            )

                # Move legend 
            fig.update_layout(legend=dict(
                # orientation="h",
                yanchor="bottom",
                y=-0.5,
                xanchor="left",
                x=0.01
                ))
                
            st.plotly_chart(fig, use_container_width=True)

        st.caption('Data Sources: World Development Indicators (WDI)')
        
        st.write("------------")
    # ########## ROW 3 #########################################
        st.header("B. Public finance indicators ")
        

        col1, col2, col3 = st.columns([1,0.02,1])
        with col1:
            st.subheader("Revenue")
        
            #### Explanatory text box 1
            st.markdown("""<div style="text-align: justify;">Government revenue is made up
                        of tax revenue and non-tax revenue (includes social security
                        contributions, grants, property income, sales, fees, among others). 
                        General government refers to all tiers of government and 
                        excludes public corporations.A low level of tax revenues (relative to GDP) may 
                        indicate a low capacity of the state to sustainably contribute to achieving 
                        the SDGs (Addis Ababa Action Agenda, Addis Tax Initiative Declarations).  </div>""", unsafe_allow_html=True
                                )
            chart5_data = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
                                        ['Fiscal, General Government, Revenue, 2001 Manual, Domestic Currency',
                                        'Fiscal, General Government, Revenue, Tax, 2001 Manual, Domestic Currency'])
            chart5_data.replace({'Fiscal, General Government, Revenue, 2001 Manual, Domestic Currency':'Revenue',
                                        'Fiscal, General Government, Revenue, Tax, 2001 Manual, Domestic Currency':'Tax Revenue',
                                        }, inplace= True)
            chart5_data = chart5_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')

            # Configure plot
            fig = make_subplots()
            subfig1  =  px.line(chart5_data[chart5_data.Indicator == 'Revenue'],
                        x="Year", 
                        y="Value",
                        line_group='Country',
                        color='Indicator',
                        hover_name="Value",
                        color_discrete_sequence=px.colors.qualitative.Plotly
                        )
                        
            
            subfig2 =   px.line(chart5_data[chart5_data.Indicator == 'Tax Revenue'],
                        x="Year", 
                        y="Value",
                        line_group='Country',
                        color='Indicator',
                        hover_name="Value",
                        color_discrete_sequence=px.colors.qualitative.Plotly
                        )
            # subfig2.update_traces(yaxis="y2")

            fig.add_traces(subfig1.data + subfig2.data)

            fig.update_layout(legend=dict(
                    # orientation="h",
                    yanchor="bottom",
                    y=-0.5,
                    xanchor="left",
                    x=0.01
                    ),
                    title_text = 'Chart 5 - Revenue and Tax Revenue ')
            fig.layout.xaxis.title="Year"
            fig.layout.yaxis.title="Value"

            # fig.update_yaxes(title_text="<b>GDP</b> Indicator Value", secondary_y=False)
            # fig.update_yaxes(title_text="<b>GINI Index</b> value", secondary_y=True)
            fig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))

                
            st.plotly_chart(fig, use_container_width=True)
                
        with col3: 
            
        # Get data
            st.subheader("Expenditure")
        
            #### Explanatory text box 1
            st.markdown("""<div style="text-align: justify;">General government expenses
                        serve two broad economic responsibilities: provide selected
                        goods and services to the community and redistribute income
                        and wealth. Expenses exceeding revenues need to be 
                        financed, e.g., through borrowing.</div>

                        """, unsafe_allow_html=True
                                )
            chart6_data = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
                                    ['Fiscal, General Government, Expense, 2001 Manual, Domestic Currency'])
            chart6_data.replace({'Fiscal, General Government, Expense, 2001 Manual, Domestic Currency':'Expenditure'},
                            inplace= True)
            chart6_data = chart6_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')
            st.write("")
            st.write("")
            st.write("")
            # Configure plot
            fig = px.line(chart6_data,
                            x="Year", 
                            y="Value",   
                            color='Country',
                            title='Chart 6 - Expenditure',
                            hover_name="Value",
                            color_discrete_sequence=px.colors.qualitative.Plotly
                            )

                # Move legend 
            fig.update_layout(legend=dict(
                # orientation="h",
                yanchor="bottom",
                y=-0.5,
                xanchor="left",
                x=0.01
                ))
                
            st.plotly_chart(fig, use_container_width=True)

        st.caption('Data Sources: International Monetary Fund (IMF)')
        st.write("")

        ############### ROW 4 ########################################################

        chart7_data = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
                            ['Prices, Consumer Price Index, All items, Index'])
        chart7_data.replace({'Prices, Consumer Price Index, All items, Index':'Consumer Price Index'},
                            inplace= True)
        chart7_data = chart7_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')
        col1, col2, col3 = st.columns([1,0.02,1])
        with col1:
            st.subheader("Inflation")
            #### Explanatory text box 1
            st.markdown("""<div style="text-align: justify;">The annual inflation rate measures
                        the yearly change in a general price index. Inflation reduces 
                        the purchasing power of money; the inflation rate can be used to 
                        account for price level changes in the development of nominal measures 
                        by translating them to real values (e.g. nominal versus real GDP).</div>
                        <br>
                        <div style="text-align: justify;">Inflation has multiple 
                        potential causes (e.g. related to expansionary monetary policy)
                        and affects government and private finances in several ways. 
                        Both high and very low levels of inflation warrant attention 
                        to underlying political, economic and financial dynamics and 
                        their consequences.  </div>""", unsafe_allow_html=True)
        with col3:
                # Configure plot
            fig = px.line(chart7_data,
                            x="Year", 
                            y="Value", 
                            color='Country',
                            title='Chart 7 - Consumer Price Index',
                            hover_name="Value",
                            color_discrete_sequence=px.colors.qualitative.Plotly
                            )

            # Move legend 
            fig.update_layout(legend=dict(
                # orientation="h",
                yanchor="bottom",
                y=-0.5,
                xanchor="left",
                x=0.01
                ))

            # Display graph
            st.plotly_chart(fig, use_container_width=True)
            st.caption('Data Sources: International Monetary Fund (IMF)')
        st.write("")

        ############### ROW 5 ########################################################

        chart8_data = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
                            ['Labour force participation rate','Unemployment rate'])
        # chart7_data.replace({'Prices, Consumer Price Index, All items, Index':'Consumer Price Index'},
        #                     inplace= True)
        chart8_data = chart8_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')
        col1, col2, col3 = st.columns([1,0.02,1])
        with col1:
            st.subheader("Unemployment")
            #### Explanatory text box 1
            st.markdown("""<div style="text-align: justify;">Official unemployment rates 
                        measure the proportion of the working age population that is 
                        looking for but cannot find formal work (according to certain criteria). 
                        High unemployment is typically associated with poverty, 
                        inequality and a loss of output and productive resources. 
                        For more detail on employment and unemployment.
                        [Unemployment Dashboard](https://employment-dashboard.streamlit.app).</div>""", 
                        unsafe_allow_html=True)
        with col3:
                # Configure plot
            fig = make_subplots()
            subfig1  =  px.line(chart8_data[chart8_data.Indicator == 'Labour force participation rate'],
                        x="Year", 
                        y="Value",
                        line_group='Country',
                        color='Indicator',
                        hover_name="Value",
                        color_discrete_sequence=px.colors.qualitative.Plotly
                        )
                        
            
            subfig2 =   px.line(chart8_data[chart8_data.Indicator == 'Unemployment rate'],
                        x="Year", 
                        y="Value",
                        line_group='Country',
                        color='Indicator',
                        hover_name="Value",
                        color_discrete_sequence=px.colors.qualitative.Plotly
                        )
            # subfig2.update_traces(yaxis="y2")

            fig.add_traces(subfig1.data + subfig2.data)

            fig.update_layout(legend=dict(
                    # orientation="h",
                    yanchor="bottom",
                    y=-0.5,
                    xanchor="left",
                    x=0.01
                    ),
                    title_text = 'Chart 8 - Unemployment')
            fig.layout.xaxis.title="Year"
            fig.layout.yaxis.title="Value"

            # fig.update_yaxes(title_text="<b>GDP</b> Indicator Value", secondary_y=False)
            # fig.update_yaxes(title_text="<b>GINI Index</b> value", secondary_y=True)
            fig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))

                
            st.plotly_chart(fig, use_container_width=True)
            st.caption('Data Sources: International Labour Organization (ILO)')
        st.write("")

        ############### ROW 6 ########################################################

        chart9_data = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
                            ['Debt to GDP Ratio'])
        chart9_data = chart9_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')
        col1, col2, col3 = st.columns([1,0.02,1])
        with col1:
            st.subheader("Debt Rate")
            #### Explanatory text box 1
            st.markdown("""<div style="text-align: justify;">An increase in the 
                        public debt/government debt to GDP ratio indicates an 
                        increase in public liabilities relative to gross domestic output. 
                        Rising debt rates may be associated with decreasing debt 
                        sustainability and the capacity to access new financing. 
                        Details depend on several factors including financing 
                        conditions, type of debt, capacity to repay (e. g. DRM).</div>""", unsafe_allow_html=True)
        with col3:
                # Configure plot
            fig = px.line(chart9_data,
                            x="Year", 
                            y="Value", 
                            color='Country',
                            title='Chart 9 - Debt to GDP Ratio',
                            hover_name="Value",
                            color_discrete_sequence=px.colors.qualitative.Plotly
                            )

            # Move legend 
            fig.update_layout(legend=dict(
                # orientation="h",
                yanchor="bottom",
                y=-0.5,
                xanchor="left",
                x=0.01
                ))

            # Display graph
            st.plotly_chart(fig, use_container_width=True)
            st.caption('Data Sources: International Monetary Fund (IMF)')
        st.write("----------------------------------------------")

        ##################### Row 7 #########################################################
        st.subheader("More Indicators Plot")
        chart10_data = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
                            ['Exports of Goods and Services, Nominal, Domestic Currency',
                            'Imports of Goods and Services, Nominal, Domestic Currency'])
        chart10_data.replace({'Exports of Goods and Services, Nominal, Domestic Currency':'Exports',
                            'Imports of Goods and Services, Nominal, Domestic Currency':'Imports'},
                            inplace= True)
        chart10_data = chart10_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')
        col1, col2, col3 = st.columns([1,0.02,1])
        with col1:
            fig = make_subplots()
            subfig1  =  px.line(chart10_data[chart10_data.Indicator == 'Exports'],
                        x="Year", 
                        y="Value",
                        line_group='Country',
                        color='Indicator',
                        hover_name="Value",
                        color_discrete_sequence=px.colors.qualitative.Plotly
                        )
                        
            
            subfig2 =   px.line(chart10_data[chart10_data.Indicator == 'Imports'],
                        x="Year", 
                        y="Value",
                        line_group='Country',
                        color='Indicator',
                        hover_name="Value",
                        color_discrete_sequence=px.colors.qualitative.Plotly
                        )
            # subfig2.update_traces(yaxis="y2")

            fig.add_traces(subfig1.data + subfig2.data)

            fig.update_layout(legend=dict(
                    # orientation="h",
                    yanchor="bottom",
                    y=-0.5,
                    xanchor="left",
                    x=0.01
                    ),
                    title_text = 'Chart 10 - Exports & Imports')
            fig.layout.xaxis.title="Year"
            fig.layout.yaxis.title="Value"

            # fig.update_yaxes(title_text="<b>GDP</b> Indicator Value", secondary_y=False)
            # fig.update_yaxes(title_text="<b>GINI Index</b> value", secondary_y=True)
            fig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))

                
            st.plotly_chart(fig, use_container_width=True)
            st.caption('Data Sources: International Monetary Fund (IMF)')

        with col3:
                # Configure plot
            chart11_data = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
                        ['Gini index'])

            chart11_data = chart11_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')    
            fig = px.line(chart11_data,
                            x="Year", 
                            y="Value", 
                            color='Country',
                            title='Chart 11 - Gini index',
                            hover_name="Value",
                            color_discrete_sequence=px.colors.qualitative.Plotly
                            )

            # Move legend 
            fig.update_layout(legend=dict(
                # orientation="h",
                yanchor="bottom",
                y=-0.5,
                xanchor="left",
                x=0.01
                ))

            # Display graph
            st.plotly_chart(fig, use_container_width=True)
            st.caption('Data Sources: World Development Indicators (WDI)')
    

    ####################### Explorer TAB ###########################3
else:

    st.header(" This is your Playgroud ")
    Indicators = list(df_combined.Indicator.unique())

    selected_indicators = st.multiselect("Choose the labels for your plot",
                                         options= Indicators
                                         )
    # title_txt = st.text_area(
    # "Give title to your Graph",
    # "Default",
    # )
    count_of_indicators = len(selected_indicators)
    filtered_data = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
                            selected_indicators)

    filtered_data = filtered_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')
    
    plots_holder = []
    for i in range(count_of_indicators):
        plots_holder.append(px.line(filtered_data[filtered_data.Indicator == selected_indicators[i]],
                        x="Year", 
                        y="Value",
                        line_group='Country',
                        color='Indicator',
                        hover_name="Value",
                        color_discrete_sequence=px.colors.qualitative.Plotly
       
                        ))
        
    if count_of_indicators ==2:
        fig = make_subplots(specs=[[{"secondary_y": True}]])  
        plots_holder[1].update_traces(yaxis="y2")
    else:
        fig = make_subplots()  

    fig_data = ()
    for i in plots_holder:
        fig_data = fig_data + i.data
    fig.add_traces(fig_data)

    fig.update_layout(legend=dict(
            # orientation="h",
            yanchor="bottom",
            y=-0.5,
            xanchor="left",
            x=0.01
            ))
    fig.layout.xaxis.title="Year"
    fig.layout.yaxis.title="Value"

    if count_of_indicators == 2:
        fig.update_yaxes(title_text="<b>{}</b>".format(selected_indicators[0]), secondary_y=False)
        fig.update_yaxes(title_text="<b>{}</b> value".format(selected_indicators[1]), secondary_y=True)

    fig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))

            
    st.plotly_chart(fig, use_container_width=True)
        

    ############# ROW 8 ########################################################
    # 
    # chart10_data = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
    #                     ['Current Account, Goods and Services, Net, National Currency',
    #                      'Fiscal, General Government, Assets and Liabilities, Net Worth'])
    # # chart10_data.replace({'Prices, Consumer Price Index, All items, Index':'Consumer Price Index'},
    # #                     inplace= True)
    # chart10_data = chart10_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')
    # col1, col2, col3 = st.columns([1,0.02,1])
    # with col1:
        
    #     fig = px.line(chart10_data[chart10_data.Indicator == 'Current Account, Goods and Services, Net, National Currency'],
    #                     x="Year", 
    #                     y="Value", 
    #                     color='Country',
    #                     title='Chart 10 - Current Account, Goods and Services, Net',
    #                     hover_name="Value",
    #                     color_discrete_sequence=px.colors.qualitative.Plotly
    #                     )

    #     # Move legend 
    #     fig.update_layout(legend=dict(
    #         # orientation="h",
    #         yanchor="bottom",
    #         y=-0.5,
    #         xanchor="left",
    #         x=0.01
    #         ))

    #     # Display graph
    #     st.plotly_chart(fig, use_container_width=True)
    #     #### Explanatory text box 1
    #     # st.markdown("""<div style="text-align: justify;">An increase in the 
    #     #             public debt/government debt to GDP ratio indicates an 
    #     #             increase in public liabilities relative to gross domestic output. 
    #     #             Rising debt rates may be associated with decreasing debt 
    #     #             sustainability and the capacity to access new financing. 
    #     #             Details depend on several factors including financing 
    #     #             conditions, type of debt, capacity to repay (e. g. DRM).</div>""", unsafe_allow_html=True)
    # with col3:
    #         # Configure plot
    #     fig = px.line(chart10_data[chart10_data.Indicator == 'Fiscal, General Government, Assets and Liabilities, Net Worth'],
    #                     x="Year", 
    #                     y="Value", 
    #                     color='Country',
    #                     title='Chart 11 - Assets and Liabilities, Net Worth',
    #                     hover_name="Value",
    #                     color_discrete_sequence=px.colors.qualitative.Plotly
    #                     )

    #     # Move legend 
    #     fig.update_layout(legend=dict(
    #         # orientation="h",
    #         yanchor="bottom",
    #         y=-0.5,
    #         xanchor="left",
    #         x=0.01
    #         ))

    #     # Display graph
    #     st.plotly_chart(fig, use_container_width=True)
    # st.caption('Data Sources: International Monetary Fund (IMF)')
    # st.write("")
   

    ############################# ROW 10 ###########################3

        
    #     fig = px.line(chart10_data[chart10_data.Indicator == 'Current Account, Goods and Services, Net, National Currency'],
    #                     x="Year", 
    #                     y="Value", 
    #                     color='Country',
    #                     title='Chart 10 - Current Account, Goods and Services, Net',
    #                     hover_name="Value",
    #                     color_discrete_sequence=px.colors.qualitative.Plotly
    #                     )

    #     # Move legend 
    #     fig.update_layout(legend=dict(
    #         # orientation="h",
    #         yanchor="bottom",
    #         y=-0.5,
    #         xanchor="left",
    #         x=0.01
    #         ))

    #     # Display graph
    #     st.plotly_chart(fig, use_container_width=True)
    #     #### Explanatory text box 1
    #     # st.markdown("""<div style="text-align: justify;">An increase in the 
    #     #             public debt/government debt to GDP ratio indicates an 
    #     #             increase in public liabilities relative to gross domestic output. 
    #     #             Rising debt rates may be associated with decreasing debt 
    #     #             sustainability and the capacity to access new financing. 
    #     #             Details depend on several factors including financing 
    #     #             conditions, type of debt, capacity to repay (e. g. DRM).</div>""", unsafe_allow_html=True)
    # with col3:
    #         # Configure plot
    #     st.subheader('Fiscal, General Government, Assets and Liabilities, Net Worth')
    #     fig = px.line(chart10_data[chart10_data.Indicator == 'Fiscal, General Government, Assets and Liabilities, Net Worth'],
    #                     x="Year", 
    #                     y="Value", 
    #                     color='Country',
    #                     title='Chart 11 - Assets and Liabilities, Net Worth',
    #                     hover_name="Value",
    #                     color_discrete_sequence=px.colors.qualitative.Plotly
    #                     )

    #     # Move legend 
    #     fig.update_layout(legend=dict(
    #         # orientation="h",
    #         yanchor="bottom",
    #         y=-0.5,
    #         xanchor="left",
    #         x=0.01
    #         ))

        # Display graph
        # st.plotly_chart(fig, use_container_width=True)


    


    #     chart3_data = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
    #                                 ['GDP per capita','GNI per capita'])
         
        
    #     chart3_data = chart3_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')
    #     fig = make_subplots(specs=[[{"secondary_y": True}]])

    #     # Add traces
    #     subfig1  =  px.line(chart3_data_1,
    #                 x="Year", 
    #                 y="Value",
    #                 line_group='Country',
    #                 color='Indicator',
    #                 title='Chart 3 - GDP and Inequality',
    #                 hover_name="Value",
    #                 color_discrete_sequence=px.colors.qualitative.Plotly
    #                 )
                    
        
    #     subfig2 =   px.line(chart3_data_2,
    #                 x="Year", 
    #                 y="Value",
    #                 line_group='Country',
    #                 color='Indicator',
    #                 hover_name="Value",
    #                 color_discrete_sequence=px.colors.qualitative.Plotly
    #                 )
    #     subfig2.update_traces(yaxis="y2")

    #     fig.add_traces(subfig1.data + subfig2.data)

    #     fig.update_layout(legend=dict(
    #             # orientation="h",
    #             yanchor="bottom",
    #             y=-0.5,
    #             xanchor="left",
    #             x=0.01
    #             ))
    #     fig.update_yaxes(title_text="<b>GDP</b> Indicator Value", secondary_y=False)
    #     fig.update_yaxes(title_text="<b>GINI Index</b> value", secondary_y=True)
    #     fig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
            
    #     st.plotly_chart(fig, use_container_width=True)

    #     st.caption('Data Sources: World Development Indicators (WDI)')








    #     tab1, tab2, tab3 = st.tabs(["Country Data", "Unemployment Comparison", "Labour Force Comparison"])

        # # Configure plot
        # fig = px.line(chart3_data,
        #                 x="Year", 
        #                 y="Value", 
                          
        #                 color='Country',
        #                 title='Chart 3 - GDP per capita',
        #                 hover_name="Value",
        #                 color_discrete_sequence=px.colors.qualitative.Plotly
        #                 )

        # # Move legend 
        # fig.update_layout(legend=dict(
        #     # orientation="h",
        #     yanchor="bottom",
        #     y=-0.5,
        #     xanchor="left",
        #     x=0.01
        #     ))

    #     # Display graph
    #     st.plotly_chart(fig, use_container_width=True)
            
    # with col3: 
        
    # # Get data
    #     chart4_data = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
    #                             ['GNI per capita'])
    #     chart4_data = chart4_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')

    #         # Configure plot
    #     fig = px.line(chart4_data,
    #                     x="Year", 
    #                     y="Value",   
    #                     color='Country',
    #                     title='Chart 4 - GNI per capita',
    #                     hover_name="Value",
    #                     color_discrete_sequence=px.colors.qualitative.Plotly
    #                     )

    #         # Move legend 
    #     fig.update_layout(legend=dict(
    #         # orientation="h",
    #         yanchor="bottom",
    #         y=-0.5,
    #         xanchor="left",
    #         x=0.01
    #         ))
            
    #     st.plotly_chart(fig, use_container_width=True)

    # st.caption('Data Sources: World Development Indicators (WDI)')
#     col1, col2, col3 = st.columns([1,0.02,1])
#     with col1:
#         st.subheader("GDP and Inequality")
#         st.markdown("""<div style="text-align: justify;">Gross Domestic Product (GDP) per capita is a widely used
#                         indicator of a country's economic performance and development level. 
#                     It is calculated by dividing the total annual domestic output 
#                     of a country by its population size, thus providing a statistical 
#                     average of GDP per person. This metric offers valuable insights 
#                     into a country's standard of living and economic health, 
#                     especially when considered in conjunction with other indicators 
#                     such as the Human Development Index.</div> 
#                     <br>
#                     <div style="text-align: justify;">The growth rate of GDP per capita is 
#                     generally regarded as the primary measure of a country's economic 
#                     growth. It reflects the increase in the average income of a country's 
#                     citizens over time, which is a key factor in determining their standard
#                     of living. A steadily growing GDP per capita is often seen as an 
#                     indicator of a robust economy, as it suggests that the country is producing
#                     more goods and services per person, thereby improving people's 
#                     purchasing power and overall quality of life.<div>
#                     <br>
#                     <div style="text-align: justify;">
#                     However, it is important to note that GDP per 
#                     capita has its limitations as a measure of a 
#                     country's economic well-being. For instance, 
#                     it does not take into account factors such as 
#                     income inequality, poverty rates, and environmental
#                     degradation, which can significantly impact a 
#                     country's overall development.<div>""",  unsafe_allow_html=True)
#     with col3:
#         chart3_data_1 = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
#                                     ['GDP per capita', 'GNI per capita'])
#         # 'GDP, PPP (constant 2017 international $)','GDP per capita', 'Gini index'
#         chart3_data_1 = chart3_data_1.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')

#         chart3_data_2 = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
#                                     ['Gini index'])
       
#         # 'GDP, PPP (constant 2017 international $)','GDP per capita', 
#         chart3_data_2 = chart3_data_2.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')


#     # Create figure with secondary y-axis
#         fig = make_subplots(specs=[[{"secondary_y": True}]])

#         # Add traces
#         subfig1  =  px.line(chart3_data_1,
#                     x="Year", 
#                     y="Value",
#                     line_group='Country',
#                     color='Indicator',
#                     title='Chart 3 - GDP and Inequality',
#                     hover_name="Value",
#                     color_discrete_sequence=px.colors.qualitative.Plotly
#                     )
                    
        
#         subfig2 =   px.line(chart3_data_2,
#                     x="Year", 
#                     y="Value",
#                     line_group='Country',
#                     color='Indicator',
#                     hover_name="Value",
#                     color_discrete_sequence=px.colors.qualitative.Plotly
#                     )
#         subfig2.update_traces(yaxis="y2")

#         fig.add_traces(subfig1.data + subfig2.data)

#         fig.update_layout(legend=dict(
#                 # orientation="h",
#                 yanchor="bottom",
#                 y=-0.5,
#                 xanchor="left",
#                 x=0.01
#                 ))
#         fig.update_yaxes(title_text="<b>GDP</b> Indicator Value", secondary_y=False)
#         fig.update_yaxes(title_text="<b>GINI Index</b> value", secondary_y=True)
#         fig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
            
#         st.plotly_chart(fig, use_container_width=True)

#     st.caption('Data Sources: World Development Indicators (WDI)')

#     ####################### ROW 3 ####################################################################
#     col1, col2, col3 = st.columns([1,0.02,1])
#     with col1:
#         st.subheader("Revenue and Expenditure")
#         st.markdown("""<div style="text-align: justify;">Gross Domestic Product (GDP) per capita is a widely used
#                         indicator of a country's economic performance and development level. 
#                     It is calculated by dividing the total annual domestic output 
#                     of a country by its population size, thus providing a statistical 
#                     average of GDP per person. This metric offers valuable insights 
#                     into a country's standard of living and economic health, 
#                     especially when considered in conjunction with other indicators 
#                     such as the Human Development Index.</div> 
#                     <br>
#                     <div style="text-align: justify;">The growth rate of GDP per capita is 
#                     generally regarded as the primary measure of a country's economic 
#                     growth. It reflects the increase in the average income of a country's 
#                     citizens over time, which is a key factor in determining their standard
#                     of living. A steadily growing GDP per capita is often seen as an 
#                     indicator of a robust economy, as it suggests that the country is producing
#                     more goods and services per person, thereby improving people's 
#                     purchasing power and overall quality of life.<div>
#                     <br>
#                     """,  unsafe_allow_html=True)
    
#     with col3:
#         chart4_data = get_filtered_data(df_combined,[selected_country], selected_start_year, selected_end_year, 
#                                     ['Fiscal, General Government, Revenue, 2001 Manual, Domestic Currency',
#        'Fiscal, General Government, Revenue, Tax, 2001 Manual, Domestic Currency',
#        'Fiscal, General Government, Expense, 2001 Manual, Domestic Currency'])
#         # 'GDP, PPP (constant 2017 international $)','GDP per capita', 'Gini index'
#         chart4_data = chart4_data.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')

#         fig = px.line(chart4_data,
#                         x="Year", 
#                         y="Value",   
#                         color='Indicator',
#                         title='Chart 4 - Revenue and Expenditure',
#                         hover_name="Value",
#                         color_discrete_sequence=px.colors.qualitative.Plotly
#                         )

#             # Move legend 
#         fig.update_layout(legend=dict(
#             # orientation="h",
#             yanchor="bottom",
#             y=-0.5,
#             xanchor="left",
#             x=0.01
#             ))
            
#         st.plotly_chart(fig, use_container_width=True)

#         st.caption('Data Sources: International Monetary Fund (IMF)')

#         # chart3_data_2 = get_filtered_data(df_combined,[selected_country] + selected_peer, selected_start_year, selected_end_year, 
#         #                             ['Gini index'])
       
#         # # 'GDP, PPP (constant 2017 international $)','GDP per capita', 
#         # chart3_data_2 = chart3_data_2.groupby(['Indicator'],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')


    
        
#     # fig.add_trace(
#     #     px.Scatter(x =  name="yaxis data"),
#     #     secondary_y=False,
#     # )

#     # fig.add_trace(
#     #     go.Scatter(x=[2, 3, 4], y=[4, 5, 6], name="yaxis2 data"),
#     #     secondary_y=True,
#     # )

#     # # Add figure title
#     # fig.update_layout(
#     #     title_text="Double Y Axis Example"
#     # )
#     #     fig = make_subplots(specs=[[{"secondary_y": True}]])


    



#         # Display subheading 
        

# # # Add the info box
# # with st.expander("ℹ️ - About the data sources", expanded=False):
# #     st.write(
# #         """
# #         It inlcudes IMF, Worldbanl, ILO and Human Devlopment Report data
# #         """)
    

# # # ############################ ROW 1 ###################################

# # # # Display subheading 
# # # st.subheader("Everyone is talking about  Gross Domestic Product (GDP) - but what does it actually mean? ")

# # Configure columns





#     # ### Group data by year
    

# #     # Caption graph
# #     

# # # # ### GRAPH AND TEXT 1 ###

# # # # with col1: 
    
# # # #     # Text 
# # # #     st.markdown("""<div style="text-align: justify;">The best way to understand the concept of GDP is probably
# # # #                  by breaking it down into its components. Click through the tabs to explore the 
# # # #                 different components.</div>""",unsafe_allow_html=True)
    
# # # #     # Tabs 
# # # #     tab1, tab2, tab3, tab4, tab5 = st.tabs(["Product", "Services", "Goods", "Domestic", "Gross"])

# # # #     with tab1: 
# # # #         st.markdown("""<div style="text-align: justify;">Let us start from the back and look at the term 
# # # #                         <strong>"Product"</strong> first: 
# # # #                         The GDP measures all final goods and services that have been produced within a defined time 
# # # #                         period (typically a year).  If this year, 
# # # #                         someone sells a house that has been build two years ago, it will not be part of 
# # # #                         this year's GDP. Also, if someone resells a car that has been manufactured and that 
# # # #                         she has bought this year it will only be counted once into the GDP since reselling 
# # # #                         is not producing.</div>""",unsafe_allow_html=True)

# # # #     with tab2: 
# # # #         st.markdown("""<div style="text-align: justify;">Examples for <strong>"Services"</strong> are a 
# # # #                         haircut, entertainment, a taxi ride, consultancy, a craft activity, renting out an apartment, 
# # # #                         formal schooling, or health care. They all have in common that you cannot store them.</div>""",unsafe_allow_html=True)
    
# # # #     with tab3: 
# # # #         st.markdown("""<div style="text-align: justify;"><strong>"Goods"</strong>, in turn, can be stored as they are 
# # # #                         tangible things such as food, clothes, books, computers, mobiles, machines in general, and even 
# # # #                         buildings.  What does the term <strong>final</strong> mean? A car is a final good – but the steel and 
# # # #                         glass a car manufacturer buys to produce 
# # # #                         the car are not final goods. That is: All the goods and services which directly end up 
# # # #                         in a product are not final goods. Machines, however, are final goods since they are used 
# # # #                         to produce goods, but do not directly end up in them.</div>""",unsafe_allow_html=True)

# # # #     with tab4: 
# # # #             st.markdown(""" <div style="text-align: justify;">Finally, <strong>"domestic"</strong> refers to the fact
# # # #                         that only those final goods and services are part of the GDP that are produced 
# # # #                         in the considered country. Whether a domestic factory belongs to a foreign owner or 
# # # #                         a domestic one does not matter - it only matters that the good is produced in the regarded country.</div>""", unsafe_allow_html=True)

# # # with col1:

# # #     # Display subheading 
# # #     st.subheader("Everyone is talking about  Gross Domestic Product (GDP) - but what does it actually mean? ")
 
   
# # #     #### Explanatory text box 1
# # #     st.markdown("""<div style="text-align: justify;">The best way to understand GDP is probably
# # #                 by breaking it down into its components. Let us start with <strong>"Product"</strong>: The GDP measures all final goods and services that 
# # #                 have been produced within a defined time period (typically a year).  If this year, 
# # #                 someone sells a house that has been build two years ago, it will not be part of 
# # #                 this year's GDP. Also, if someone resells a car that has been manufactured and that 
# # #                 she has bought this year it will only be counted once into the GDP since reselling 
# # #                 is not producing.Examples for <strong>"services"</strong> are a haircut, entertainment, a taxi ride, 
# # #                 consultancy, a craft activity, renting out an apartment, formal schooling, or health care. 
# # #                 They all have in common that you cannot store them.</div> 
# # #                 <br>
# # #                 <div style="text-align: justify;"><strong>"Goods"</strong>, in turn, can be stored as they are tangible things such as food, clothes, books, 
# # #                 computers, mobiles, machines in general, and even buildings.  What does the term <strong>final</strong> 
# # #                 mean? A car is a final good – but the steel and glass a car manufacturer buys to produce 
# # #                 the car are not final goods. That is: All the goods and services which directly end up 
# # #                 in a product are not final goods. Machines, however, are final goods since they are used 
# # #                 to produce goods, but do not directly end up in them.</div>  
# # #                 <br>
# # #                 <div style="text-align: justify;"><strong>"Domestic"</strong>: Only those final goods and services are part of the GDP that are produced 
# # #                 in the considered country. Whether a domestic factory belongs to a foreign owner or 
# # #                 a domestic one does not matter - it only matters that the good is produced in the regarded country.</div>""", unsafe_allow_html=True
# # #     )
        
# # #     st.header("")

# # # #### Graph 1

# # # with col3: 

# # #     # Create tabs 
# # #     tab1, tab2 = st.tabs(['GDP per capita', 'GDP'])

# # #     with tab1: 

# # #         # Get data
# # #         chart1_data = get_filtered_data([selected_country] + selected_peer, selected_start_year, selected_end_year, ['GDP per capita'])

# # #         # ### Group data by year
# # #         chart1_data = chart1_data.groupby([chart1_data.Indicator],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')

# # #         # Configure plot
# # #         fig = px.line(chart1_data,
# # #                         x="Year", 
# # #                         y="Value",   
# # #                         color='Country',
# # #                         title='Chart 1 - GDP per capita',
# # #                         hover_name="Value",
# # #                         color_discrete_sequence=px.colors.qualitative.Plotly
# # #                         )

# # #         # # Move legend 
# # #         # fig.update_layout(legend=dict(
# # #         #     # orientation="h",
# # #         #     yanchor="bottom",
# # #         #     y=1.05,
# # #         #     xanchor="left",
# # #         #     x=0.01
# # #         #     ))

# # #         # Display graph
# # #         st.plotly_chart(fig, use_container_width=True)

# # #         # Caption graph
# # #         st.caption('Data Sources: World Development Indicators (WDI)')
    
# # #     with tab2: 
        
# # #         # Get data
# # #         chart2_data = get_filtered_data([selected_country] + selected_peer, selected_start_year, selected_end_year, ['GDP'])

# # #         # ### Group data by year
# # #         chart2_data = chart2_data.groupby([chart2_data.Indicator],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')

# # #         # Configure plot
# # #         fig = px.line(chart2_data,
# # #                         x="Year", 
# # #                         y="Value",   
# # #                         color='Country',
# # #                         title='Chart 2 - GDP',
# # #                         hover_name="Value",
# # #                         color_discrete_sequence=px.colors.qualitative.Plotly
# # #                         )

# # #         # # Move legend 
# # #         # fig.update_layout(legend=dict(
# # #         #     # orientation="h",
# # #         #     yanchor="bottom",
# # #         #     y=1.05,
# # #         #     xanchor="left",
# # #         #     x=0.01
# # #         #     ))

# # #         # Display graph
# # #         st.plotly_chart(fig, use_container_width=True)

# # #         # Caption graph
# # #         st.caption('Data Sources: World Development Indicators (WDI)')


# # # ############################# ROW 2 ###################################

# # # # Text 
# # # st.subheader("So how do people actually manage that their economies grow?")

# # # # Configure columns
# # # col1, col2, col3 = st.columns([1,0.02,1])

# # # with col1: 
    
# # #     st.markdown("""<div style="text-align: justify;">In chart 1, we can see that 
# # #                 the economies of a lot of countries (if selected) tend to grow. That is, 
# # #                 year by year most countries manage to establish new "high scores" in terms 
# # #                 of the total value of final goods and services they have produced in that 
# # #                 year (GDP). So how do people actually manage that their economies grow?</div>  
# # #                 <br>
# # #                 <div style="text-align: justify;">Production depends on three so-called factors of production: Economists 
# # #                 call the first land – which is a synonym for natural resources. They 
# # #                 provide the material input for all the goods and services that an economy 
# # #                 produces. Obviously, the material boundaries of our planet set an upper 
# # #                 limit for material growth on earth.</div>   
# # #                 <br>
# # #                 <div style="text-align: justify;">The second factor is capital: Capital are all those products that can 
# # #                 be used to produce further products and do not end up in them: machines, 
# # #                 tools and equipment, patents, buildings, a country's infrastructure. The 
# # #                 more of these products are available, the more goods and services an economy 
# # #                 can produce. Or, in turn, without any factories there will not be any industrial 
# # #                 products. Hence, increasing the capital stock is one way to make an economy grow.
# # #                 <br>
# # #                 <div style="text-align: justify;">The last and third factor of production is labour. Labour is provided by people. 
# # #                 That means, if the population is growing, there are more people around who can work. 
# # #                 Thus, usually, an economy grows when its population is growing (for more 
# # #                 information on employment, check out our other dashboards).</div>
# # #                 </div>""", unsafe_allow_html=True
# # #         )    
# # # with col3:
                
# # #     st.markdown("""<div style="text-align: justify;">The last and third factor of production is labour. Labour is provided by people. 
# # #                 That means, if the population is growing, there are more people around who can work. 
# # #                 Thus, usually, an economy grows when its population is growing (for more 
# # #                 information on employment, check out our other dashboards).</div>  
# # #                 <br>
# # #                 <div style="text-align: justify;">Besides the pure quantity of people and capital items around, the quality of 
# # #                 both factors matters as well: If people are better educated and trained they 
# # #                 will, most likely, be able to work more efficient and will consequently produce 
# # #                 more per hour than before. In this context, one also often refers to the 
# # #                 term “human capital”. What education is to humans, innovation (or science) is 
# # #                 to capital: If the same number of machines and production processes suddenly 
# # #                 function with a more efficient technology, due to an innovation, then again 
# # #                 production increases – thus, the economy grows.</div>
# # #                 <br>
# # #                 <div style="text-align: justify;">What education is to humans, innovation (or science) is to capital: If the same number of machines 
# # #                 and production processes suddenly function with a more efficient technology, due to an innovation, 
# # #                 then again production increases – thus, the economy grows.</div>""", unsafe_allow_html=True
# # #         )

# # # # Configure columns
# # # col1, col2, col3 = st.columns([1,1,1])

# # # ### Chart Capital ###

# # # with col1: 
    
# # #   # Get data
# # #     chart3_data = get_filtered_data([selected_country] + selected_peer, selected_start_year, selected_end_year, ['Total population'])

# # #     # ### Group data by year
# # #     chart3_data = chart3_data.groupby([chart3_data.Indicator],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')

# # #     # Configure plot
# # #     fig = px.line(chart3_data,
# # #                     x="Year", 
# # #                     y="Value",   
# # #                     color='Country',
# # #                     title='Chart 3 - Total Population',
# # #                     hover_name="Value",
# # #                     color_discrete_sequence=px.colors.qualitative.Plotly
# # #                     )

# # #     # Move legend 
# # #     fig.update_layout(legend=dict(
# # #         # orientation="h",
# # #         yanchor="bottom",
# # #         y=-0.5,
# # #         xanchor="left",
# # #         x=0.01
# # #         ))

# # #     # Display graph
# # #     st.plotly_chart(fig, use_container_width=True)

# # #     # Caption graph
# # #     st.caption('Data Sources: World Development Indicators (WDI)')


# # # ### Chart Capital ###

# # # with col2: 
    
# # #   # Get data
# # #     chart4_data = get_filtered_data([selected_country] + selected_peer, selected_start_year, selected_end_year, ['Capital stock (in bil. 2011US$)'])

# # #     # ### Group data by year
# # #     chart4_data = chart4_data.groupby([chart4_data.Indicator],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')

# # #     # Configure plot
# # #     fig = px.line(chart4_data,
# # #                     x="Year", 
# # #                     y="Value",   
# # #                     color='Country',
# # #                     title='Chart 4 - Capital stock (in bil. 2011US$)',
# # #                     hover_name="Value",
# # #                     color_discrete_sequence=px.colors.qualitative.Plotly
# # #                     )

# # #     # Move legend 
# # #     fig.update_layout(legend=dict(
# # #         # orientation="h",
# # #         yanchor="bottom",
# # #         y=-0.5,
# # #         xanchor="left",
# # #         x=0.01
# # #         ))

# # #     # Display graph
# # #     st.plotly_chart(fig, use_container_width=True)

# # #     # Caption graph
# # #     st.caption('International Monetary Fund (IMF)')

# # #     ### Chart Capital ###

# # # with col3: 
    
# # #   # Get data
# # #     chart5_data = get_filtered_data([selected_country] + selected_peer, selected_start_year, selected_end_year, ['Population Growth Rate', 'GDP Growth', 'Growth rate in total capital (%)'])

# # #     # ### Group data by year
# # #     chart5_data = chart5_data.groupby([chart5_data.Indicator],group_keys=False,sort=False).apply(pd.DataFrame.sort_values,'Year')

# # #     # Configure plot
# # #     fig = px.line(chart5_data,
# # #                     x="Year", 
# # #                     y="Value",   
# # #                     color='Indicator',
# # #                     title="Chart 5 - Your Country's Annual Growth Rates [%]: GDP, Population & Capital",
# # #                     hover_name="Value",
# # #                     color_discrete_sequence=px.colors.qualitative.Plotly
# # #                     )

# # #     # Move legend 
# # #     fig.update_layout(legend=dict(
# # #         # orientation="h",
# # #         yanchor="bottom",
# # #         y=-0.5,
# # #         xanchor="left",
# # #         x=0.01
# # #         ))

# # #     # Display graph
# # #     st.plotly_chart(fig, use_container_width=True)

# # #     # Caption graph
# # #     st.caption('International Monetary Fund (IMF)')