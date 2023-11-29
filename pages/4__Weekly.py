import streamlit as st
from LoadData import ExcelHandler
import plotly_express as px 
import pandas as pd

# Create an instance of the ExcelHandler class
excel_handler = ExcelHandler()

PAID_DATE_COLUMN = "PaidDate"
PAYMENT_DATE_COLUMN = "PaymentDate"
ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


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



with st.container():
    st.subheader("Top Day of the Week")

    col1, col2 = st.columns([1,2])
    successful_data_v = st.session_state.successful_data_v
    
    week_day_transaction_count = Grouped_data_dayOfWeek(successful_data_v)

    with col1:
        st.write(PivotWeekDayPrcessType(week_day_transaction_count))

    with col2:
        TopDayOfWeekPlot(week_day_transaction_count, ordered_days)