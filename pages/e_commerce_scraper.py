import streamlit as st

def show_e_commerce_scraper():
    st.header("Data Processing Page")
    st.write("Welcome to the Data Processing section. Here, you can upload and process your data.")

    # Example content for Data Processing
    uploaded_file = st.file_uploader("Upload a file for processing:")
    if uploaded_file:
        st.write(f"File `{uploaded_file.name}` uploaded successfully!")

show_e_commerce_scraper()