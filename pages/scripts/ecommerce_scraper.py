import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import pandas as pd


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
