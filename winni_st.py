import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date
import altair as alt
import datetime

html_temp = """
    <div style="background:#025246 ;padding:10px">
    <h2 style="color:white;text-align:center;"> Winnipesaukee Fishing Reports </h2>
    </div>
    """
st.markdown(html_temp, unsafe_allow_html = True)

today = date.today()
today

url = 'https://github.com/dancosta154/Winnipesaukee_MultiRegression/blob/main/model_data/winni_reports.csv?raw=true'
df = pd.read_csv(url,index_col=0)

def make_unique_list(col):
    return col.unique()

# # universal variables
location = make_unique_list(df['location'])
weather = [str(x) for x in df['weather'].unique() if x != 'no_weather_recorded']
wind_directions = make_unique_list(df['wind_dir'])

# create sidebar and sidebar options
sidebar = st.sidebar

with sidebar:
    selected = option_menu(
        menu_title = 'Navigation',
        options=['Home', 'Show Me My Fish', 'Where Should I Fish?', 'Add Fish', 'How Does My Data Cluster?'],
        icons=['house','folder2-open','cloud-sun','journal-plus','grid-1x2'],
        menu_icon='cast',
        default_index=0,
        styles={
        "container": {"padding": "0"},
        "icon": {"color": "black", "font-size": "15px"}, 
        "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#025246"}
        }
    )

if selected == 'Home':
    st.write("""Remember how you wrote down all of those entries into your book? Well here they are! 
    If you want to see all of the fish you've caught by location or weather condition,
    click on the **"I want to see all the fish I've caught"** checkbox. \n\n Alternatively, if you'd like to know where to fish based on tomorrow's 
    weather conditions, then click the **"I don't know where to fish"** checkbox. \n\n Even cooler, as you catch fish, you can add them to this website and the data will be
    reflective of your newly caught fish! Just click on the **"Add fish that I've caught"** checkbox to access this part. \n\n Now, this website wouldn't be complete without some
    modeling... so if you'd like to see how your data is clustered (think "dividing the population or data points into a number of groups such that data points in the same groups are
    more similar to other data points in the same group and dissimilar to the data points in other groups"), then click on the **"How does this data cluster?"** checkbox.""")
if selected == 'Show Me My Fish':
    st.text("""
    This page shows you a history of all of the records from your notebook! Each record 
    in the table is an entry from the notebook; however, that doesn't mean one entry per 
    day... each fish is it's own entry as the data is different for that particular 
    fish (fish type, length, depth caught, etc.) 

    Filtering the selections on the left will shrink the table and graphs below to only 
    records that match the selections you choose. Have fun!
    """)
    
    location = make_unique_list(df['location'])
    
    location_selector = sidebar.selectbox(
        "Select a Location",
        np.sort(location)
    )

    # filter df to only records with the selected location 
    df_location = df[df['location'] == location_selector]

    # get list of all weather conditions that have occurred in selected location
    weather = np.sort([str(x) for x in df_location['weather'].unique() if x != 'no_weather_recorded'])[::-1]

    weather_selector = sidebar.selectbox(
        "Select a Weather Condition",
        weather
    )

    # temperature sliders
    temp = sidebar.slider('Select a Temperature', 35, 90, 70, 1)
    temp_plus_minus = sidebar.slider("Plus or Minus Degrees", 0, 30, 30, 1)

    # wind sliders
    wind = sidebar.slider('Select a Wind Speed', 0, 20, 7, 2)
    wind_plus_minus = sidebar.slider("Plus or Minus Windspeed MPH", 0, 30, 30, 1)

    df_weather = df_location[(df_location['weather'] == weather_selector) & (df_location['wind_speed_mph'].between(wind - wind_plus_minus, wind + wind_plus_minus)) & (df_location['air_temp_f'].between(temp - temp_plus_minus, temp + temp_plus_minus))] 

    # Reporting about selected location 
    st.write(f"**Weather Conditions: {weather_selector.title()}, {temp}&deg;, {wind} mph winds** for **{location_selector.title()}**")
    if df_weather.shape[0] > 1:
        st.write(f'This location has **{df_weather.shape[0]} records** with these weather conditions')
    else:
        st.write(f'This location has **{df_weather.shape[0]} record** with these weather conditions')
    st.write(f"Under these weather conditions, this location was last fished on **{df_weather['date'].max()}**")

    st.dataframe(df_weather)
    st.write(f'{len(df_weather)} records')
    
    # Download dfs to CSV
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    csv = convert_df(df_weather)

    st.download_button(
        'Click to download filtered table', 
        csv,
        f'winni_data_{location_selector}_{today}.csv',
        'text/csv',
        key='download-csv'
    )

    csv = convert_df(df)

    st.download_button(
        'Click to download table with all records', 
        csv,
        f'winni_data_{today}.csv',
        'text/csv',
        key='download-csv'
    )

    st.markdown("""---""")

    # Pie Chart and Table associated with chart
    pie = df_weather.value_counts(['fish_type'], normalize=True).to_frame()
    pie.rename(columns = {0: 'Percent_Caught'}, inplace = True)
    pie.reset_index(inplace = True)
    pie['fish_type'] = pie['fish_type'].map(lambda x: x.title())
    pie.set_index('fish_type', inplace = True)
    
    # creates pie-chart based on user selections
    fig, ax = plt.subplots()
    ax.pie(pie['Percent_Caught'], 
           labels=pie.index, 
           autopct='%1.1f%%',
           textprops = {'size': 'small'},
           wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
    plt.title(f'Fish Caught {location_selector.title()}: \n {weather_selector.title()} Weather Conditions', fontdict={'fontsize': 8})
    st.pyplot(fig)

    # Display pie-chart table
    st.dataframe(pie)

    st.markdown("""---""") 

    ## Bar Chart and Table associated with chart
    # creates bar-chart based on user selections
    a = df_weather.groupby('month').sum()['skunked'].reset_index()
    b = df_weather.groupby('month').count()['date'].reset_index()
    chart = pd.merge(b, a, on = 'month')
    chart.rename(columns={'month': 'Month', 'skunked': 'Skunked', 'date': 'Times Fished'}, inplace = True)
    chart_month = chart.copy()
    chart_month['Month'] = chart_month['Month'].map({4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September'})

    st.markdown("<h6 style='text-align: center; color: black;'>Times Fished vs. Times Skunked</h6>", unsafe_allow_html=True)
    st.bar_chart(chart_month.set_index('Month'), width=0, height=0, use_container_width=True)

    # Display bar-chart table
    st.dataframe(chart_month)
    
if selected == 'Where Should I Fish?':
    st.text("""
    This page helps to show you where to fish based on the weather conditions you 
    select. It will filter the table and graphs to show you those records that match 
    where you have fished previously under the selected conditions, and the graphs will 
    show you where the best places have been with these weather conditions.
    """)

    # create sidebar with weather dropdown
    weather_condition = sidebar.selectbox(
        "Select a Weather Condition",
        weather
    )

    # create dropdown with wind direction
    wind_dir_selector = sidebar.selectbox(
        'Select a Wind Direction',
        wind_directions
    )

    # temperature sliders
    temp = sidebar.slider('Select a Temperature', 35, 90, 70, 1)
    temp_plus_minus = sidebar.slider("Plus or Minus Degrees", 0, 30, 30, 1)

    # wind sliders
    wind = sidebar.slider('Select a Wind Speed', 0, 20, 7, 1)
    wind_plus_minus = sidebar.slider("Plus or Minus Windspeed MPH", 0, 30, 30, 1)

    df_weather = df.loc[(df['weather'] == weather_condition) & (df['wind_speed_mph'].between(wind - wind_plus_minus, wind + wind_plus_minus)) & (df['air_temp_f'].between(temp - temp_plus_minus, temp + temp_plus_minus)) & (df['wind_dir'] == wind_dir_selector)]

    st.dataframe(df_weather)
    st.write(f'{len(df_weather)} records')

    # Distribution of Locations Fished    
    days_fished = df_weather.groupby(['location', 'date']).count().groupby('location').count()['month'].sort_values(ascending=False).to_frame().rename(columns={"month":"# of Days Fished"}).reset_index()
       
    days_fished_bc = alt.Chart(days_fished).mark_bar(size=40).encode(
        x=alt.X('location', sort='-y', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('# of Days Fished', axis=alt.Axis(tickMinStep=1)),
    ).properties(
        title = 'Days Fished by Location',
        width=800,
        height=600
    ).configure_title(
        fontSize=15,
        color='black'
    )

    st.altair_chart(days_fished_bc)

    # Bar Chart - Fish Caught by Location
    fish_caught = df_weather.loc[(df['fish_type'] != 'no_fish_caught')].groupby('location')['fish_type'].count().sort_values(ascending=False).to_frame().rename(columns={"fish_type":"# of Fish Caught"}).reset_index()
    # fish_caught.rename(columns={"fish_type":"# of Fish Caught"})

    bar_chart = alt.Chart(fish_caught).mark_bar(size=40).encode(
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

    st.altair_chart(bar_chart)
    st.write(fish_caught.head(10))
    
if selected == 'Add Fish':
    d = st.date_input(
     "What is the date you fished?",
     datetime.date(2022, 6, 22))
    
    st.write('You caught these fish on:', d)
    
if selected == 'How Does My Data Cluster?':
    st.write('Working on this section')

    
# model = sidebar.button('Will I Catch a Fish?!?')


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