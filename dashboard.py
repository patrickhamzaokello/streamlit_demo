import streamlit as st
import pandas as pd
import numpy as np
import calendar
import plotly_express as px 
import humanize

# Load and apply custom CSS
def load_custom_css():
    with open("assets/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



st.set_page_config(
    page_title="GAPS Dasbboard View",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS
load_custom_css()


st.sidebar.title('GTBANK (Uganda)')
st.sidebar.subheader('GAPS Dashboard')
st.sidebar.divider()
PAID_DATE_COLUMN = "PaidDate"
PAYMENT_DATE_COLUMN = "PaymentDate"
ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


csv_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"] ,label_visibility="collapsed")
st.sidebar.divider()

@st.cache_data
def load_data(csv_file_data):
    data = pd.read_csv(csv_file_data)
    data[PAID_DATE_COLUMN] = pd.to_datetime(data[PAID_DATE_COLUMN], format='mixed')
    data[PAYMENT_DATE_COLUMN] = pd.to_datetime(data[PAYMENT_DATE_COLUMN], format='ISO8601')
    return data

@st.cache_data
def selectDataYear(selected_year, data):
    data = data[data[PAYMENT_DATE_COLUMN].dt.year == selected_year]
    return data

@st.cache_data
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
        'PaymentFlag',
        'Remarks'
    ]
    
    processed_data = raw_data[selected_columns]

    # Remove records with PaidDate of null
    # processed_data = processed_data.dropna(subset=[PAID_DATE_COLUMN])

    return processed_data

@st.cache_data
def successfulTransaction(processed_data):
    successful_data = processed_data[(processed_data['PaymentDeclined'] == 0) & (processed_data['PaymentFlag'] == 1) & (processed_data['ProcessFlag'].isin(['A']))]

    return successful_data


@st.cache_data
def notDeclined(processed_data):
    unDeclined_data = processed_data[(processed_data['PaymentDeclined'] == 0)]

    return unDeclined_data

@st.cache_data
def declinedTransactions(processed_data):
    declined_data = processed_data[(processed_data['PaymentDeclined'] == 1)]

    return declined_data

@st.cache_data
def Quarterly_Count_Pie_chart(quarterly_summary):    
    fig = px.pie(quarterly_summary, 
                 values='TransactionCount', names='Quarter', 
                 labels='Quarter', 
                 color_discrete_sequence=px.colors.sequential.Aggrnyl)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        title=f'Percent of Transaction Total Count by Quarter',
        xaxis_title='Month',
        yaxis_title='Count',
        legend=dict(orientation='v', y=1, x=-0.1),
    )
    st.plotly_chart(fig,use_container_width=True)

@st.cache_data
def Monthly_count_bar_graph(successful_data_v):
    successful_data_v['YearMonth'] = successful_data_v[PAYMENT_DATE_COLUMN].dt.to_period('M')
    monthly_counts = successful_data_v['YearMonth'].value_counts().sort_index()

    # Create a bar graph using Plotly with month names on the x-axis
    fig = px.bar(
        x=monthly_counts.index.strftime('%b'),  # Format month names
        y=monthly_counts.values,
        labels={'x': 'Month', 'y': 'Transaction Count'},
        color_discrete_sequence=px.colors.sequential.Aggrnyl,
    )

    fig.update_layout(
        title=f'Total Transaction Count by Month',
        xaxis_title='Month',
        yaxis_title='Count'
    )

    st.plotly_chart(fig,use_container_width=True)


def Filtered_data(successful_data_v):
    # Map 'ProcessType_Description' to 'ProcessType' in the DataFrame
    process_type_monthly_counts = successful_data_v.copy()
    process_type_monthly_counts['ProcessType'] = process_type_monthly_counts['ProcessType_Description']

    # Group the data by 'ProcessType' and year-month of 'PaymentDate' and count the occurrences
    process_type_monthly_counts = process_type_monthly_counts.groupby(['ProcessType', process_type_monthly_counts[PAYMENT_DATE_COLUMN].dt.to_period('M')]).size().reset_index(name='Count')

    # Format the 'PaymentDate' to 'YYYY-MM'
    process_type_monthly_counts[PAYMENT_DATE_COLUMN] = process_type_monthly_counts[PAYMENT_DATE_COLUMN].dt.strftime('%Y-%m')

    all_descriptions = process_type_monthly_counts['ProcessType'].unique()

    # Streamlit filter for selecting 'ProcessType_Description' with multi-select checkboxes
    selected_descriptions = st.multiselect('Select Process Type Descriptions', all_descriptions, default=all_descriptions)

    # Filter the DataFrame based on the selected descriptions
    filtered_data = process_type_monthly_counts[process_type_monthly_counts['ProcessType'].isin(selected_descriptions)]

    return filtered_data

@st.cache_data
def PieChartProcessTypes(filtered_data):
    fig = px.pie(
        filtered_data, 
        values='Count', 
        names='ProcessType', labels='ProcessType', 
        color_discrete_sequence=px.colors.sequential.Aggrnyl
        )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        title=f'Percent of each Process Type Contribution to Total Transaction Count',
        legend=dict(orientation='v', y=1, x=-0.1),
    )
    st.plotly_chart(fig,use_container_width=True)

@st.cache_data
def ProcessTypeLineGraph(filtered_data):
    fig = px.line(
        filtered_data,
        x=PAYMENT_DATE_COLUMN,
        y='Count',
        color='ProcessType',
        line_group='ProcessType',
        labels={PAYMENT_DATE_COLUMN: 'Month'},
        color_discrete_sequence=px.colors.sequential.Aggrnyl
    )
    fig.update_layout(
        title=f'Total Count of Selected Process Type Descriptions Over Each Month',
        xaxis_title='Month',
        yaxis_title='Count',
        legend=dict(orientation='h', y=-0.2, x=-0.1),
    )
    
    st.plotly_chart(fig,use_container_width=True)


@st.cache_data
def Grouped_data_dayOfWeek(successful_data_v):
    week_day_name_count = successful_data_v.groupby(['ProcessType_Description', successful_data_v[PAYMENT_DATE_COLUMN].dt.day_name()]).size().reset_index(name='Count')

    return week_day_name_count


@st.cache_data
def TopDayOfWeekPlot(grouped_data,ordered_days):
    fig = px.bar(
        grouped_data, 
        x=PAYMENT_DATE_COLUMN, 
        y='Count', 
        color='ProcessType_Description', 
        labels={'Count': 'Total Count'},
        category_orders={PAYMENT_DATE_COLUMN: ordered_days} ,
        color_discrete_sequence=px.colors.sequential.Aggrnyl,
        )

    # Customize the layout
    fig.update_layout(
        title='Total Count of Each ProcessType Description Grouped by Day of the Week',
        xaxis_title='Day of the Week',
        yaxis_title='Total Count',
        legend=dict(orientation='h', y=-0.2, x=-0.1),
    )
    

    st.plotly_chart(fig, use_container_width=True)


if csv_file is not None:
    data_load_state = st.sidebar.text('Loading data...')
    data = load_data(csv_file)
    data_load_state.text("Done! (Loaded Successfully)")

    clean_data = processed_data(data)

    year_options = sorted(clean_data[PAYMENT_DATE_COLUMN].dt.year.unique())
    default_year = 2022

    selected_year = st.sidebar.selectbox("Select a Year", year_options, index=year_options.index(default_year))


    processed_data_v = selectDataYear(selected_year, clean_data)

    Total_v = len(processed_data_v)
    total_amount_v = processed_data_v['Amount'].sum()
    users_v = processed_data_v['CompanyName'].str.strip().nunique()



    successful_data_v = successfulTransaction(processed_data_v)

    declined = declinedTransactions(processed_data_v)
    not_declined = notDeclined(processed_data_v)


   
    success_v = len(successful_data_v)
   

    not_declined_v = len(not_declined)
    declined_v = len(declined)

    un_successful_v = not_declined_v - success_v

    
    Transaction_types_v = processed_data_v['ProcessType'].nunique()



    undeclined_percent = str(round(not_declined_v / Total_v * 100, 2))
    declined_v_percent = str(round(declined_v / Total_v * 100, 2))

    with st.container():

        st.title(f"Analysing GAPS Transaction History In {selected_year}")
       
        st.markdown("---")
        st.subheader("Metrics")
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(label=f"Total Count", value=str("{:,.0f}".format(Total_v)))
            st.metric(label=f"Total Amount", value=str(humanize.intword(total_amount_v)))
        with col2:
            st.metric(label=f"UnDeclined Transaction Count ", value=str("{:,.0f}".format(not_declined_v)), delta = f"+ UnDeclined  - ({undeclined_percent} %)" )
            st.metric(label=f"Processed Transactions ", value=str("{:,.0f}".format(success_v)))
            st.metric(label=f"Un-Processed Transactions ", value=str("{:,.0f}".format(un_successful_v)))
        with col3:
            st.metric(label=f"Declined Transactions Count ", value=str( "{:,.0f}".format(declined_v)) , delta = f"- Declined - ({declined_v_percent} %)" )
        with col4:
            st.metric(label=f"Total Companies", value=str(users_v) )
        with col5:
            st.metric(label="Transaction Types", value=str(Transaction_types_v))
     


        st.markdown("---")

    with st.container():

        st.subheader('Quarterly Transaction Summary')
        col3,col1, col2 = st.columns([1,2,2])

        # Resample the data to quarterly counts
        quarterly_counts = successful_data_v.resample('Q', on=PAYMENT_DATE_COLUMN).size()    
        # Calculate the total amount per quarter
        quarterly_total_amount = successful_data_v.resample('Q', on=PAYMENT_DATE_COLUMN)['Amount'].sum()

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
            Monthly_count_bar_graph(successful_data_v)

        with col2:
            Quarterly_Count_Pie_chart(quarterly_summary)
       
        st.markdown("---")


    with st.container():

        st.subheader("Transaction Types")
        filtered_table = Filtered_data(successful_data_v)

        col3,col1, col2, = st.columns([1,2,2])

        with col1:
            PieChartProcessTypes(filtered_table)

        with col2:
            ProcessTypeLineGraph(filtered_table)

        with col3:
            st.write(filtered_table,use_container_width=True)

        st.markdown("---")


    with st.container():
        st.subheader("Top Day of the Week")

        col1, col2 = st.columns([1,2])
       
        week_day_transaction_count = Grouped_data_dayOfWeek(successful_data_v)

        with col1:
            st.write(week_day_transaction_count)

        with col2:
            TopDayOfWeekPlot(week_day_transaction_count, ordered_days)


    st.markdown("---")

    with st.container():
        st.subheader("Transaction Data Tables")
        tab1, tab2, tab3 = st.tabs([f"Raw Data ({len(data)})", f"Processed Transactions ({success_v})", f"Declined Transactions ({len(declined)})"])
        with tab1:
            st.write('**Raw data ( Year: Mixed)**')
            st.write(data)

        with tab2:
            st.write(f'**Processed data (No: {len(successful_data_v)})**')
            st.write(successful_data_v)

        with tab3:
            st.write(f'**Declined Transactions (No: {len(declined)})**')
            st.write(declined)


        st.markdown("---")