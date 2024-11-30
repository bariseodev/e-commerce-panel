import asyncio
import streamlit as st
import sys
import os
from scripts.telegram_scrape_script import scrape_group_to_excel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def show_telegram_scraper_page():
    st.header("Telegram Scraper Modülü")
    st.write("Veri çekmek istediğiniz grubun ismini aşağıya yazınız ve Scrape butonuna basınız.")

    chat_name = st.text_input("chat/group username gir:", placeholder="@example_chat", key="chat_name_input")
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
                async def run_scraper():
                    output_dir = os.path.join(project_path, "scraper_outputs")
                    os.makedirs(output_dir, exist_ok=True)

                    output_file = os.path.join(output_dir, f"{chat_name}_scraped_data.xlsx")

                    # Call the scraper function and pass the output file path
                    await scrape_group_to_excel(chat_name=chat_name, message_limit=message_limit, output_file=output_file)
                    st.success(f"Scraping completed successfully! Data saved to {output_file}")

                # Run the scraper asynchronously
                asyncio.create_task(run_scraper())


            except Exception as e:
                # Handle any exceptions during scraping
                st.error(f"An error occurred: {e}")

# Show the telegram scraper page
show_telegram_scraper_page()
