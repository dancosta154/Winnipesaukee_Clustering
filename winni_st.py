import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date
import altair as alt

html_temp = """
    <div style="background:#025246 ;padding:10px">
    <h2 style="color:white;text-align:center;"> Winnipesaukee Fishing Reports </h2>
    </div>
    """
st.markdown(html_temp, unsafe_allow_html = True)

url = 'https://github.com/dancosta154/Winnipesaukee_MultiRegression/blob/main/model_data/winni_reports.csv?raw=true'
df = pd.read_csv(url,index_col=0)

## Location
# create list of all locations & wind directions
location = df['location'].unique()
wind_directions = df['wind_dir'].unique()

# create sidebar with location dropdown
sidebar = st.sidebar
history = sidebar.checkbox("I want to see all the fish I've caught")

if history:
    
    st.markdown("""---""")
    
    st.text("""This page shows you a history of all of the records from your notebook! Each record 
in the table is an entry from the notebook; however, that doesn't mean one entry per 
day... each fish is it's own entry as the data is different for that particular 
fish (fish type, length, depth caught, etc.) 

Filtering the selections on the left will shrink the table and graphs below to only 
records that match the selections you choose. Have fun!""")
    
    st.markdown("""---""")

    location_selector = sidebar.selectbox(
        "Select a Location",
        location
    )

    # filter df to only records with the selected location 
    df_location = df[df['location'] == location_selector]

    ## Weather
    # get list of all weather conditions that have occurred in selected location
    mylist = [str(x) for x in df_location['weather'].unique()]
    weather = [x for x in mylist if x != 'no_weather_recorded']

    # create sidebar with weather dropdown
    weather_selector = sidebar.selectbox(
        "Select a Weather Condition",
        np.sort(weather)
    )

    # create slider with temperatures
    temp = sidebar.slider('Select a Temperature', 35, 90, 70, 1)
    temp_plus_minus = sidebar.slider("Plus or Minus Degrees", 0, 30, 30, 1)

    # create slider with wind
    wind = sidebar.slider('Select a Wind Speed', 0, 20, 7, 2)
    wind_plus_minus = sidebar.slider("Plus or Minus Windspeed MPH", 0, 30, 30, 1)

    # filter df_location to only records with selected weather condition
    df_weather = df_location[df['weather'] == weather_selector] 
    # filter df_weather to a range of wind within selected plus_minus
    df_wind = df_weather[df_weather['wind_speed_mph'].between(wind - wind_plus_minus, wind + wind_plus_minus)]
    # filter df_wind to a range of temperatures within selected plus_minus
    df_temp = df_wind[df_wind['air_temp_f'].between(temp - temp_plus_minus, temp + temp_plus_minus)]
    # filter df_temp to a wind direction
    # df_wind_dir = df_temp[df_temp['wind_dir'] == wind_dir_selector]

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

    # creates pie-chart based on user selections
    fig, ax = plt.subplots()
    ax.pie(x['Percent_Caught'], 
           labels=x.index, 
           autopct='%1.1f%%',
           textprops = {'size': 'small'},
           wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
    plt.title(f'Fish Caught {location_selector.title()}: \n {weather_selector.title()} Weather Conditions', fontdict={'fontsize': 8})
    st.pyplot(fig)

    # Display pie-chart table
    st.dataframe(x)
    
    st.markdown("""---""")
 
    

    ## Bar Chart and Table associated with chart
    # creates bar-chart based on user selections
    y = df.loc[(df['location'] == location_selector) & (df['weather'] == weather_selector) & (df['wind_speed_mph'].between(wind - wind_plus_minus, wind + wind_plus_minus)) & (df['air_temp_f'].between(temp - temp_plus_minus, temp + temp_plus_minus))].groupby('month').sum()['skunked']
    z = df.loc[(df['location'] == location_selector) & (df['weather'] == weather_selector) & (df['wind_speed_mph'].between(wind - wind_plus_minus, wind + wind_plus_minus)) & (df['air_temp_f'].between(temp - temp_plus_minus, temp + temp_plus_minus))].groupby('month').count()['date']
    y = y.reset_index()
    z = z.reset_index()
    df = pd.merge(z, y, on = 'month')
    df.rename(columns={'month': 'Month', 'skunked': 'Skunked', 'date': 'Times Fished'}, inplace = True)
    df_month = df.copy()
    df_month['Month'] = df_month['Month'].map({4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September'})

    st.markdown("<h6 style='text-align: center; color: black;'>Times Fished vs. Times Skunked</h6>", unsafe_allow_html=True)
    st.bar_chart(df_month.set_index('Month'), width=0, height=0, use_container_width=True)

    # Display bar-chart table
    st.dataframe(df)
    
# ----------------------------------------------------------------------------
# Where to Fish
where_to_fish = sidebar.checkbox("I don't know where to fish...")

if where_to_fish:
    
        st.markdown("""---""")
    
        st.text("""This page helps to show you where to fish based on the weather conditions you 
select. It will filter the table and graphs to show you those records that match 
where you have fished previously under the selected conditions, and the graphs will 
show you where the best places have been with these weather conditions.""")
        
        st.markdown("""---""")
        
        ## Weather
        # get list of all weather conditions that have occurred in selected location
        ml = [str(x) for x in df['weather'].unique()]
        weather_types = [x for x in ml if x != 'no_weather_recorded']

        # create sidebar with weather dropdown
        weather_condition = sidebar.selectbox(
            "Select a Weather Condition",
            weather_types
        )
        
        # create dropdown with wind direction
        wind_dir_selector = sidebar.selectbox(
            'Select a Wind Direction',
            wind_directions
        )

        # create slider with temperatures
        temperature = sidebar.slider('Select a Temperature', 35, 90, 70, 1)
        temperature_plus_minus = sidebar.slider("Plus or Minus Degrees", 0, 30, 30, 1)

        # create slider with wind
        wind_speed = sidebar.slider('Select a Wind Speed', 0, 20, 7, 2)
        wind_speed_plus_minus = sidebar.slider("Plus or Minus Windspeed MPH", 0, 30, 30, 1)

        df_where = df.loc[(df['weather'] == weather_condition) & (df['wind_speed_mph'].between(wind_speed - wind_speed_plus_minus, wind_speed + wind_speed_plus_minus)) & (df['air_temp_f'].between(temperature - temperature_plus_minus, temperature + temperature_plus_minus)) & (df['wind_dir'] == wind_dir_selector)]
        
        st.dataframe(df_where)
        st.write(f'{len(df_where)} records')
        
        # Distribution of Locations Fished
        
        hist = alt.Chart(df_where).mark_bar(
            size=30
        ).encode(
            x=alt.X("location", bin=False, axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('count()', axis=alt.Axis(tickMinStep=1)),
        ).properties(
            title='Distribution of Locations Fished',
            width=800,
            height=600
        ).configure_title(
            fontSize=15,
            color='black'
        )
        
        st.altair_chart(hist)
        
        # Fish Caught by Location
        
        fish_caught = df_where.loc[(df['fish_type'] != 'no_fish_caught')].groupby('location')['fish_type'].count().sort_values(ascending=False).to_frame().rename(columns={"fish_type":"# of Fish Caught"})
        fish_caught.reset_index(inplace = True)
        fish_caught.rename(columns={"fish_type":"# of Fish Caught"})
        
        bar = alt.Chart(fish_caught).mark_bar().encode(
            x=alt.X('location', sort='-y', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('# of Fish Caught', axis=alt.Axis(tickMinStep=1)),
        ).properties(
            title = 'Fish Caught by Location',
            width=800,
            height=600
        ).configure_title(
            fontSize=15,
            color='black'
        )
        
        st.altair_chart(bar)
        st.write(fish_caught)
# ----------------------------------------------------------------------------
# Model
model = sidebar.button('Will I Catch a Fish?!?')


# if model():

#     st.text("""Clicking this button triggers a model to run, which calculates the 
# probability of catching a fish based on the selections you have made. This model 
# uses historic data to determine whether or not a fish is likely to be caught.

# This is mostly for our nerdy selves to have some extra fun with this project!""")

    
# ----------------------------------------------------------------------------
# Database 

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