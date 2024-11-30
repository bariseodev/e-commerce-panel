import asyncio
import streamlit as st
from pages.scripts.telegram_scrape_script import scrape_group_to_excel
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def show_telegram_scraper_page():
    st.header("Telegram Scraper Modülü")
    st.write("Veri çekmek istediğiniz grubun ismini aşağıya yazınız ve Scrape butonuna basınız.")

    chat_name = st.text_input("chat/group username gir:", placeholder="@example_chat", key="chat_name_input_1")
    message_limit = st.slider("Mesaj sayısı:", 10, 500, 100)

    if "project_path" not in st.session_state:
        st.error("No project selected. Please select a project in the sidebar.")
        return

    project_path = st.session_state["project_path"]

    if st.button("Scrape"):
        if not chat_name:
            st.warning("Please enter a chat/group username.")
        else:
            st.info("Scraping in progress... Please wait.")
            try:
                # We directly await the asynchronous function using asyncio.run
                output_dir = os.path.join(project_path, "scraper_outputs")
                os.makedirs(output_dir, exist_ok=True)

                output_file = os.path.abspath(os.path.join(project_path, "scraper_outputs", f"{chat_name}_scraped_data.xlsx"))
                print(f"Output file will be saved to: {output_file}")

                # Call the scraper function and pass the output file path
                asyncio.run(scrape_group_to_excel(chat_name=chat_name, message_limit=message_limit, output_file=output_file))

                st.success(f"Scraping completed successfully! Data saved to {output_file}")

            except Exception as e:
                # Handle any exceptions during scraping
                st.error(f"An error occurred: {e}")

# Show the telegram scraper page
show_telegram_scraper_page()
