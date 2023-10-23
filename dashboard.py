import streamlit as st
import pandas as pd
import numpy as np
import calendar
import plotly_express as px 
import humanize

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


if csv_file is not None:
    data_load_state = st.sidebar.text('Loading data...')
    data = load_data(csv_file)
    data_load_state.text("Done! (Loaded Successfully)")

    processed_data_v = processed_data(data)
    successful_data_v = successfulTransaction(processed_data_v)
    failed_data_v = failedTransactions(processed_data_v)

    total_amount_v = successful_data_v['Amount'].sum()
    Total_v = len(processed_data_v)
    success_v = len(successful_data_v)
    failed_v = len(failed_data_v)

    users_v = data['CompanyName'].nunique()
    Transaction_types_v = data['ProcessType'].nunique()

    success_percent = str(round(success_v / Total_v * 100, 2))
    failed_v_percent = str(round(failed_v / Total_v * 100, 2))

    with st.container():
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(label="Total Count", value=str("{:,.0f}".format(Total_v)))
            st.metric(label="Total Amount", value=str(humanize.intword(total_amount_v)))
        with col2:
            st.metric(label=f"Successful Transaction Count", value=str("{:,.0f}".format(success_v)), delta = f"+ Success  - ({success_percent} %)" )
        with col3:
            st.metric(label=f"Failed Transactions Count", value=str( "{:,.0f}".format(failed_v)) , delta = f"- Failed - ({failed_v_percent} %)" )
        with col4:
            st.metric(label="Total Users", value=str(users_v) )
        with col5:
            st.metric(label="Transaction Types", value=str(Transaction_types_v))
     


        st.markdown("---")

    with st.container():

        st.subheader('Quarterly Transaction Summary')
        col3,col1, col2 = st.columns([1,2,2])

            

        # Resample the data to quarterly counts
        quarterly_counts = successful_data_v.resample('Q', on='PaymentDate').size()

        # Calculate the total amount per quarter
        quarterly_total_amount = successful_data_v.resample('Q', on='PaymentDate')['Amount'].sum()

        # Get the labels for quarters
        quarter_labels = ['Q1', 'Q2', 'Q3', 'Q4']

        # Create a new DataFrame with counts, total amount, and labels
        quarterly_summary = pd.DataFrame({
            'Quarter': quarter_labels,
            'TransactionCount': quarterly_counts,
        })


        quarterly_volume_summary = pd.DataFrame({
            'Quarter': quarter_labels,
            'TotalAmount': quarterly_total_amount
        })



        with col3:
          
            st.write('**Total Transaction Count Per Quarter**')
            st.dataframe(quarterly_summary.style)
            st.write('**Total Transaction Amount Per Quarter**')
            st.dataframe(quarterly_volume_summary.style)
            
        with col1:
            successful_data_v['YearMonth'] = successful_data_v['PaymentDate'].dt.to_period('M')
            monthly_counts = successful_data_v['YearMonth'].value_counts().sort_index()

            # Create a bar graph using Plotly with month names on the x-axis
            fig = px.bar(
                x=monthly_counts.index.strftime('%b'),  # Format month names
                y=monthly_counts.values,
                labels={'x': 'Month', 'y': 'Transaction Count'},
                color_discrete_sequence=px.colors.sequential.RdBu,
            )

            fig.update_layout(
                title=f'Total Transaction Count by Month',
                xaxis_title='Month',
                yaxis_title='Count'
            )

            st.plotly_chart(fig,use_container_width=True)

        with col2:
        
            fig = px.pie(quarterly_summary, values='TransactionCount', names='Quarter', labels='Quarter', color_discrete_sequence=px.colors.sequential.RdBu)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                title=f'Percent of Transaction Total Count by Quarter',
                xaxis_title='Month',
                yaxis_title='Count'
            )
            st.plotly_chart(fig,use_container_width=True)

       
        st.markdown("---")


    with st.container():

        st.subheader("Transaction Types")
        
        
        # Map 'ProcessType_Description' to 'ProcessType' in the DataFrame
        process_type_monthly_counts = successful_data_v.copy()
        process_type_monthly_counts['ProcessType'] = process_type_monthly_counts['ProcessType_Description']

        # Group the data by 'ProcessType' and year-month of 'PaymentDate' and count the occurrences
        process_type_monthly_counts = process_type_monthly_counts.groupby(['ProcessType', process_type_monthly_counts['PaymentDate'].dt.to_period('M')]).size().reset_index(name='Count')

        # Format the 'PaymentDate' to 'YYYY-MM'
        process_type_monthly_counts['PaymentDate'] = process_type_monthly_counts['PaymentDate'].dt.strftime('%Y-%m')

        all_descriptions = process_type_monthly_counts['ProcessType'].unique()

        # Streamlit filter for selecting 'ProcessType_Description' with multi-select checkboxes
        selected_descriptions = st.multiselect('Select Process Type Descriptions', all_descriptions, default=all_descriptions)

        # Filter the DataFrame based on the selected descriptions
        filtered_data = process_type_monthly_counts[process_type_monthly_counts['ProcessType'].isin(selected_descriptions)]

        col3,col1, col2, = st.columns([1,2,2])

        with col1:
            fig = px.pie(filtered_data, values='Count', names='ProcessType', labels='ProcessType', color_discrete_sequence=px.colors.sequential.RdBu)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                title=f'Percent of each Process Type Contribution to Total Transaction Count',
            )
            st.plotly_chart(fig,use_container_width=True)

        with col2:
            fig = px.line(
                filtered_data,
                x='PaymentDate',
                y='Count',
                color='ProcessType',
                line_group='ProcessType',
                labels={'PaymentDate': 'Month'},
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig.update_layout(
                title=f'Total Count of Selected Process Type Descriptions Over Each Month',
                xaxis_title='Month',
                yaxis_title='Count'
            )
            
            st.plotly_chart(fig,use_container_width=True)

        with col3:
            st.write(filtered_data,use_container_width=True)


        st.markdown("---")


    with st.container():
        st.subheader("Top Day of the Week")

        col1, col2 = st.columns([1,2])
        ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        grouped_data = successful_data_v.groupby(['ProcessType_Description', successful_data_v['PaymentDate'].dt.day_name()]).size().reset_index(name='Count')

        with col1:
            st.write(grouped_data)

        with col2:
            # Create a stacked bar graph using Plotly Express
            fig = px.bar(
                grouped_data, 
                x='PaymentDate', 
                y='Count', 
                color='ProcessType_Description', 
                labels={'Count': 'Total Count'},
                category_orders={'PaymentDate': ordered_days} ,
                color_discrete_sequence=px.colors.sequential.RdBu,
                )

            # Customize the layout
            fig.update_layout(
                title='Total Count of Each ProcessType Description Grouped by Day of the Week',
                xaxis_title='Day of the Week',
                yaxis_title='Total Count'
            )

            st.plotly_chart(fig, use_container_width=True)


    st.markdown("---")

    with st.container():
        st.subheader("Transaction Data Tables")

        tab1, tab2, tab3, tab4 = st.tabs([f"Raw Data ({Total_v})", f"Processed ({Total_v})", f"Successful Transactions ({success_v})", f"Failed Transactions ({failed_v})"])
        with tab1:
            st.write('**Raw data**')
            st.write(data)

        with tab2:
            st.write('**Processed data**')
            st.write(processed_data_v)

        with tab3:
            st.write('**Successful Transactions**')
            st.write(successful_data_v)

        with tab4:
            st.write('**Failed Transactions**')
            st.write(failed_data_v)

        st.markdown("---")