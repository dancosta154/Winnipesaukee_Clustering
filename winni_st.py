import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.title("Helping Bill Catch Fish on Lake Winnepausakee")

url = 'https://github.com/aothree/Fishing-Winni/blob/main/model_data/winni_reports.csv?raw=true'
df = pd.read_csv(url,index_col=0)

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

# create slider with wind dropdown
wind = sidebar.slider('How windy is it?', 0, 20,2)
wind_plus_minus = sidebar.slider("Plus or Minus wind mph", 0, 8,1)

# filter df_location to only records with selected weather condition
df_weather = df_location[df['weather'] == weather_selector] 
# filter df_weather to a range of wind within seleceted plus_minus
df_wind = df_weather[df_weather['wind_speed_mph'].between(wind - wind_plus_minus, wind + wind_plus_minus)]





# reporting about selected location 
st.write(f'This location has been fished {df_location.shape[0]} days')
st.write(f"This location was last fished on {df_location['date'].max()}")
st.write(f'This location has been fished {df_wind.shape[0]} days with {weather_selector} conditions and wind of {wind}, plus or minus {wind_plus_minus} mph')
st.write(f"This location was last fished, with these weather conditions, on {df_wind['date'].max()}")

st.markdown("""---""")
st.write('The following data shows records matching the selections')
st.dataframe(df_wind)

st.markdown("""---""")

# creates and displays df based on user selections
x = df.loc[(df['location'] == location_selector) & (df['weather'] == weather_selector)].value_counts(['fish_type'], normalize=True).to_frame()
x.rename(columns = {0: 'Percent_Caught'}, inplace = True)
x.reset_index(inplace = True)
x['fish_type'] = x['fish_type'].map(lambda x: x.title())
x.set_index('fish_type', inplace = True)


# creates pie-chart based on user selections
st.write('Pie Chart does not account for wind')
fig, ax = plt.subplots()
ax.pie(x['Percent_Caught'], 
       labels=x.index, 
       autopct='%1.1f%%',
       textprops = {'size': 'small'},
       wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
plt.title(f'Fish Caught - {location_selector.title()} \n {weather_selector.title()} Weather Conditions')
st.pyplot(fig)

st.dataframe(x)