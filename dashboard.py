import streamlit as st
import pandas as pd
import numpy as np
import calendar
import plotly_express as px 
import humanize

from LoadData import ExcelHandler


excel_handler = ExcelHandler()


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
PAID_DATE_COLUMN = "PaidDate"
PAYMENT_DATE_COLUMN = "PaymentDate"


st.sidebar.divider()

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



def usersTop(processed_data_v,number):
    user_counts = processed_data_v['CompanyName'].value_counts()

    # Sort the user counts in descending order to get the top users
    top_users = user_counts.head(number)  # You can adjust the number to display more or fewer top user

    # Display the top users and their transaction counts
    st.write(f'**Top {number} Companies with the Most Transaction Counts**')
    for i, (user, count) in enumerate(top_users.items(), 1):
        st.write(f'{i}. {user}: **{"{:,.0f}".format(count)}** Transactions')




def buildDashboard(file_raw_data):
    data = file_raw_data
    clean_data = processed_data(file_raw_data)
    year_options = sorted(clean_data[PAYMENT_DATE_COLUMN].dt.year.unique())
    default_year = 2022
    selected_year = st.sidebar.selectbox("Select a Year", year_options, index=year_options.index(default_year))

    processed_data_v = selectDataYear(selected_year, clean_data)

    Total_v = len(processed_data_v)
    total_amount_v = processed_data_v['Amount'].sum()
    users_v = processed_data_v['CompanyName'].str.strip().nunique()



    successful_data_v = successfulTransaction(processed_data_v)
    st.session_state.successful_data_v = successful_data_v

    declined = declinedTransactions(processed_data_v)
    st.session_state.declined = declined
    not_declined = notDeclined(processed_data_v)


   
    success_v = len(successful_data_v)
    st.session_state.success_v = success_v
   

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




if st.session_state.excel_data is not None:
    st.sidebar.success("Data is Loaded")

file_upload_csv = excel_handler.load_excel_file()
file_session_csv = st.session_state.excel_data

if file_session_csv is not None:
    st.write("session")
    buildDashboard(file_session_csv)
else:
    if file_upload_csv is not None:
        st.sidebar.success("Upload A CSV File to Begin Analysis")
        buildDashboard(file_upload_csv)
