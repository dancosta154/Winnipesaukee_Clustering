import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date

col1, col2 = st.columns(2)

st.title("Winnipesaukee Fishing Reports")
st.header("Helping Billy Catch Fish")

st.text('''This website shows you a breakdown of the fish you have caught, or not caught, \nsince 2015. Select an area of the lake, then select weather conditions to see \nhow that area of the lake has fished historically.''')

url = 'https://github.com/dancosta154/Winnipesaukee_MultiRegression/blob/main/model_data/winni_reports.csv?raw=true'
df = pd.read_csv(url,index_col=0)

st.subheader('The following table shows **all** records')
df

# Download df to CSV
today = date.today() # used for naming csv

def convert_df(df):
    return df.to_csv().encode('utf-8')

csv = convert_df(df)

st.download_button(
    'Click to download table', 
    csv,
    f'winni_data_{today}.csv',
    'text/csv',
    key='download-csv'
)

st.markdown("""---""")

# create list of all locations
location = df['location'].unique()

# create sidebar with location dropdown

sidebar = st.sidebar
location_selector = sidebar.selectbox(
    "Select a Location",
    location
)

# filter df to only records with the selected location 
df_location = df[df['location'] == location_selector]

# get list of all weather conditions that have occurred in selected location
mylist = [str(x) for x in df_location['weather'].unique()]
weather = [x for x in mylist if x != 'nan']

# create sidebar with weather dropdown
weather_selector = sidebar.selectbox(
    "Select a Weather Condition",
    weather
)

# create slider with temperatures
temp = sidebar.slider('What is the temperature?', 35, 90, 66, 1)
temp_plus_minus = sidebar.slider("Plus or Minus Degrees", 0, 10, 5, 1)

# create slider with wind
wind = sidebar.slider('How windy is it?', 0, 20, 7, 2)
wind_plus_minus = sidebar.slider("Plus or Minus Windspeed MPH", 0, 10, 3, 1)

# filter df_location to only records with selected weather condition
df_weather = df_location[df['weather'] == weather_selector] 
# filter df_weather to a range of wind within selected plus_minus
df_wind = df_weather[df_weather['wind_speed_mph'].between(wind - wind_plus_minus, wind + wind_plus_minus)]
# filter df_wind to a range of temperatures within selected plus_minus
df_temp = df_wind[df_wind['air_temp_f'].between(temp - temp_plus_minus, temp + temp_plus_minus)]

st.subheader('This section reflects the location and weather selections')

col1, col2 = st.columns(2)

with col1:
    st.write(f"**{location_selector.title()} Statistics**")
    st.write(f'This location has **{df_temp.shape[0]} records**') # Commenting out because I think this shows all records at location, not unique dates
    st.write(f"This location was **last fished on {df_temp['date'].max()}**")
with col2:
    st.write(f"**Weather Conditions: {weather_selector.title()}, {temp}&deg;, {wind} mph winds**")
    st.write(f'This location has **{df_temp.shape[0]} records** with these weather conditions')
    st.write(f"Under these weather conditions, this location was last fished on **{df_temp['date'].max()}**")

# reporting about selected location 
# st.markdown(f"This location has been fished **{len(df_location['date'].unique())} days**") # I think this is accurate, but opens a can of words - so commenting out for now
# st.markdown(f'This location has been fished **{df_wind.shape[0]} days** with **{weather_selector} conditions** and **wind of {wind}**, plus or minus **{wind_plus_minus} mph**')

st.dataframe(df_temp)
st.write(f'{len(df_temp)} records')

# Download df to CSV
csv = convert_df(df_temp)

st.download_button(
    'Click to download table', 
    csv,
    f'winni_data_{location_selector}_{today}.csv',
    'text/csv',
    key='download-csv'
)

st.markdown("""---""")

# creates and displays df based on user selections
x = df.loc[(df['location'] == location_selector) & (df['weather'] == weather_selector)].value_counts(['fish_type'], normalize=True).to_frame()
x.rename(columns = {0: 'Percent_Caught'}, inplace = True)
x.reset_index(inplace = True)
x['fish_type'] = x['fish_type'].map(lambda x: x.title())
x.set_index('fish_type', inplace = True)

st.subheader('This graph provides a breakdown of fish caught by location')
# creates pie-chart based on user selections
st.caption('Pie chart does not account for temperature or wind speed')
fig, ax = plt.subplots()
ax.pie(x['Percent_Caught'], 
       labels=x.index, 
       autopct='%1.1f%%',
       textprops = {'size': 'small'},
       wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
plt.title(f'Fish Caught - {location_selector.title()} \n {weather_selector.title()} Weather Conditions')
st.pyplot(fig)

st.dataframe(x)

st.subheader('Will I get skunked tomorrow?')

st.button('Will I Catch a Fish Tomorrow?!')


st.markdown("""---""")
st.markdown("""---""")
st.markdown("""---""")

import psycopg2

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

rows = run_query("SELECT * from mytable;")

# Print results.
for row in rows:
    st.write(f"{row[0]} has a :{row[1]}:")