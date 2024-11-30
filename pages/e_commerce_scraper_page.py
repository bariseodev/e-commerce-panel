import os
import streamlit as st
import pandas as pd
from pages.scripts.ecommerce_scraper import ImitationScraper, GemstoneScraper  # Import your scraper classes


def show_ecommerce_scraper_page():
    st.header("E-commerce Scraper Modülü")

    # Dropdown to select which website to scrape
    scraper_type = st.selectbox("Webste Tipini Seçin", ("Imitation Scraper", "Gemstone Scraper"))

    # Input fields for URL and file upload
    url_input = st.text_input("Ürün URL'i girin:", placeholder="https://example.com/product")
    file_upload = st.file_uploader("Ya da URL'leri içeren bir Excel tablosu yükleyin (.xlsx formatı)", type=["xlsx"])

    if st.button("Scrape"):
        if url_input:
            # Scrape single URL based on selected scraper type
            st.info("Scraping in progress... Please wait.")
            try:
                if scraper_type == "Imitation Scraper":
                    scraper = ImitationScraper(url_input)
                else:  # Default to GemstoneScraper if not Imitation Scraper
                    scraper = GemstoneScraper(url_input)

                scraper.scrape()
                st.success(f"Scraping completed successfully for {url_input}.")
            except Exception as e:
                st.error(f"An error occurred while scraping {url_input}: {e}")
        elif file_upload:
            # Process multiple URLs from Excel
            try:
                # Load the uploaded Excel file
                file_df = pd.read_excel(file_upload)
                urls = file_df['URLs'].dropna().tolist()  # Assuming the column header is 'URLs'

                st.info(f"{len(urls)} URL Bulundu. Scraper çalışıyor...")

                # Scrape each URL from the uploaded file
                for url in urls:
                    try:
                        if scraper_type == "Imitation Scraper":
                            scraper = ImitationScraper(url)
                        else:  # Default to GemstoneScraper if not Imitation Scraper
                            scraper = GemstoneScraper(url)

                        scraper.scrape()
                        st.success(f"Scrape işlemi tamamlandı: {url}")
                    except Exception as e:
                        st.error(f"An error occurred while scraping {url}: {e}")
            except Exception as e:
                st.error(f"An error occurred while processing the file: {e}")
        else:
            st.warning("Bir URL girin ya da URL'leri içeren bir Excel dosyası yükleyin.")

    # Show a link to the saved Excel file if it exists
    if os.path.exists('scraped_data.xlsx'):
        st.write("### Ürün Veri Tablosunu İndir")
        st.download_button("Excel Dosyasını İndir", 'scraped_data.xlsx', file_name='scraped_data.xlsx')


# Show the e-commerce scraper page
show_ecommerce_scraper_page()
