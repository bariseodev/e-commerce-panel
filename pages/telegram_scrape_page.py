import asyncio
import streamlit as st
import sys
import os

# Add the path to your script folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from telegram_scrape_script import scrape_group_to_excel

def show_telegram_scraper_page():
    st.header("Telegram Scraper Modülü")
    st.write("Veri çekmek istediğiniz grubun ismini aşağıya yazınız ve Scrape butonuna basınız.")

    # User input
    chat_name = st.text_input("Enter the chat/group username:", placeholder="@example_chat")
    message_limit = st.slider("Number of messages to scrape:", 10, 500, 100)

    # Scrape button and action
    if st.button("Scrape"):
        if not chat_name:
            st.warning("Please enter a chat/group username.")
        else:
            st.info("Scraping in progress... Please wait.")
            try:
                # Define a wrapper function for async task
                async def run_scraper():
                    await scrape_group_to_excel(chat_name=chat_name, message_limit=message_limit)

                # Run the scraper asynchronously
                asyncio.run(run_scraper())
                st.success("Scraping completed successfully!")

            except Exception as e:
                # Handle any exceptions during scraping
                st.error(f"An error occurred: {e}")

show_telegram_scraper_page()