import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
import altair as alt

url = 'https://github.com/dancosta154/Winnipesaukee_MultiRegression/blob/main/model_data/winni_reports.csv?raw=true'
df = pd.read_csv(url,index_col=0)

st.title("Winnipesaukee Fishing Reports")
st.header("Helping Billy Catch Fish")

st.text('''This website shows you a breakdown of the fish you have caught, or not caught, \nsince 2015. Select an area of the lake, then select weather conditions to see \nhow that area of the lake has fished historically.''')

st.markdown("""---""")

## Location
# create list of all locations
location = df['location'].unique()

# create sidebar with location dropdown
sidebar = st.sidebar
history = sidebar.checkbox("I want to see all the fish I've caught")

if history:
    try:
        location_selector = sidebar.selectbox(
            "Select a Location",
            location
        )

        # filter df to only records with the selected location 
        df_location = df[df['location'] == location_selector]

        ## Weather
        # get list of all weather conditions that have occurred in selected location
        mylist = [str(x) for x in df_location['weather'].unique()]
        weather = [x for x in mylist if x != 'nan']

        # create sidebar with weather dropdown
        weather_selector = sidebar.selectbox(
            "Select a Weather Condition",
            weather
        )

        # create slider with temperatures
        temp = sidebar.slider('What is the temperature?', 35, 90, 70, 1)
        temp_plus_minus = sidebar.slider("Plus or Minus Degrees", 0, 30, 30, 1)

        # create slider with wind
        wind = sidebar.slider('How windy is it?', 0, 20, 7, 2)
        wind_plus_minus = sidebar.slider("Plus or Minus Windspeed MPH", 0, 30, 30, 1)

        # filter df_location to only records with selected weather condition
        df_weather = df_location[df['weather'] == weather_selector] 
        # filter df_weather to a range of wind within selected plus_minus
        df_wind = df_weather[df_weather['wind_speed_mph'].between(wind - wind_plus_minus, wind + wind_plus_minus)]
        # filter df_wind to a range of temperatures within selected plus_minus
        df_temp = df_wind[df_wind['air_temp_f'].between(temp - temp_plus_minus, temp + temp_plus_minus)]

        ## Reporting
        # reporting about selected location 
        st.write(f"**Weather Conditions: {weather_selector.title()}, {temp}&deg;, {wind} mph winds** for **{location_selector.title()}**")
        st.write(f'This location has **{df_temp.shape[0]} records** with these weather conditions')
        st.write(f"Under these weather conditions, this location was last fished on **{df_temp['date'].max()}**")

        st.dataframe(df_temp)
        st.write(f'{len(df_temp)} records')

        ## Download Button
        # Download df to CSV
        def convert_df(df):
            return df.to_csv().encode('utf-8')

        today = date.today() # used for naming csv

        csv = convert_df(df_temp)

        st.download_button(
            'Click to download filtered table', 
            csv,
            f'winni_data_{location_selector}_{today}.csv',
            'text/csv',
            key='download-csv'
        )

        # Download df to CSV
        csv = convert_df(df)

        st.download_button(
            'Click to download table with all records', 
            csv,
            f'winni_data_{today}.csv',
            'text/csv',
            key='download-csv'
        )

        st.markdown("""---""")

        ## Pie Chart and Table associated with chart
        # creates and displays df based on user selections
        x = df.loc[(df['location'] == location_selector) & (df['weather'] == weather_selector) & (df['wind_speed_mph'].between(wind - wind_plus_minus, wind + wind_plus_minus)) & (df['air_temp_f'].between(temp - temp_plus_minus, temp + temp_plus_minus))].value_counts(['fish_type'], normalize=True).to_frame()
        x.rename(columns = {0: 'Percent_Caught'}, inplace = True)
        x.reset_index(inplace = True)
        x['fish_type'] = x['fish_type'].map(lambda x: x.title())
        x.set_index('fish_type', inplace = True)

        st.subheader('This graph provides a breakdown of fish caught by location')

        # creates pie-chart based on user selections
        fig, ax = plt.subplots()
        ax.pie(x['Percent_Caught'], 
               labels=x.index, 
               autopct='%1.1f%%',
               textprops = {'size': 'small'},
               wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
        plt.title(f'Fish Caught - {location_selector.title()} \n {weather_selector.title()} Weather Conditions')
        st.pyplot(fig)

        # Display pie-chart table
        st.dataframe(x)


        ## Bar Chart and Table associated with chart
        # creates bar-chart based on user selections
        y = df.loc[(df['location'] == location_selector) & (df['weather'] == weather_selector) & (df['wind_speed_mph'].between(wind - wind_plus_minus, wind + wind_plus_minus)) & (df['air_temp_f'].between(temp - temp_plus_minus, temp + temp_plus_minus))].groupby('month').sum()['skunked']
        z = df.loc[(df['location'] == location_selector) & (df['weather'] == weather_selector) & (df['wind_speed_mph'].between(wind - wind_plus_minus, wind + wind_plus_minus)) & (df['air_temp_f'].between(temp - temp_plus_minus, temp + temp_plus_minus))].groupby('month').count()['date']
        y = y.reset_index()
        z = z.reset_index()
        df = pd.merge(y, z, on = 'month')
        df.rename(columns={'month': 'Month', 'skunked': 'Skunked', 'date': 'Times Fished'}, inplace = True)

        # Bar Chart
        bc = alt.Chart(df).mark_bar(
            size=50
        ).encode(
            x=alt.X("Month", axis=alt.Axis(tickCount=y.shape[0], grid=False)),
            y="Skunked"
        ).properties(
            title='Skunked by Month',
            width=500,
            height=500
        ).configure_title(
            fontSize=40,
            # font='Courier',
            anchor='start',
            color='black'
        )

        st.altair_chart(bc)

        # Display bar-chart table
        st.dataframe(df)

    except:
        pass


# ----------------------------------------------------------------------------
## Where to Fish
where_to_fish = sidebar.checkbox("I don't know where to fish...")

if where_to_fish:   
    
        ## Weather
        # get list of all weather conditions that have occurred in selected location
        ml = [str(x) for x in df['weather'].unique()]
        weather_types = [x for x in ml if x != 'nan']

        # create sidebar with weather dropdown
        weather_condition = sidebar.selectbox(
            "Select a Weather Condition",
            weather_types
        )

        # create slider with temperatures
        temperature = sidebar.slider('What is the temperature?', 35, 90, 70, 1)
        temperature_plus_minus = sidebar.slider("Plus or Minus Degrees", 0, 30, 30, 1)

        # create slider with wind
        wind_speed = sidebar.slider('How windy is it?', 0, 20, 7, 2)
        wind_speed_plus_minus = sidebar.slider("Plus or Minus Windspeed MPH", 0, 30, 30, 1)

        df_where = df.loc[(df['weather'] == weather_condition) & (df['wind_speed_mph'].between(wind_speed - wind_speed_plus_minus, wind_speed + wind_speed_plus_minus)) & (df['air_temp_f'].between(temperature - temperature_plus_minus, temperature + temperature_plus_minus))]
        
        st.dataframe(df_where)
        
        hist = alt.Chart(df_where).mark_bar(
            size=30
        ).encode(
            alt.X("location", bin=False),
            y='count()'
        ).properties(
            title='Most Fished Places',
            width=800,
            height=500
        ).configure_title(
            fontSize=40,
            # font='Courier',
            anchor='start',
            color='black'
        )
        
        st.altair_chart(hist)
# ----------------------------------------------------------------------------
## Model
model = sidebar.button('Will I Catch a Fish?!?')

# if model():
    ## Put model here

    
    

## Database
# import streamlit as st
# import psycopg2

# # Initialize connection.
# # Uses st.experimental_singleton to only run once.
# @st.experimental_singleton
# def init_connection():
#     return psycopg2.connect(**st.secrets["postgres"])

# conn = init_connection()

# # Perform query.
# # Uses st.experimental_memo to only rerun when the query changes or after 10 min.
# @st.experimental_memo(ttl=600)
# def run_query(query):
#     with conn.cursor() as cur:
#         cur.execute(query)
#         return cur.fetchall()

# rows = run_query("SELECT * from mytable;")

# # Print results.
# for row in rows:
#     st.write(f"{row[0]} has a :{row[1]}:")