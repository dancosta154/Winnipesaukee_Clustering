import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import tableauserverclient as TSC
import streamlit.components.v1 as components

from datetime import date
import datetime

from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler

from io import StringIO
import io
from google.cloud import storage
from google.oauth2 import service_account

html_temp = """
    <div style="background:#025246 ;padding:10px">
    <h2 style="color:white;text-align:center;"> Winnipesaukee Fishing Reports </h2>
    </div>
    """
st.markdown(html_temp, unsafe_allow_html = True)

today = datetime.date.today()
today

# '--------------------------------'

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = storage.Client(credentials=credentials)

# Retrieve file contents every one second
@st.experimental_memo(ttl=1)

def read_file(bucket_name, file_path):
    bucket = client.bucket(bucket_name)
    content = bucket.blob(file_path).download_as_string().decode("utf-8")
    return content

bucket_name = "winni-data-bucket"
file_path = "winni_reports.csv"

content = read_file(bucket_name, file_path)

result_df = io.StringIO(content)
df = pd.read_csv(result_df, index_col = 0)

# '--------------------------------'

def make_unique_list(col):
    return col.unique()

# universal variables
location = make_unique_list(df['location'])
weather = [str(x) for x in df['weather'].unique() if x != 'no_weather_recorded']
wind_directions = make_unique_list(df['wind_dir'])
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

# create sidebar and sidebar options
sidebar = st.sidebar

with sidebar:
    selected = option_menu(
        menu_title = 'Navigation',
        options=['Home', 'Show Me My Fish', 'Where Should I Fish?', 'Add Fish', 'How Is My Data Clustered?', 'Additional Graphics'],
        icons=['house','folder2-open','cloud-sun','journal-plus','grid-1x2', 'file-bar-graph'], # https://icons.getbootstrap.com/
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
    click on **"Show Me My Fish"**. \n\n Alternatively, if you'd like to know where to fish based on tomorrow's 
    weather conditions, then click the **"Where Should I Fish?"**. \n\n Even cooler, as you catch fish, you can add them to this website and the data will be
    reflective of your newly caught fish! Just click on **"Add Fish"** to access this part. \n\n Now, this website wouldn't be complete without some
    modeling... so if you'd like to see how your data is clustered (think "dividing the population or data points into a number of groups such that data points in the same groups are
    more similar to other data points in the same group and dissimilar to the data points in other groups"), then click on the **"How Does My Data Cluster?"**.""")

if selected == 'Show Me My Fish':
    
    def main():
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
        wind = sidebar.slider('Select a Wind Speed', 0, 20, 7, 1)
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
    
    if __name__ == '__main__':
        main()
     
    
if selected == 'Where Should I Fish?':
    
    def main():
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
        
    if __name__ == '__main__':
        main()
    
if selected == 'Add Fish':
    
    def main():
        st.write("This section allows for you to add the fish you have caught, one fish at a time. Adding records where no fish were caught is equally important to this dataset!")

        with st.form(key='myform', clear_on_submit=True):
            date = st.date_input('What is the Date You Fished?', today)
            location_selector = st.selectbox("Where Did You Fish?", np.sort(location))
            fish_type = st.selectbox('What Type of Fish Did You Catch?', ('Salmon', 'Rainbow', 'Lake Trout', 'Horned Pout', 'Smallmouth', 'No Fish Caught'))
            fish_length = st.number_input('Length of Fish')
            water_depth = st.number_input('Depth at Which You Caught the Fish')
            time_caught = st.time_input('What Time Did You Catch the Fish?', datetime.time(7, 30))
            weather_condition = st.selectbox("Select a Weather Condition", weather)
            temperature = st.number_input('Air Temperature (F)')
            water_temperature = st.number_input('Water Temperature (F)')
            wind_dir_selector = st.selectbox('Select a Wind Direction', wind_directions)
            wind_speed = st.number_input('Wind Speed (MPH)')
            lines_in = st.time_input('What Time Did You Start Fishing?', datetime.time(7, 00))
            lines_out = st.time_input('What Time Did You Stop Fishing?', datetime.time(11, 45))
            
            record = [
                str(date)[:4], # year
                date, 
                temperature,
                water_temperature,
                wind_speed,
                wind_dir_selector,
                weather_condition,
                location_selector, 
                time_caught,
                fish_type, 
                fish_length, 
                water_depth, 
                np.where(fish_type == "No Fish Caught", True, False), # skunked
                lines_in,
                lines_out,
                ''.join([i for i in location_selector.split() if i not in ['east', 'west', 'north', 'south', 'of']]), # general_loc
                (pd.to_datetime(lines_out, format='%H:%M:%S') - pd.to_datetime(lines_in, format='%H:%M:%S')).total_seconds() / 60, # duration_min
                date.month, # month
                time_caught.hour # hour
            ]
            
            if st.form_submit_button("Add Record"):
                df.loc[len(df.index)] = record
                
            df.to_csv('updated_df.csv')
            
            with open('updated_df.csv') as f:
                s = f.read() + '\n' # add trailing new line character
               
            client = storage.Client(credentials=credentials)
            bucket = client.get_bucket(bucket_name)
            blob = bucket.blob(file_path)
            blob.upload_from_string(s)

            st.write(df)               
       
    if __name__ == '__main__':
        main()
     
        
if selected == 'How Is My Data Clustered?':
    
    def main():
        
        cluster_type = st.selectbox(
            "Select Which Model to Cluster",
            ('KMeans', 'DBScan')
        )

        numeric_col1 = st.selectbox(
            "Select Field 1 to Analyze",
            numeric_cols,
            index=numeric_cols.index('water_temp_f')
            )

        numeric_col2 = st.selectbox(
            "Select Field 2 to Analyze",
            [i for i in numeric_cols if i != numeric_col1],
            index=[i for i in numeric_cols if i != numeric_col1].index('fish_length_in')
            )

        # Model Prep
        df_dummies = pd.get_dummies(df, columns = ['wind_dir', 'weather', 'general_loc', 'fish_type'], drop_first = True)

        # Define X
        X = df_dummies.drop(columns = ['date','fish_length_in', 'time_caught', 'lines_in', 'lines_out', 'location', 'skunked'])

        # Standard Scalar
        sc = StandardScaler()
        X_scaled = sc.fit_transform(X)

        if cluster_type == 'KMeans':

            num_clusters = st.slider('How Many Clusters?', 2, 5, 3, 1)

            def run_kmeans(df, n_clusters=3):
                kmeans = KMeans(n_clusters, random_state=0).fit(df[[numeric_col1, numeric_col2]])

                df['cluster'] = kmeans.labels_ + 1

                fig, ax = plt.subplots(figsize=(16, 9))

                ax.grid(False)
                ax.set_facecolor("#FFF")
                ax.spines[["left", "bottom"]].set_visible(True)
                ax.spines[["left", "bottom"]].set_color("#4a4a4a")
                ax.tick_params(labelcolor="#4a4a4a")
                ax.yaxis.label.set(color="#4a4a4a", fontsize=25)
                ax.xaxis.label.set(color="#4a4a4a", fontsize=25)
                # --------------------------------------------------

                # Create scatterplot
                ax = sns.scatterplot(
                    ax=ax,
                    x=df[numeric_col1],
                    y=df[numeric_col2],
                    hue=df['cluster'],
                    s=100,
                    palette=sns.color_palette("colorblind", n_colors=n_clusters),
                    legend=True
                )
                plt.legend(
                    title='Cluster',
                    loc='right',
                    bbox_to_anchor=(1.12, .9),
                    title_fontsize=19,
                    fontsize=15
                )

                # Annotate cluster centroids
                for ix, [water_temp_f, month] in enumerate(kmeans.cluster_centers_):
                    ax.scatter(water_temp_f, month, s=200, c="#a8323e")
                    ax.annotate(
                        f"Cluster #{ix+1}",
                        (water_temp_f, month),
                        fontsize=25,
                        color="#a8323e",
                        xytext=(water_temp_f + 5, month + 3),
                        bbox=dict(boxstyle="square, pad=0.2", fc="white", ec="#a8323e", lw=1),
                        ha="center",
                        va="center",
                    )

                return fig

            st.write(run_kmeans(df, n_clusters=num_clusters))

            st.write('Averages by KMeans Cluster')
            cluster_df = df.groupby('cluster').mean().T
            st.dataframe(cluster_df)

        elif cluster_type == 'DBScan':

            eps_select = st.slider('What value of Epsilon do you want to use?', .2, 2.0, .6, .2)
            min_samples_select = st.slider('How many Samples do you want to use?', 5, 8, 5, 1)

            def run_dbscan(df):
                dbscan = DBSCAN(eps = eps_select, min_samples=min_samples_select).fit(X_scaled)

                df['cluster'] = dbscan.labels_ + 2

                n_clusters = df['cluster'].nunique()

                fig, ax = plt.subplots(figsize=(16, 9))

                ax.grid(False)
                ax.set_facecolor("#FFF")
                ax.spines[["left", "bottom"]].set_visible(True)
                ax.spines[["left", "bottom"]].set_color("#4a4a4a")
                ax.tick_params(labelcolor="#4a4a4a")
                ax.yaxis.label.set(color="#4a4a4a", fontsize=25)
                ax.xaxis.label.set(color="#4a4a4a", fontsize=25)
                # --------------------------------------------------

                # Create scatterplot
                ax = sns.scatterplot(
                    ax=ax,
                    x=df[numeric_col1],
                    y=df[numeric_col2],
                    hue=df['cluster'],
                    s=100,
                    palette=sns.color_palette("colorblind", n_colors=n_clusters),
                    legend=True
                )
                plt.legend(
                    title='Cluster',
                    loc='right',
                    bbox_to_anchor=(1.12, .9),
                    title_fontsize=19,
                    fontsize=15
                )

                return fig

            st.write(run_dbscan(df))

            st.write('Averages by DBSCAN Cluster')
            cluster_df = df.groupby('cluster').mean().T
            st.dataframe(cluster_df)
    
    if __name__ == '__main__':
        main()
     
if selected == 'Additional Graphics':
    
        st.write('Each fish represents a location.  Hover the mouse over a fish for more info!')
        
        def main():
            html_temp = "<div class='tableauPlaceholder' id='viz1656796414285' style='position: relative'><noscript><a href='#'><img alt='Fish Length vs Water Depth, by Location ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Wi&#47;WinniLake&#47;Sheet1&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='WinniLake&#47;Sheet1' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Wi&#47;WinniLake&#47;Sheet1&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1656796414285');                    var vizElement = divElement.getElementsByTagName('object')[0];                    vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';                    var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>"

            components.html(html_temp, height = 800, width = 800)

        if __name__ == "__main__":    
            main()