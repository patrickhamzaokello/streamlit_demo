import streamlit as st
import pandas as pd
import numpy as np


st.sidebar.title('GTBANK (Uganda)')
st.sidebar.subheader('GAPS Dashboard')
st.sidebar.divider()
PAYMENT_DATE_COLUMN = "PaymentDate"
PAID_DATE_COLUMN = "PaidDate"


csv_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"] ,label_visibility="collapsed")
st.sidebar.divider()

def load_data(csv_file_data):
    data = pd.read_csv(csv_file_data)
    data[PAYMENT_DATE_COLUMN] = pd.to_datetime(data[PAYMENT_DATE_COLUMN], format='mixed')
    data[PAID_DATE_COLUMN] = pd.to_datetime(data[PAID_DATE_COLUMN], format='mixed')
    selected_year = st.sidebar.selectbox("Select a Year", sorted(data[PAYMENT_DATE_COLUMN].dt.year.unique()))
    data = data[data[PAYMENT_DATE_COLUMN].dt.year == selected_year]
    return data


def processed_data(raw_data):
    process_type_mapping = pd.DataFrame({
        'ProcessType': [1, 10, 11, 12, 13, 14, 2, 3, 4, 5, 6, 7, 8, 9],
        'ProcessType_Description': [
            "GTB", "CONFIRMCHEQUE", "RTGS", "ATW", "AGENCYBANKING", "AIRTIME",
            "AUTOPAY", "DRAFT", "NEFT", "NIPS", "CIT", "OWN", "NEFTDEBIT", "DIT"
        ]
    })
    raw_data = raw_data.merge(process_type_mapping, on='ProcessType', how='left')

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
        'ProcessType_Description',
        'PaymentDeclined',
        'Remarks'
    ]
    
    processed_data = raw_data[selected_columns]
    return processed_data

@st.cache_data
def successfulTransaction(processed_data):
    successful_data = processed_data[
    (processed_data['PaymentDeclined'] == 0) &
    (processed_data['ProcessFlag'].isin(['A']))]

    return successful_data


@st.cache_data
def failedTransactions(processed_data):
    failed_data = processed_data[
    ~(
        (processed_data['PaymentDeclined'] == 0) &
        (processed_data['ProcessFlag'].isin(['A'])) 
    )]

    return failed_data



if csv_file is not None:
    data_load_state = st.sidebar.text('Loading data...')
    data = load_data(csv_file)
    data_load_state.text("Done! (Loaded Successfully)")

    processed_data_v = processed_data(data)
    successful_data_v = successfulTransaction(processed_data_v)
    failed_data_v = failedTransactions(processed_data_v)

    st.sidebar.text("Gaps Data Filter")
    if st.sidebar.checkbox('Raw data'):
        st.subheader(f'Raw data {len(data)}')
        st.write(data)

    if st.sidebar.checkbox(f'({len(processed_data_v)}) Processed data'):
        st.subheader('Processed data')
        st.write(processed_data_v)

    if st.sidebar.checkbox(f'({len(successful_data_v)}) Successful Transactions'):
        st.subheader('Successful Transactions')
        st.write(successful_data_v)

    if st.sidebar.checkbox(f'({len(failed_data_v)}) Failed Transactions'):
            st.subheader('Failed Transactions ')
            st.write(failed_data_v)