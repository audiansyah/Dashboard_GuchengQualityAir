import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime

# Load dataset
file_path = 'PRSA_Data_Gucheng_20130301-20170228.csv'
data = pd.read_csv(file_path)

# Data Cleaning
data_cleaned = data.dropna().copy()

# Konversi kolom 'year', 'month', 'day', 'hour' menjadi format datetime
data_cleaned['date'] = pd.to_datetime(data_cleaned[['year', 'month', 'day', 'hour']])

# Drop kolom yang tidak diperlukan
data_cleaned = data_cleaned.drop(columns=['year', 'month', 'day', 'hour'])

# Membuat kolom 'season' berdasarkan bulan
def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

data_cleaned['season'] = data_cleaned['date'].dt.month.apply(get_season)

# Streamlit App
st.title("Dashboard Kualitas Udara di Gucheng (2013-2017)")
st.markdown("Analisis tren polusi udara dan pengaruh variasi musim terhadap kualitas udara di Gucheng.")

# Sidebar untuk filter tahun
start_year, end_year = st.sidebar.slider('Pilih Rentang Tahun:', min_value=2013, max_value=2017, value=(2013, 2017))
filtered_data = data_cleaned[(data_cleaned['date'].dt.year >= start_year) & (data_cleaned['date'].dt.year <= end_year)]

# Pilih hanya kolom numerik untuk resampling
numeric_columns = filtered_data.select_dtypes(include=[np.number]).columns

# Resample hanya pada kolom numerik dengan 'ME' (end of month)
data_resampled = filtered_data.resample('ME', on='date')[numeric_columns].mean()

# Tren PM2.5 dan PM10
st.subheader("Tren Perubahan PM2.5 dan PM10")
fig, ax = plt.subplots(figsize=(14,6))
ax.plot(data_resampled.index, data_resampled['PM2.5'], label='PM2.5', color='blue')
ax.plot(data_resampled.index, data_resampled['PM10'], label='PM10', color='red')
ax.set_title('Tren Perubahan PM2.5 dan PM10 di Gucheng ({}-{})'.format(start_year, end_year))
ax.set_xlabel('Tahun')
ax.set_ylabel('Konsentrasi (µg/m³)')
ax.legend()
st.pyplot(fig)

# Variasi Musim
st.subheader("Pengaruh Musim terhadap Kualitas Udara")
seasonal_data = filtered_data.groupby('season')[['PM2.5', 'SO2', 'NO2']].mean()

fig2, ax2 = plt.subplots(figsize=(10,6))
seasonal_data.plot(kind='bar', ax=ax2)
ax2.set_title('Variasi Musim terhadap Kualitas Udara')
ax2.set_ylabel('Konsentrasi (µg/m³)')
st.pyplot(fig2)

# Menampilkan statistik deskriptif
st.subheader("Statistik Deskriptif Polutan")
st.dataframe(filtered_data[['PM2.5', 'PM10', 'SO2', 'NO2']].describe())

# Membuat tabel RFM Analysis untuk kualitas udara berdasarkan musim
st.subheader("RFM Analysis Berdasarkan Musim")
rfm_seasonal = seasonal_data.reset_index()
rfm_seasonal['Recency'] = rfm_seasonal.index.map({'Winter': 1, 'Spring': 2, 'Summer': 3, 'Fall': 4})
rfm_seasonal['Frequency'] = rfm_seasonal[['PM2.5', 'SO2', 'NO2']].mean(axis=1)
rfm_seasonal['Monetary'] = rfm_seasonal[['PM2.5', 'SO2', 'NO2']].max(axis=1)
st.table(rfm_seasonal)

# Menampilkan raw data jika diinginkan
if st.checkbox('Tampilkan Data Mentah'):
    st.write(filtered_data)