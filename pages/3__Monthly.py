import streamlit as st
from LoadData import ExcelHandler


# Create an instance of the ExcelHandler class
excel_handler = ExcelHandler()

if st.sidebar.button('View Data'):
    excel_handler.view_data()