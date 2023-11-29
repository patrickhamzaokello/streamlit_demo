import streamlit as st
import pandas as pd

class ExcelHandler:
    def __init__(self):
        # Check if 'excel_data' is in session_state, if not, initialize it
        if 'excel_data' not in st.session_state:
            st.session_state.excel_data = None

        self.PAID_DATE_COLUMN = "PaidDate"
        self.PAYMENT_DATE_COLUMN = "PaymentDate"

    def load_excel_file(self):
        uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"], label_visibility="collapsed")

        if uploaded_file is not None:
            data =  pd.read_csv(uploaded_file)
            data[self.PAID_DATE_COLUMN] = pd.to_datetime(data[self.PAID_DATE_COLUMN], format='mixed')
            data[self.PAYMENT_DATE_COLUMN] = pd.to_datetime(data[self.PAYMENT_DATE_COLUMN], format='ISO8601')
            st.session_state.excel_data = data
            return st.session_state.excel_data
        return None

    def view_data(self):
        if st.session_state.excel_data is not None:
            st.write("### Raw Data Overview")
            st.write(st.session_state.excel_data)
        else:
            st.warning("Missing Data, Please Add Data source.")

