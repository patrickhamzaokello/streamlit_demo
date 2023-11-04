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
    st.subheader("Distribution of Transaction Types by Quarter")
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

@st.cache_data
def Quarterly_count_bar_graph(quarterly_data_v):
    st.subheader("Comparison of Transaction Counts by Quarter")
    # Create a bar graph using Plotly with month names on the x-axis
    fig = px.bar(quarterly_data_v,
        x='Quarter',  # Format month names
        y='TransactionCount',
        labels={'x': 'Quarter', 'y': 'Transaction Count'},
        color_discrete_sequence=px.colors.sequential.Aggrnyl,
    )

    fig.update_layout(
        title=f'Bar Graph of Total Transaction Count For Each Quarter',
        xaxis_title='Quarter',
        yaxis_title='Transaction Count'
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
    st.subheader("**Distribution of Transaction Types by Count**")
    fig = px.pie(
        filtered_data, 
        values='Count', 
        names='ProcessType', labels='ProcessType', 
        color_discrete_sequence=px.colors.sequential.Aggrnyl
        )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        title=f'Percentage of Total Transactions for Each Type',
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
def ProcessTypeBarGraph(filtered_data):
    st.subheader("Comparison of Transaction Types by Count Over Time")
    # Pivot the DataFrame to create a suitable format for the grouped bar graph
    pivoted_data = filtered_data.pivot(index=PAYMENT_DATE_COLUMN, columns='ProcessType', values='Count')

    # If there are missing values in the pivoted data, replace them with 0
    pivoted_data = pivoted_data.fillna(0)

    # Create a grouped bar graph using Plotly Express
    fig = px.bar(pivoted_data, x=pivoted_data.index, 
                 y=pivoted_data.columns, 
                 title='Monthly Transaction Type Breakdown', 
                 text='ProcessType',
                 color_discrete_sequence=px.colors.sequential.Aggrnyl
                 )
    
    # Customize the plot
    fig.update_xaxes(title_text='Month')
    fig.update_yaxes(title_text='Transaction Count')
    fig.update_traces(texttemplate='%{text}', textposition='outside')  # Add labels on each bar

    # Use Streamlit to display the Plotly figure
    st.plotly_chart(fig,use_container_width=True)


@st.cache_data
def Grouped_data_dayOfWeek(successful_data_v):
    week_day_name_count = successful_data_v.groupby(['ProcessType_Description', successful_data_v[PAYMENT_DATE_COLUMN].dt.day_name()]).size().reset_index(name='Count')

    return week_day_name_count


def PivotWeekDayPrcessType(week_day_name_count):
    pivoted_Week_data = week_day_name_count.pivot(index=PAYMENT_DATE_COLUMN, columns='ProcessType_Description', values='Count')
    pivoted_Week_data = pivoted_Week_data.fillna(0)

    # pivoted_Week_data['Daily_Total'] = pivoted_Week_data.sum(axis=1)

    return pivoted_Week_data



@st.cache_data
def TopDayOfWeekPlot(grouped_data,ordered_days):
    st.subheader("**Transaction Type Analysis by Day of the Week**")
    fig = px.bar(
        grouped_data, 
        x=PAYMENT_DATE_COLUMN, 
        y='Count', 
        color='ProcessType_Description', 
        labels={'Count': 'Total Count'},
        text='ProcessType_Description',
        category_orders={PAYMENT_DATE_COLUMN: ordered_days} ,
        color_discrete_sequence=px.colors.sequential.Aggrnyl,
        )

    # Customize the layout
    fig.update_layout(
        title='Stacked View of Transaction Types Total Count by Weekday',
        xaxis_title='Day of the Week',
        yaxis_title='Total Count',
        legend=dict(orientation='h', y=-0.2, x=-0.1),
    )
    

    st.plotly_chart(fig, use_container_width=True)


def GrowthTrend(filtered_data):
   # Pivot the DataFrame to create a suitable format for the grouped bar graph
    pivoted_data = filtered_data.pivot(index=PAYMENT_DATE_COLUMN, columns='ProcessType', values='Count')

    # If there are missing values in the pivoted data, replace them with 0
    pivoted_data = pivoted_data.fillna(0)

    monthly_total_counts = pivoted_data.sum(axis=1)
    # Calculate the number of process types (columns) for each month
    # num_process_types = pivoted_data.gt(0).sum(axis=1)  # Count non-zero values (non-missing data)
    num_process_types = pivoted_data.count(axis=1)
    pivoted_data['MonthlyTotalCounts'] = monthly_total_counts
    # pivoted_data['NumProcessTypes'] = num_process_types


    # Calculate the monthly average transaction count
    pivoted_data['MonthlyAverageCounts'] = (monthly_total_counts / num_process_types).round()

    # pivoted_data['PercentageChange'] = 

    pivoted_data['AverageChange'] = pivoted_data['MonthlyAverageCounts'].diff()
    pivoted_data['AverageChange'].iloc[0] = 0


    pivoted_data['PercentageChange'] = ((pivoted_data['MonthlyAverageCounts'] / pivoted_data['MonthlyAverageCounts'].shift(1) - 1) * 100).round()
    pivoted_data['PercentageChange'].iloc[0] = 0  # Set the first value to 0


    return pivoted_data



def growthTrendGraph(pivoted_data_table):
    st.subheader("Comparison of Transaction Counts Over Time")
    # Create a bar graph for the monthly total counts
    bar_fig = px.bar(pivoted_data_table, x=pivoted_data_table.index, y='MonthlyTotalCounts', 
                     title='Monthly Transaction Count', text='MonthlyTotalCounts',   color_discrete_sequence=px.colors.sequential.Aggrnyl)
    
    # Customize the bar graph
    bar_fig.update_xaxes(title_text='Month')
    bar_fig.update_yaxes(title_text='Monthly Total Transaction Count', showline=False)  # Remove the y-axis line
    bar_fig.update_traces(texttemplate='%{text}', textposition='outside')  # Add labels on each bar

    # Use Streamlit to display the bar graph
    st.plotly_chart(bar_fig, use_container_width=True)


def usersTop(processed_data_v,number):
    user_counts = processed_data_v['CompanyName'].value_counts()

    # Sort the user counts in descending order to get the top users
    top_users = user_counts.head(number)  # You can adjust the number to display more or fewer top user

    # Display the top users and their transaction counts
    st.write(f'**Top {number} Companies with the Most Transaction Counts**')
    for i, (user, count) in enumerate(top_users.items(), 1):
        st.write(f'{i}. {user}: **{"{:,.0f}".format(count)}** Transactions')


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

    
    Transaction_types_v = processed_data_v['ProcessType_Description'].nunique()
    process_descriptions = processed_data_v['ProcessType_Description'].unique()
    process_descriptions_str = ', '.join(process_descriptions)



    success_v_percent = str(round(success_v / Total_v * 100, 2))
    un_successful_v_percent = str(round(un_successful_v / Total_v * 100, 2))
    declined_v_percent = str(round(declined_v / Total_v * 100, 2))

    with st.container():

        st.title(f"GAPS Transaction In {selected_year}")
       
        st.markdown("---")
        st.subheader("Metrics")
        col1, col2, col4 = st.columns([1,1,2])

        with col1:
            st.metric(label=f"Total Count ({selected_year})", value=str("{:,.0f}".format(Total_v)))
            st.metric(label=f"Total Transaction Amount ({selected_year})", value=str(humanize.intword(total_amount_v)))

            st.metric(label="Transaction Types", value=str(Transaction_types_v))
            st.write(f"**Transaction Types Labels** ({process_descriptions_str})")
    
        with col2:
            st.metric(label=f"Total Processed Transaction Count ", value=str("{:,.0f}".format(success_v)),delta = f"({success_v_percent} %) of Total Count" )
            st.metric(label=f"Total Un-Processed Transaction Count ", value=str("{:,.0f}".format(un_successful_v)), delta_color="off",delta = f"- ({un_successful_v_percent} %) of Total Count" )
            st.metric(label=f"Total Declined Transaction Count ", value=str( "{:,.0f}".format(declined_v)) , delta = f"- ({declined_v_percent} %) of Total Count" )
        # with col3:
        #     st.metric(label=f"UnDeclined Transaction Count ", value=str("{:,.0f}".format(not_declined_v)), delta = f"+ UnDeclined  - ({undeclined_percent} %)" )
        with col4:
            st.metric(label=f"Total Number of Companies on GAPS", value=str(users_v) )
            # number_to_display = st.slider('Select the number of customers to show', min_value=1, max_value=len(successful_data_v['CompanyName'].unique()), value=10)
            number_to_display = 4
            usersTop(successful_data_v, number_to_display)

    with st.container():
        col2,col1 = st.columns([2,1])
        with col1:
            result = successful_data_v.groupby('ProcessType_Description').agg({
                'CompanyName': 'nunique',  # Count unique company names
                'Amount': 'sum'          # Calculate the sum of Amount
            }).rename(columns={'CompanyName': 'TotalCompanies', 'Amount': 'TotalAmount'})

            st.write(result)

            # desired_process_type = 'GTB'

            # companies_for_desired_process = successful_data_v[successful_data_v['ProcessType_Description'] == desired_process_type]
            # st.write(companies_for_desired_process)
        with col2:
            result_df = {
                'ProcessType_Description': result.index,
                'TotalCompanies': result['TotalCompanies']
            }

            # Create the pie chart
            fig = px.pie(result_df, names='ProcessType_Description', values='TotalCompanies',color_discrete_sequence=px.colors.sequential.Aggrnyl, title='Distribution of Companies by Process Type')
            st.plotly_chart(fig,use_container_width=True)

            st.write("This pie chart illustrates the proportion of companies participating in different process types. Each slice represents a unique process type, and the size of the slice corresponds to the number of companies associated with that process type.")



    with st.container():

        st.header("Transaction Count and Types Analysis")
        
        filtered_table = Filtered_data(successful_data_v)
        pivote_data = GrowthTrend(filtered_table)


        col1, col2 = st.columns([1,2])

        with col1:
            PieChartProcessTypes(filtered_table)

        with col2:
            growthTrendGraph(pivote_data)

    with st.container():

        col1, col2 = st.columns([1,2])
        with col1:
            st.write(pivote_data)
        with col2:          
            ProcessTypeBarGraph(filtered_table)

 

    with st.container():
        st.subheader("Top Day of the Week")

        col1, col2 = st.columns([1,2])
       
        week_day_transaction_count = Grouped_data_dayOfWeek(successful_data_v)

        with col1:
            st.write(PivotWeekDayPrcessType(week_day_transaction_count))

        with col2:
            TopDayOfWeekPlot(week_day_transaction_count, ordered_days)




    with st.container():

        st.subheader('Quarterly Transaction Count Analysis')
        st.write("**An Overview of Transaction Counts by Quarter, Presented Through Bar Graphs and Pie Charts**")
        col1, col2 = st.columns([2,1])

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


        with col1:
            Quarterly_count_bar_graph(quarterly_summary)
            # Monthly_count_bar_graph(successful_data_v)

        with col2:
            Quarterly_Count_Pie_chart(quarterly_summary)
       

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