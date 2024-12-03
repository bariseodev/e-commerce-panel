import os
import streamlit as st
import pandas as pd
from pages.scripts.ecommerce_scraper import ImitationScraper, GemstoneScraper, TrendyolScraper


def show_ecommerce_scraper_page():
    st.header("E-commerce Scraper Modülü")

    # Dropdown to select which website to scrape
    scraper_type = st.selectbox("Webste Tipini Seçin", ("Imitation Scraper", "Gemstone Scraper", "Trendyol Scraper"))

    # Input fields for URL, pages, and file upload
    url_input = st.text_input("Ürün URL'i girin:", placeholder="https://example.com/product")
    pages_input = st.number_input("Sayfa Sayısı", min_value=1, max_value=200, value=1)
    file_upload = st.file_uploader("Ya da URL'leri içeren bir Excel tablosu yükleyin (.xlsx formatı)", type=["xlsx"])

    # Step 1: Extract Links
    if st.button("Extract Product Links"):
        if scraper_type == "Trendyol Scraper" and url_input:
            st.info("Extracting product links... Please wait.")
            try:
                # Create an instance of TrendyolScraper to extract product links
                scraper = TrendyolScraper(url_input, pages_input)
                scraper.extract_links()  # Call the method for extracting links
                st.success(f"Product links extraction completed for {url_input}.")
            except Exception as e:
                st.error(f"An error occurred while extracting product links from Trendyol: {e}")
        elif scraper_type != "Trendyol Scraper" and url_input:
            st.warning(f"Please select Trendyol Scraper to extract links.")
        else:
            st.warning("Please enter a valid URL for link extraction.")

    # Step 2: Retrieve Product Details
    if st.button("Retrieve Product Details"):
        if scraper_type == "Trendyol Scraper":
            st.info("Retrieving product details... Please wait.")
            try:
                # Create an instance of TrendyolScraper to retrieve product details
                scraper = TrendyolScraper(url_input, pages_input)
                scraper.retrieve_product_details()  # Call the method for retrieving product details
                st.success(f"Product details retrieval completed for {url_input}.")
            except Exception as e:
                st.error(f"An error occurred while retrieving product details from Trendyol: {e}")
        elif scraper_type != "Trendyol Scraper" and url_input:
            st.warning(f"Please select Trendyol Scraper to retrieve product details.")
        else:
            st.warning("Please enter a valid URL for retrieving product details.")

    # Handle other scrapers (ImitationScraper, GemstoneScraper)
    elif url_input:
        st.info("Scraping in progress... Please wait.")
        try:
            if scraper_type == "Imitation Scraper":
                scraper = ImitationScraper(url_input)
            else:
                scraper = GemstoneScraper(url_input)

            scraper.scrape()
            st.success(f"Scraping completed successfully for {url_input}.")
        except Exception as e:
            st.error(f"An error occurred while scraping {url_input}: {e}")

    # Process URLs from the uploaded file
    elif file_upload:
        try:
            # Process URLs from the uploaded file
            file_df = pd.read_excel(file_upload)
            urls = file_df['URLs'].dropna().tolist()

            st.info(f"{len(urls)} URLs found. Scraping in progress...")

            for url in urls:
                if scraper_type == "Imitation Scraper":
                    scraper = ImitationScraper(url)
                elif scraper_type == "Gemstone Scraper":
                    scraper = GemstoneScraper(url)
                else:
                    scraper = TrendyolScraper(url, pages_input)

                scraper.scrape()
                st.success(f"Scraping completed for {url}")
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")

    else:
        st.warning("Bir URL girin ya da URL'leri içeren bir Excel dosyası yükleyin.")

    # Provide a download button for the Excel file
    if os.path.exists('scraped_data.xlsx'):
        st.write("### Ürün Veri Tablosunu İndir")
        st.download_button("Excel Dosyasını İndir", 'scraped_data.xlsx', file_name='scraped_data.xlsx')


# Show the e-commerce scraper page
show_ecommerce_scraper_page()
