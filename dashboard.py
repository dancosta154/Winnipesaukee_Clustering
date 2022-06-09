import streamlit as st
import pandas as pd

pd.options.display.max_columns = 100

st.title("Winnepesaukee Fishing Reports")
st.write('Yellow signifies the highest value in that column.')
st.write('Click the top of a column to sort by that column.')

url = f"https://www.espn.com/mens-college-basketball/team/stats/_/id/2540"
info = pd.read_html(url)
names = pd.DataFrame(info[2])
stats = pd.DataFrame(info[3])
df = pd.concat([names, stats], axis = 1)

df["points/min"] = (df["PTS"] / df["MIN"]).apply(lambda x: round(x, 2))
df["rebounds/min"] = (df["REB"] / df["MIN"]).apply(lambda x: round(x, 2))
df["assists/min"] = (df["AST"] / df["MIN"]).apply(lambda x: round(x, 2))
df["blocks/min"] = (df["BLK"] / df["MIN"]).apply(lambda x: round(x, 2))
df["steals/min"] = (df["STL"] / df["MIN"]).apply(lambda x: round(x, 2))
df["turnovers/min"] = (df["TO"] / df["MIN"]).apply(lambda x: round(x,2))
df['offensive_reb/min'] = (df["OR"] / df["MIN"]).apply(lambda x: round(x, 2))
df['defensive_reb/min'] = (df["DR"] / df["MIN"]).apply(lambda x: round(x, 2))
df['FTA/min'] = (df["FTA"] / df["MIN"]).apply(lambda x: round(x, 2))
df['3PA/min'] = (df["3PA"] / df["MIN"]).apply(lambda x: round(x, 2))

df = df[:-1] # drops last row which is a totals row

df = df.loc[(df.MIN > 12)].copy() # filter out any player who's played less than 12 minutes
df.set_index("Name", inplace=True)

df = df[['MIN', 'points/min', 'rebounds/min',
       'assists/min', 'blocks/min', 'steals/min', 'turnovers/min',
       'offensive_reb/min', 'defensive_reb/min', 'FTA/min', '3PA/min',
       'FGM', 'FGA', 'FTM', 'FTA', '3PM', '3PA', 'PTS', 'OR', 'DR',
       'REB', 'AST', 'TO', 'STL', 'BLK'
      ]]

st.dataframe(df.style.highlight_max(axis=0), height=1000)

st.title("Per Minute Visuals")

st.bar_chart(df['points/min'], height = 400)

st.bar_chart(df["rebounds/min"], height = 400)

st.bar_chart(df['offensive_reb/min'], height = 400)

st.bar_chart(df['defensive_reb/min'], height = 400)

st.bar_chart(df["assists/min"], height = 400)

st.bar_chart(df["blocks/min"], height = 400)

st.bar_chart(df["steals/min"], height = 400)

st.bar_chart(df["turnovers/min"], height = 400)