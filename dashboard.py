import streamlit as st
from datetime import datetime
from utilities import *

st.set_page_config(
    page_title='Air Quality', 
    page_icon='🌫️',
    layout='wide'
    )

# Load and clean the data
data = load_and_clean_data()
min_date = data['datetime'].min().to_pydatetime()
max_date = data['datetime'].max().to_pydatetime()

########## Side Bar #############
with st.sidebar:
    st.markdown(
        '''
        <a href="https://www.linkedin.com/in/lutfi-kurrotaeni/" target="_blank" style="text-decoration: none;">
            <div style="display: flex; align-items: center;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" width="30" height="30">
                <span style="font-size: 16px; margin-left: 5px;">Follow me on LinkedIn</span>
            </div>
        </a>
        ''', 
        unsafe_allow_html=True
    )

    st.header('Filters')

    st.write(
        '''
        This app visualizes data from [Air Quality Dataset](https://github.com/marceloreis/HTI/tree/master/PRSA_Data_20130301-20170228).
        It shows the state of the air quality in some Chinese stations. Just click
        on the widgets below to explore!
        '''
    )

    station = st.selectbox(
        'Station',
        ['Aotizhongxin', 'Changping', 'Dingling', 'Dongsi', 'Guanyuan',
       'Gucheng', 'Huairou', 'Nongzhanguan', 'Shunyi', 'Tiantan',
       'Wanliu', 'Wanshouxigong'],    
    )
    
    option = st.radio(
        'Time range:',
        ['Hourly', 'Daily', 'Monthly', 'Yearly']
    )

    if (option == 'Hourly') or (option == 'Daily'):   
        start_date, end_date = st.slider(
            'Select a date range:',
            min_value=min_date,
            max_value=max_date,
            value=(datetime(2016, 1, 12), datetime(2016, 7, 12)),
            format="YYYY-MM-DD"
        )  

    elif option == 'Monthly':
        start_date, end_date = st.slider(
            'Select a month range:',
            min_value=min_date,
            max_value=max_date,
            value=(datetime(2016, 1, 1), datetime(2017, 1, 31)),
            format="YYYY-MM"
        )

    else:
        start_date, end_date = st.slider(
            'Select a year range:',
            min_value=min_date,
            max_value=max_date,
            value=(datetime(2016, 1, 1), datetime(2017, 1, 1)),
            format="YYYY"
        )
        
    st.caption(f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")    
    st.info('Created by Lutfi Kurrotaeni')

st.title(f'🌫️ Air Quality in {station}')

# Filter the data using the imported function
df_polutan, df_wind, df_wd = filter_data(data, station, option, start_date, end_date)
# st.write(df_wd)

df_city = load_city()
st.write(df_city)
plot_map(df_city, station)

with st.container():
    names = ['PM2.5', 'PM10', 'SO2', 'NO2', 'O3', 'CO']
    pollutan = calculate_pollutan(df_polutan[names])
    display_pollutan(pollutan, names)

    cols = st.columns(2)
    with cols[0]:
        with st.expander('PM2.5'):
            fig = lineplot(df_polutan, 'time', 'PM2.5', 'µg/m³')
            st.plotly_chart(fig)

        with st.expander('SO2'):
            fig = lineplot(df_polutan, 'time', 'SO2', 'µg/m³')
            st.plotly_chart(fig)

        with st.expander('O3'):
            fig = lineplot(df_polutan, 'time', 'O3', 'µg/m³')
            st.plotly_chart(fig)

    with cols[1]:
        with st.expander('PM10'):
            fig = lineplot(df_polutan, 'time', 'PM10', 'µg/m³')
            st.plotly_chart(fig)

        with st.expander('NO2'):
            fig = lineplot(df_polutan, 'time', 'NO2', 'µg/m³')
            st.plotly_chart(fig)

        with st.expander('CO'):
            fig = lineplot(df_polutan, 'time', 'CO', 'µg/m³')
            st.plotly_chart(fig)

with st.container():
    wind_names = ['TEMP', 'PRES', 'DEWP', 'WSPM']
    wind_df = calculate_wind(df_wind[wind_names])
    display_wind(wind_names, wind_df)

    cols = st.columns(2)
    with cols[0]:
        with st.expander('Temperature'):
            fig = lineplot(df_wind, 'time', 'TEMP', 'Celcius')
            st.plotly_chart(fig)

        with st.expander('DEWP'):
            fig = lineplot(df_wind, 'time', 'DEWP', 'Celscius')
            st.plotly_chart(fig)

    with cols[1]:
        with st.expander('Pressure'):
            fig = lineplot(df_wind, 'time', 'PRES', 'hPa')
            st.plotly_chart(fig)

        with st.expander('WSPM'):
            fig = lineplot(df_wind, 'time', 'WSPM', 'm/s')
            st.plotly_chart(fig)

with st.container():
    wd = wind_direction(df_wd)
    cols = st.columns([0.75, 1, 1.5, 0.75])

    with cols[1]:
        st.markdown('### Wind Direction')

        st.dataframe(
            wd.sort_values('No', ascending=False),
            hide_index=True,
            column_config={
                'wd': st.column_config.TextColumn('Wind Direction'),
                'No': st.column_config.ProgressColumn(
                    'Number of wd',
                    format='%f',
                    min_value=0,
                    max_value=max(wd['No'])
                )
            }
        )

        with cols[2]:
            fig = plot_wd(wd)
            st.plotly_chart(fig)