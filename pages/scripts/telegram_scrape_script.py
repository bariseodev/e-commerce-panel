import asyncio
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
import openpyxl
import re
import os

api_id = '22212468'  # Replace with your own API ID
api_hash = 'acb50cf1727d879901881360ed7f4b0d'  # Replace with your own API hash

# Folder where the images will be saved
image_folder = 'images'

PROJECTS_DIR = "projects"


def project_selection():
    """Reusable project selection logic."""
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]

    if not projects:
        st.error("No projects found! Please add projects to the /projects folder.")
        return None

    if "selected_project" not in st.session_state:
        st.session_state["selected_project"] = projects[0]

    selected_project = st.sidebar.selectbox(
        "Select Project",
        options=projects,
        index=projects.index(st.session_state["selected_project"]),
    )
    st.session_state["selected_project"] = selected_project

    st.sidebar.write(f"**Selected Project:** {selected_project}")
    return selected_project

if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Function to write to Excel
def write_to_excel(product_name, description, images, price, size, original_description, output_file):
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)

    try:
        workbook = openpyxl.load_workbook(output_file)
        sheet = workbook.active
    except FileNotFoundError:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        # Write headers if the file does not exist
        sheet['A1'] = 'Product Name'
        sheet['B1'] = 'Size'
        sheet['C1'] = 'Product Description'
        sheet['D1'] = 'Price'
        sheet['E1'] = 'Images'
        sheet['F1'] = 'Original Description'

    # Append the new data
    row = [product_name, size, description, price, ', '.join(images), original_description]
    sheet.append(row)

    # Save the workbook
    workbook.save(output_file)
    print(f"Written to Excel: {product_name}, {size}, {description} -> {price} -> {', '.join(images)}")

# Function to extract price from the description
def extract_price(description):
    # Adjusted regular expression to capture price at the end
    match = re.search(r'(\d+)(?:[^\d]*\$)', description)
    if match:
        # Return price including the $ symbol
        return f"${match.group(1)}"
    return None  # Return None if no price is found

# Function to extract size (second row)
def extract_size(description):
    # Split the description into lines and extract the second line (size)
    lines = description.split('\n')
    if len(lines) >= 2:
        return lines[1]  # Return the second line (size)
    return None  # Return None if size is not found

async def scrape_group_to_excel(chat_name, message_limit, start_from_latest=True, output_file=None):
    async with TelegramClient('session_name', api_id, api_hash) as client:
        group = await client.get_entity(chat_name)  # Replace with your group's username

        if start_from_latest:
            print("Starting from the latest messages.")
            offset_id = None
        else:
            print("Calculating offset to start from a specific point.")
            # Retrieve messages to determine offset
            messages = await client.get_messages(group, limit=message_limit)
            if not messages:
                print("No messages found in the group.")
                return
            offset_id = messages[-1].id  # Use the ID of the oldest message in this batch

        # Ensure offset_id is used only if valid
        if offset_id is not None:
            print(f"Starting from message ID: {offset_id}")
            messages = await client.get_messages(group, offset_id=offset_id, limit=message_limit)
        else:
            messages = await client.get_messages(group, limit=message_limit)

        image_messages = []
        descriptions = []

        for message in messages:
            try:
                if message.media and isinstance(message.media, MessageMediaPhoto):
                    photo = message.media.photo
                    image_file_name = f'{os.path.dirname(output_file)}/downloaded_image_{message.id}.jpg'
                    image_messages.append(os.path.basename(image_file_name))
                    await message.download_media(image_file_name)
                    print(f"Downloaded image: {image_file_name}")

                elif message.text and image_messages:
                    descriptions.append(message.text)
                    print(f"Description for images: {message.text}")

                    product_name = descriptions[-1].split('\n')[0]
                    product_description = '\n'.join(descriptions[-1].split('\n')[1:])
                    price = extract_price(product_description)
                    size = extract_size(product_description)
                    original_description = descriptions[-1]
                    print(f"Output file path: {output_file}")

                    #WRITE TO EXCEL
                    write_to_excel(product_name, product_description, image_messages, price, size, original_description, output_file)

                    image_messages = []  # Reset image list

            except Exception as e:
                print(f"Error processing message {message.id}: {e}")
                continue

            await asyncio.sleep(1)  # 1-second delay between processing messages

        print("Finished scraping messages.")
#if __name__ == '__main__':
#    asyncio.run(scrape_group_to_excel(start_from_latest=True))