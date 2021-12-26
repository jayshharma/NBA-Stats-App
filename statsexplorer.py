#import statements
import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt 
import seaborn as sns 
import numpy as np 

LOGO_IMAGE = "Basketball Image.png"

#Title
st.markdown(
    """
    <style>
    .container {
        display: flex;
    }
    .logo-text {
        font-weight:700 !important;
        font-size:50px !important;
    }
    .logo-img {
        margin: auto;
        width: 7vh;
        height: 7vh;
        margin-left: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="container">
        <p class="logo-text">NBA Stats Explorer</p>
        <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
    </div>
    """,
    unsafe_allow_html=True
)

#Description
st.markdown("""
A web application developed using Python for scraping NBA Player Stats Data.
* **Python Libraries:** base64, pandas, matplotlib, numpy, seaborn, streamlit.
* **Data Source:** [Basketball-reference.com](https://www.basketball-reference.com/).
""")

#Sidebar Year Selection Filter
st.sidebar.header('Filter Data')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950,2022)))) #Reversed list for displaying years in descending order

#Webscraping 
@st.cache
def load_data(year): #function for loading player data based on year specified
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html" #data source in the form of an HTML file
    html = pd.read_html(url, header = 0) #pandas reads data from HTML file
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index)
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)
    return playerstats 
playerstats = load_data(selected_year) #retrieves player stats by using the selected_year variable as an input argument in the custom function load_data

#Sidebar Team Selection Filter
sorted_unique_team = sorted(playerstats.Tm.unique()) #displays unique values from team column
selected_team = st.sidebar.multiselect('Team', sorted_unique_team) 

#Sidebar Position Selection Filter
unique_pos = ['C', 'PF', 'SF', 'SG', 'PG']
selected_pos = st.sidebar.multiselect('Position', unique_pos)

#Filtering Data using Pandas
df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))].astype(str) #Filters data based on user selection for team and position

st.header('Player Stats of Selected Team(s)')
st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
st.dataframe(df_selected_team)

#Download NBA Player Stats Data using base64
def filedownload(df): #custom function for downloading dataframe
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href 

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)


#Intercorrelation Heatmap Generation using matplotlib 
if st.button('View Intercorrelation Heatmap'):
    st.header('Intercorrelation Heatmap')
    df_selected_team.to_csv('output.csv', index=False)
    df = pd.read_csv('output.csv')
    
    #Intercorrelation Matrix Calculations
    corr = df.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7,5))
        ax = sns.heatmap(corr, mask=mask, vmax=1,square=True)
    st.pyplot()

st.set_option('deprecation.showPyplotGlobalUse', False)