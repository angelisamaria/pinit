import requests
import json
from PIL import Image
from io import BytesIO
import os
        
# Pinterest API credentials
API_BASE_URL = "https://api.pinterest.com/v5"
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
BOARD_ID = os.environ.get("BOARD_ID")

# Niche keywords and trusted domains
NICHE_KEYWORDS = ['decor', 'modern', 'interior', 'furniture']
TRUSTED_DOMAINS = ['pinterest.com', 'etsy.com', 'amazon.com', 'wayfair.com']

# Filter thresholds
MIN_SAVES = 500

# Function to fetch pins
def fetch_pins():
    url = f"{API_BASE_URL}/pins"
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}', 'Content-Type': 'application/json',
    'Accept': 'application/json',}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses 
    return response.json()

# Function to check pin relevance
def is_relevant_pin(pin):
    # Extract pin details
    title = pin.get('title', '').lower()
    description = pin.get('description', '').lower()
    link = pin.get('link', '')
    saves = pin.get('saves', 0)

    # Keyword relevance
    keyword_match = any(keyword in title or keyword in description for keyword in NICHE_KEYWORDS)

    # Source credibility
    credible_source = any(domain in link for domain in TRUSTED_DOMAINS)

    # Engagement check
    high_engagement = saves >= MIN_SAVES

    # Aspect ratio check (vertical format)
    image_url = pin.get('image', {}).get('original', {}).get('url', '')
    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        width, height = img.size
        is_vertical = height > width and width / height >= 0.6
    except Exception as e:
        print(f"Image processing failed: {e}")
        is_vertical = False

    # Return True if all conditions are met
    return keyword_match and credible_source and high_engagement and is_vertical

# Function to choose the top pin
def choose_top_pin(pins):
    # Filter relevant pins
    relevant_pins = [pin for pin in pins if is_relevant_pin(pin)]

    # Sort by saves (highest first)
    sorted_pins = sorted(relevant_pins, key=lambda x: x.get('saves', 0), reverse=True)

    # Return the top pin
    return sorted_pins[0] if sorted_pins else None

# Function to pin to a board
def pin_to_board(pin):
    url = f"{API_BASE_URL}/boards/{BOARD_ID}/pins"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {
        "link": pin.get("link"),
        "title": pin.get("title"),
        "description": pin.get("description"),
        "image_url": pin.get("image", {}).get("original", {}).get("url")
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # Raise an error for bad responses
    print(f"Successfully pinned: {pin.get('title')}")

# Main function
def main():
    try:
        # Fetch pins
        pins_data = fetch_pins()
        pins = pins_data.get('items', [])

        if not pins:
            print("No pins found.")
            return

        # Choose the top pin
        top_pin = choose_top_pin(pins)

        if top_pin:
            print(f"Top pin selected: {top_pin.get('title')}")
            # Pin it to the board
            pin_to_board(top_pin)
        else:
            print("No relevant pins found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the script
if __name__ == "__main__":
    main()