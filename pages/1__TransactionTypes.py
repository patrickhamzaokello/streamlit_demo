import streamlit as st
from LoadData import ExcelHandler
import plotly_express as px 

# Create an instance of the ExcelHandler class
excel_handler = ExcelHandler()



PAID_DATE_COLUMN = "PaidDate"
PAYMENT_DATE_COLUMN = "PaymentDate"

@st.cache_data
def BarChartProcessTypes(filtered_data):
    st.subheader("**Distribution of Transaction Types by Percent**")
    
    # Calculate the percentage for each process type
    filtered_data['Percentage'] = (filtered_data['Count'] / filtered_data['Count'].sum()) * 100
    
    # Group by 'ProcessType' to get total percentage for each category
    total_percentages = filtered_data.groupby('ProcessType')['Percentage'].sum().reset_index()
    
    # Sort the data in descending order by 'Percentage'
    total_percentages = total_percentages.sort_values(by='Percentage', ascending=False)
    
    # Create a horizontal bar chart using Plotly Express
    fig = px.bar(
        total_percentages,
        x='Percentage',  # Use percentage as the x-axis
        y='ProcessType',  # Use processType as the y-axis
        orientation='h',  # Set orientation to horizontal
        text=total_percentages['Percentage'].apply(lambda x: f'{x:.2f}%'),  # Display the percentage with 2 decimal points and %
        color='ProcessType',  # Use the same color for all bars
        color_discrete_sequence=px.colors.sequential.Aggrnyl
    )
    
    # Updating layout properties
    fig.update_layout(
        title='Total Percentage of Transactions for Each Type',
        xaxis_title='Total Percentage',
        yaxis_title='ProcessType',
        showlegend=False,  # Hide the legend for better clarity
    )
    
    # Displaying the horizontal bar chart using Streamlit
    st.plotly_chart(fig, use_container_width=True)

def growthTrendGraph(pivoted_data_table):
    st.subheader("Comparison of Transaction Counts Over Time")

    # Create a line graph for the monthly total counts with markers
    line_fig = px.line(
        pivoted_data_table, 
        x=pivoted_data_table.index, 
        y='MonthlyAverageCounts', 
        title='Monthly Average Transaction Count Over Time', 
        labels={'MonthlyAverageCounts': 'Monthly Average Count'},
        line_shape="linear",  # You can change the line shape (e.g., 'linear', 'spline', 'hv', etc.)
        color_discrete_sequence=px.colors.sequential.Redor_r,
        text='MonthlyAverageCounts',  # Display the 'AverageChange' values as labels
        markers=True,  # Add markers at each data point
    )
    
    # Add horizontal lines for maximum and minimum counts
    max_count = pivoted_data_table['MonthlyAverageCounts'].max()
    min_count = pivoted_data_table['MonthlyAverageCounts'].min()
    avg_count = pivoted_data_table['MonthlyAverageCounts'].mean()
    
    line_fig.add_shape(
        type='line',
        x0=pivoted_data_table.index.min(),
        x1=pivoted_data_table.index.max(),
        y0=max_count,
        y1=max_count,
        line=dict(color='gray', dash='dash'),
    )
    
    line_fig.add_shape(
        type='line',
        x0=pivoted_data_table.index.min(),
        x1=pivoted_data_table.index.max(),
        y0=min_count,
        y1=min_count,
        line=dict(color='gray', dash='dash'),
    )

    line_fig.add_shape(
        type='line',
        x0=pivoted_data_table.index.min(),
        x1=pivoted_data_table.index.max(),
        y0=avg_count,
        y1=avg_count,
        line=dict(color='green', dash='dash'),
    )
    
    # Add annotations for the maximum and minimum counts at the end of the lines
    line_fig.add_annotation(
        x=pivoted_data_table.index.max(),
        y=max_count,
        text=f'Max Count: {max_count}',
        showarrow=True,
        arrowhead=5,
        ax=80,
        ay=0,
    )
    
    line_fig.add_annotation(
        x=pivoted_data_table.index.max(),
        y=min_count,
        text=f'Min Count: {min_count}',
        showarrow=True,
        arrowhead=5,
       ax=80,
        ay=0,
    )

    line_fig.add_annotation(
        x=pivoted_data_table.index.max(),
        y=avg_count,
        text=f'Average Count: {avg_count:.2f}',
        showarrow=True,
        arrowhead=5,
        ax=80,
        ay=0,
    )
    
    # Update the trace to set the text position on top of the points
    line_fig.update_traces(textposition='top center')
    
    # Customize the line graph
    line_fig.update_xaxes(title_text='Month')
    line_fig.update_yaxes(title_text=None, showline=False, showticklabels=False)  # Remove the y-axis line
    
    # Use Streamlit to display the line graph
    st.plotly_chart(line_fig, use_container_width=True)

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

with st.container():

    st.header("Transaction Count and Types Analysis")
    
    filtered_table = Filtered_data(st.session_state.successful_data_v)
    pivote_data = GrowthTrend(filtered_table)


    col1, col2 = st.columns([1,1])

    with col1:
        BarChartProcessTypes(filtered_table)

    with col2:
        growthTrendGraph(pivote_data)

with st.container():

    col1, col2 = st.columns([1,2])
    with col1:
        st.write(pivote_data)
    with col2:          
        ProcessTypeBarGraph(filtered_table)