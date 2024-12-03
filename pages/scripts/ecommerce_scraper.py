import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import pandas as pd
import subprocess
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class BaseScraper:
    def __init__(self, url):
        self.url = url
        self.data = {}

    def fetch_page(self):
        response = requests.get(self.url)
        response.raise_for_status()
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def parse_field(self, selector):
        pass

    def save_image(self, img_url, img_name, img_index):
        try:
            response = requests.get(img_url)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))

            if not os.path.exists('images'):
                os.makedirs('images')

            # Save the image with the specified name
            image_filename = f"{img_name}.jpg"
            image_path = f'images/{image_filename}'
            image.save(image_path)

            # Store only the image filename in data (not the full path)
            self.data[f'image_{img_index}'] = image_filename
        except Exception as e:
            print(f"Error saving image: {e}")

    def save_to_excel(self):
        # Define the file path
        file_path = 'scraped_data.xlsx'

        # Convert data to a DataFrame
        df = pd.DataFrame([self.data])

        # Save to Excel, appending if the file already exists
        if os.path.exists(file_path):
            existing_df = pd.read_excel(file_path)
            df = pd.concat([existing_df, df], ignore_index=True)

        df.to_excel(file_path, index=False)
        print(f"Data saved to {file_path}")

    def scrape(self):
        self.fetch_page()
        self.parse_field()
        self.save_to_excel()


class ImitationScraper(BaseScraper):
    def parse_field(self):
        # Retrieve product name
        name_element = self.soup.find('h1')
        self.data['name'] = name_element.get_text(strip=True) if name_element else 'No name available'

        # Retrieve price
        price_element = self.soup.find('p', class_='price product-page-price price-on-sale')
        self.data['price'] = price_element.find('ins').get_text(strip=True) if price_element and price_element.find(
            'ins') else 'No price available'

        # Retrieve category
        category_element = self.soup.find('span', class_='posted_in')
        self.data['category'] = category_element.find('a').get_text(
            strip=True) if category_element else 'No category available'

        # Retrieve description
        description_element = self.soup.find('div',
                                             class_='woocommerce-Tabs-panel woocommerce-Tabs-panel--description panel entry-content active')
        self.data['description'] = description_element.get_text(
            strip=True) if description_element else 'No description available'

        # Retrieve dimensions from product-short-description
        dimensions_element = self.soup.find('div', class_='product-short-description')
        if dimensions_element:
            # Preserve line spacing
            self.data['dimensions'] = dimensions_element.get_text(separator='\n',
                                                                  strip=True)  # Use '\n' as the separator to maintain line breaks
        else:
            self.data['dimensions'] = 'No dimensions available'

        # Retrieve and save images
        image_divs = self.soup.select('.woocommerce-product-gallery__image')
        for i, div in enumerate(image_divs):
            img_url = div.find('img')['data-large_image']
            img_name = f"{self.data['name'].replace(' ', '_')}_{i + 1}"
            self.save_image(img_url, img_name, img_index=i + 1)


class GemstoneScraper(BaseScraper):
    def parse_field(self):
        # Store the page URL for reference
        self.data['url'] = self.url

        # Handle Turkish characters and retrieve product title
        title_element = self.soup.find('h1')
        self.data['product_title'] = title_element.get_text(strip=True).replace('\t',
                                                                                ' ') if title_element else 'No title available'

        # Retrieve price
        price_element = self.soup.find('div', class_='font-size-25 font-weight-bold main-purple-color product-price')
        self.data['price'] = price_element.get_text(strip=True) if price_element else 'No price available'

        # Retrieve short description
        short_desc_element = self.soup.find('div', class_='product-description mt-4')
        self.data['short_desc'] = short_desc_element.get_text(
            strip=True) if short_desc_element else 'No short description available'

        # Retrieve full description
        description_element = self.soup.find('div', class_='py-3 border-0')
        self.data['description'] = description_element.get_text(
            strip=True) if description_element else 'No description available'

        # Retrieve additional information as a dictionary
        additional_info_table = self.soup.find('table', class_='table table-striped')
        self.data['additional_info'] = {}
        if additional_info_table:
            rows = additional_info_table.find_all('tr')
            for row in rows:
                key = row.find('th', class_='text-muted')
                value = row.find('td')
                if key and value:
                    self.data['additional_info'][key.get_text(strip=True)] = value.get_text(strip=True)

        self.data['images'] = []
        parent_div = self.soup.find('div', class_='col-md-5 h-100 py-2')
        if parent_div:
            slick_items = parent_div.find_all('div', class_='slick-item pd-image-item zoom')
            for slick_item in slick_items:
                img_url = slick_item.get('data-zoom-img')
                if img_url:
                    self.data['images'].append(img_url)

        if len(self.data['images']) > 1:
            for index, i in enumerate(self.data['images']):
                img_name = f"{self.data['product_title'].replace(' ', '_')}_{index + 1}"
                self.save_image(i, img_name, img_index=index + 1)
        elif len(self.data['images']) == 1:
            img_name = f"{self.data['product_title'].replace(' ', '_')}_{1}"
            self.save_image(self.data['images'][0], img_name, img_index=1)
        else:
            pass

class TrendyolScraper:
    def __init__(self, url, pages=1):
        self.url = url
        self.pages = pages
        self.driver = None

    def setup_driver(self):
        # Setup Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0"
        chrome_options.add_argument(f"user-agent={user_agent}")

        chrome_service = Service("C:/chromedriver.exe")  # Update this with the correct path
        self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)


    def extract_links(self):
        """Extract product links from the search results."""
        if not self.driver:
            self.setup_driver()

        all_product_links = []
        try:
            for i in range(1, self.pages + 1):
                print(f"Extracting from page {i}...")
                page_url = f"{self.url}?pi={i}"
                self.driver.get(page_url)
                time.sleep(3)  # Wait for the page to load fully

                product_cards = self.driver.find_elements(By.CLASS_NAME, "p-card-wrppr")
                for card in product_cards:
                    try:
                        link_element = card.find_element(By.CSS_SELECTOR, "div.p-card-chldrn-cntnr.card-border a")
                        link = link_element.get_attribute("href")
                        all_product_links.append(link)
                    except Exception as e:
                        print(f"Error extracting link: {e}")
        except Exception as e:
            print(f"Error during link extraction: {e}")
        finally:
            self.driver.quit()
        output_directory = os.path.join("pages", "scripts")
        output_file_path = os.path.join(output_directory, "product_links.txt")

        # Save the links to the specified file
        with open(output_file_path, "w") as f:
            for link in set(all_product_links):
                f.write(link + "\n")
        print(f"Extracted {len(all_product_links)} links")

    def retrieve_product_details(self):
        """Retrieve product details for each link and save to an Excel file."""
        if not self.driver:
            self.setup_driver()

        input_directory = os.path.join("pages", "scripts")
        input_file_path = os.path.join(input_directory, "product_links.txt")

        # Load product links from the file
        with open(input_file_path, "r") as f:
            product_links = [line.strip() for line in f]

        # Prepare the DataFrame for storing product details
        columns = ['Ürün Adı', 'Fiyat', 'Satıcı', 'Kategori', 'Kategori ID', 'Ürün Kodu', 'Görseller']
        df = pd.DataFrame(columns=columns)

        for j, product_link in enumerate(product_links):
            try:
                print(f"Processing product {j + 1}: {product_link}")
                self.driver.get(product_link)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//script[@type="application/ld+json"]'))
                )

                # Extract JSON-LD data
                try:
                    script_tag = self.driver.find_element(By.XPATH, '//script[@type="application/ld+json"]')
                    json_data = script_tag.get_attribute("innerHTML")
                    product_data = json.loads(json_data)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON for {product_link}: {e}")
                    continue
                except Exception as e:
                    print(f"Error extracting JSON data for {product_link}: {e}")
                    continue

                # Parse product details from JSON
                product_name = product_data.get("name", "Not Available")
                price = product_data.get("offers", {}).get("price", "Not Available")
                price_currency = product_data.get("offers", {}).get("priceCurrency", "Not Available")
                merchant = product_data.get("offers", {}).get("seller", {}).get("name", "Not Available")
                category = product_data.get("category", "Not Available")
                category_id = product_data.get("offers", {}).get("categoryID", "Not Available")
                product_code = product_data.get("sku", "Not Available")

                # Extract images
                images = product_data.get("image", [])
                image_urls = []
                if isinstance(images, list):
                    image_urls = [str(img) for img in images if isinstance(img, str)]
                elif isinstance(images, dict) and "contentUrl" in images:
                    image_urls.append(str(images["contentUrl"]))
                image_urls_str = ", ".join(image_urls)

                # Save product details into the DataFrame
                product_details = pd.DataFrame([{
                    'Ürün Adı': product_name,
                    'Fiyat': f"{price} {price_currency}",
                    'Satıcı': merchant,
                    'Kategori': category,
                    'Kategori ID': category_id,
                    'Ürün Kodu': product_code,
                    'Görseller': image_urls_str
                }])
                df = pd.concat([df, product_details], ignore_index=True)

                # Save to Excel after each iteration
                df.to_excel("product_details.xlsx", index=False, engine="openpyxl")
                print(f"Product {product_name} saved successfully.")

            except Exception as e:
                print(f"Error processing {product_link}: {e}")
                continue

        # Final cleanup
        self.driver.quit()
        print(f"Total products processed: {len(df)}")
        print("Details saved to product_details.xlsx")


def process_urls_from_excel():
    # Read URLs from urls.xlsx
    try:
        urls_df = pd.read_excel('urls.xlsx')
        urls = urls_df['URLs'].dropna().tolist()  # Assuming the column header is 'URLs'

        print(f"Found {len(urls)} URLs to process.")

        for url in urls:
            print(f"Processing: {url}")
            scraper = GemstoneScraper(url)
            scraper.scrape()
    except FileNotFoundError:
        print("Error: 'urls.xlsx' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
