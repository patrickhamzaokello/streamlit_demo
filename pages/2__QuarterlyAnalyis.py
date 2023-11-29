import streamlit as st
from LoadData import ExcelHandler
import plotly_express as px 
import pandas as pd

# Create an instance of the ExcelHandler class
excel_handler = ExcelHandler()

PAID_DATE_COLUMN = "PaidDate"
PAYMENT_DATE_COLUMN = "PaymentDate"

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



with st.container():

    st.subheader('Quarterly Transaction Count Analysis')
    st.write("**An Overview of Transaction Counts by Quarter, Presented Through Bar Graphs and Pie Charts**")
    col1, col2 = st.columns([2,1])

    successful_data_v = st.session_state.successful_data_v

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
       