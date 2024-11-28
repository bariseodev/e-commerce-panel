import streamlit as st
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'pages/scripts'))


from pages.telegram_scrape_page import show_telegram_scraper_page

st.title('🦙 LLAMA Scraper 🦙')

st.sidebar.title("Menu")

page = st.sidebar.radio(
    "",
    ["E-Commerce Scraper", "Telegram-Scraper", "Stock Control"]
)
