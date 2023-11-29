import streamlit as st
from LoadData import ExcelHandler


# Create an instance of the ExcelHandler class
excel_handler = ExcelHandler()
successful_data_v = st.session_state.successful_data_v
data = file_session_csv = st.session_state.excel_data
success_v = st.session_state.success_v
declined = st.session_state.declined

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