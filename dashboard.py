import streamlit as st
import pandas as pd
import numpy as np
import calendar
import plotly_express as px 

st.set_page_config(
    page_title="GAPS Dasbboard View",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)


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

def interactive_plot(dataframe):
    x_axis_val = st.selectbox('Select X - Axis Value', options = dataframe.columns)
    y_axis_val = st.selectbox('Select Y - Axis Value', options = dataframe.columns)
    plot = px.scatter(dataframe , x=x_axis_val, y=y_axis_val)
    st.plotly_chart(plot)

if csv_file is not None:
    data_load_state = st.sidebar.text('Loading data...')
    data = load_data(csv_file)
    data_load_state.text("Done! (Loaded Successfully)")

    processed_data_v = processed_data(data)
    successful_data_v = successfulTransaction(processed_data_v)
    failed_data_v = failedTransactions(processed_data_v)

    col1, col2, col3, col4 = st.columns((2,1,1,1))
    
    
    with col1:
        st.subheader("Total Transaction Count for Each Month")
        successful_data_v['YearMonth'] = successful_data_v[PAYMENT_DATE_COLUMN].dt.month
        monthly_counts = successful_data_v['YearMonth'].value_counts().sort_index()


    with col2:
        st.subheader("Top Day")

    with col3:
        st.subheader("Top Day")

    with col4:
        st.subheader("Top Day")

    tab1, tab2, tab3, tab4 = st.tabs(["Raw Data", "Processed", "Successful Transactions", "Failed Transactions"])

    st.sidebar.text("Gaps Data Filter")
    if st.sidebar.checkbox('Raw data'):
        with tab1:
            st.subheader(f'Raw data ({len(data)})')
            st.write(data)

    if st.sidebar.checkbox(f'({len(processed_data_v)}) Processed data'):
        with tab2:
            st.subheader(f'Processed data ({len(processed_data_v)})')
            st.write(processed_data_v)

    if st.sidebar.checkbox(f'({len(successful_data_v)}) Successful Transactions'):
        with tab3:
            st.subheader(f'Successful Transactions ({len(successful_data_v)})')
            st.write(successful_data_v)

    if st.sidebar.checkbox(f'({len(failed_data_v)}) Failed Transactions'):
        with tab4:
            st.subheader(f'Failed Transactions ({len(failed_data_v)}) ')
            st.write(failed_data_v)