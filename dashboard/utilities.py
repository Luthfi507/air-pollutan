import pandas as pd
import plotly.express as px
import os
import streamlit as st

@st.cache_data
def load_and_clean_data():
    folder_path = '../'
    dfs = []
    
    for root, _, files in os.walk(folder_path):
        if os.path.basename(root) == 'data':
            for file in files:
                file_path = os.path.join(root, file)
                df = pd.read_csv(file_path)
                dfs.append(df)           
    
    data = pd.concat(dfs)
    data = data.interpolate() 
    data = data.dropna()      
    data['datetime'] = pd.to_datetime(data[['year', 'month', 'day']])
    return data

def filter_data(data, station, option, start_date, end_date):
    polutan = ['PM2.5', 'PM10', 'SO2', 'NO2', 'O3', 'CO']
    air = ['TEMP', 'PRES', 'DEWP', 'WSPM']

    filtered_data = data[data['station'] == station]
    filtered_data = filtered_data[(filtered_data['datetime'] >= start_date) & (filtered_data['datetime'] <= end_date)]

    if option == 'Hourly':
        time_cols = ['year', 'month', 'day', 'hour']
        df_polutan = filtered_data.groupby(time_cols)[polutan].mean().reset_index()
        df_air = filtered_data.groupby(time_cols)[air].mean().reset_index()
        df_wd = filtered_data.groupby(time_cols + ['wd'])['No'].count().reset_index()

        df_polutan['time'] = pd.to_datetime(df_polutan[time_cols])
        df_air['time'] = pd.to_datetime(df_air[time_cols])
        df_wd['time'] = pd.to_datetime(df_wd[time_cols])

    elif option == 'Daily':
        time_cols = ['year', 'month', 'day']
        df_polutan = filtered_data.groupby(time_cols)[polutan].mean().reset_index()
        df_air = filtered_data.groupby(time_cols)[air].mean().reset_index()
        df_wd = filtered_data.groupby(time_cols + ['wd'])['No'].count().reset_index()

        df_polutan['time'] = pd.to_datetime(df_polutan[time_cols]).dt.strftime('%Y-%m-%d')
        df_air['time'] = pd.to_datetime(df_air[time_cols]).dt.strftime('%Y-%m-%d')
        df_wd['time'] = pd.to_datetime(df_wd[time_cols]).dt.strftime('%Y-%m-%d')
            
    elif option == 'Monthly':        
        time_cols = ['year', 'month']
        df_polutan = filtered_data.groupby(time_cols)[polutan].mean().reset_index()
        df_air = filtered_data.groupby(time_cols)[air].mean().reset_index()
        df_wd = filtered_data.groupby(time_cols + ['wd'])['No'].count().reset_index()

        df_polutan['time'] = pd.to_datetime(df_polutan[['year', 'month']].assign(day=1)).dt.strftime('%Y-%m')
        df_air['time'] = pd.to_datetime(df_air[['year', 'month']].assign(day=1)).dt.strftime('%Y-%m')
        df_wd['time'] = pd.to_datetime(df_wd[['year', 'month']].assign(day=1)).dt.strftime('%Y-%m')

    elif option == 'Yearly':
        df_polutan = filtered_data.groupby('year')[polutan].mean().reset_index().rename(columns={'year': 'time'})
        df_air = filtered_data.groupby('year')[air].mean().reset_index().rename(columns={'year': 'time'})
        df_wd = filtered_data.groupby(['year', 'wd'])['No'].count().reset_index().rename(columns={'year': 'time'})

    return df_polutan, df_air, df_wd

def AQI(value):
    if value < 9.1:
        return 'Good', 'green'
    elif value < 35.5:
        return 'Moderate', 'yellow'
    elif value < 55.5:
        return 'Unhealthy for Sensitive Groups', 'orange'
    elif value < 125.5:
        return 'Unhealthy', 'red'
    elif value < 225.5:
        return 'Very Unhealthy', 'purple'
    else:
        return 'Hazardous', 'brown'

@st.cache_data
def calculate_pollutan(data):
    PM25 = data['PM2.5'].mean()
    PM10 = data['PM10'].mean()
    SO2 = data['SO2'].mean()
    NO2 = data['NO2'].mean()
    O3 = data['O3'].mean()
    CO = data['CO'].mean()
    quality, color = AQI(PM25)

    return [PM25, PM10, SO2, NO2, O3, CO, quality, color]

def display_pollutan(pollutan, names):
    st.header('Average Pollutants')

    cols = st.columns(3)
    for i, (pol_name, pol_value) in enumerate(zip(names[:3], pollutan[:3])):
        cols[i].metric(label=pol_name, value=f"{pol_value:.2f}")

    cols = st.columns(3)
    for i, (pol_name, pol_value) in enumerate(zip(names[3:], pollutan[3:6])):
        cols[i].metric(label=pol_name, value=f"{pol_value:.2f}")
    
    quality_text = f'<span style="color:{pollutan[-1]}; font-size:24px;">{pollutan[-2]}</span>'
    st.markdown(f'### Air Quality Index: {quality_text}', unsafe_allow_html=True)

def calculate_wind(data):
    temp = data['TEMP'].mean()
    pres = data['PRES'].mean()
    dewp = data['DEWP'].mean()
    wspm = data['WSPM'].mean()
    return [temp, pres, dewp, wspm]

def display_wind(wind_names, wind_value):
    st.header('Wind Parameters')

    cols = st.columns(4)
    for i, (name, value) in enumerate(zip(wind_names, wind_value)):
        cols[i].metric(label=name, value=f'{value:.2f}')

def lineplot(data, x, y, units):
    fig = px.line(data, x, y)
    fig.update_xaxes(title_text='Time')
    fig.update_yaxes(title_text=units)
    # fig.update_layout(
    #     title={
    #         'text': titles,
    #         'x': 0.5,
    #         'xanchor': 'center',
    #         'yanchor': 'top'
    #     })
    return fig

@st.cache_data
def wind_direction(data):
    direction_order = ['N', 'NNE', 'NE', 'ENE', 
                       'E', 'ESE', 'SE', 'SSE', 
                       'S', 'SSW', 'SW', 'WSW',
                       'W', 'WNW', 'NW', 'NNW',]
    
    data = data.groupby('wd')['No'].sum().reset_index()
    data['wd'] = pd.Categorical(data['wd'], categories=direction_order, ordered=True)
    data = data.sort_values('wd')
    
    return data

def plot_wd(data):
    fig = px.line_polar(
        data,
        r='No',  
        theta='wd', 
        line_close=True,  
        template='plotly_dark', 
    )

    # Memperbarui tampilan visual dengan warna dan garis pengisi
    fig.update_traces(fill='toself', fillcolor='teal', line_color='teal')
    
    # Mengatur tata letak grafik
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, showticklabels=False)  
        ),
        showlegend=False  
    )

    return fig

# data from https://www.researchgate.net/figure/Station-longitude-and-latitude-coordinates_tbl1_364442029
@st.cache_data
def load_city():
    for root, _, files in os.walk('../'):
        if os.path.basename(root) == 'dashboard':
            if 'country.txt' in files:
                filepath = os.path.join(root, 'country.txt')
                break
            
    df_city = pd.read_csv(filepath)
    return df_city

@st.cache_data(show_spinner=False)
def plot_map(df, station):
    selected_data = df[df['station'] == station]
    st.map(selected_data[['lat', 'lon']])