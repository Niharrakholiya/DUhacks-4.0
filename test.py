from logging import log
import requests
from dotenv import load_dotenv
import os
load_dotenv()
ACCESS_TOKEN = os.environ.get("WHATSAPP_API_TOKEN")
MEDIA_ID = "1359778541875637"

# Step 1: Get the direct media URL
media_url_response = requests.get(
    f"https://graph.facebook.com/v21.0/{MEDIA_ID}",
    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
)

if media_url_response.status_code == 200:
    media_data = media_url_response.json()
    media_url = media_data.get("url")
    print(media_url)
    # Step 2: Download the image
    image_response = requests.get(media_url, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"})

    if image_response.status_code == 200:
        with open("downloaded_image.jpg", "wb") as file:
            file.write(image_response.content)
        print("✅Image downloaded successfully!")
    else:
        print(f"❌ Failed to download image: {image_response.status_code}")
else:
    print(f"❌ Failed to get media URL: {media_url_response.status_code}")
