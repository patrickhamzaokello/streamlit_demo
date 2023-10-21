import streamlit as st
import pandas as pd
import numpy as np


st.title('GAPs Transaction Dashboard')
PAYMENT_DATE = "PaymentDate"

csv_file = st.file_uploader("Upload a CSV file", type=["csv"])


def load_data():
    df = pd.read_csv(csv_file)
    df[PAYMENT_DATE] = pd.to_datetime(df[PAYMENT_DATE], format='mixed')
    selected_year = st.sidebar.selectbox("Select a Year", sorted(df[PAYMENT_DATE].dt.year.unique()))
    data = df[df[PAYMENT_DATE].dt.year == selected_year]
    return data

def processed_data(raw_data):
    
    selected_columns = [
        'TransID',
        'BatchID',
        'VendorName',
        'VendorBankName',
        'VendorAcctNumber',
        'Amount',
        'Currency',
        'CustomerAcctNumber',
        'CompanyName',
        'PaymentDate',
        'PaidDate',
        'ProcessFlag',
        'ProcessType',
        'PaymentDeclined',
        'Remarks'
    ]
    
    processed_data = raw_data[selected_columns]
    return processed_data

if csv_file is not None:
    data_load_state = st.text('Loading data...')
    data = load_data()
    data_load_state.text("Done! (Loaded Successfully)")

    if st.sidebar.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.write(data)

    if st.sidebar.checkbox('Show Processed data'):
        st.subheader('Processed data')
        st.write(processed_data(data))
