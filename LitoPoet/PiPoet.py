import subprocess
import base64
import requests
import json
import os

def capture_image(output_path):
    # Capture image with specified resolution 640x480
    subprocess.run(['libcamera-still', '-t', '100', '-o', output_path, '--width', '640', '--height', '480'])


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def send_to_openai_vision_api(image_path):
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("API key is not set in environment variables")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    base64_image = encode_image(image_path)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system", 
                "content": [
                    {
                        "type": "text",
                        "text": 
                            "You are a university literature professor well-versed in ancient Chinese poetry and lyrics. You possess a profound understanding of their historical and cultural contexts and the realms they describe. Furthermore, you can genuinely apply this knowledge effortlessly. For instance, in your daily life, when witnessing the beauty of nature, you can always associate it with the most appropriate corresponding poems and recite them. Similarly, when encountering various situations, whether the joy of success or the hardships of life, you can recall the poems and lyrics ancient poets wrote in similar circumstances."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Based on this photo, please recite a Chinese poem that reflects the content depicted in the photo. Remember only to output the title of poem, its author and the Chinese poem."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 2000
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()


def display_chinese(response):
    try:
        poems = response['choices'][0]['message']['content']
        print(poems)  # Assuming the API returns properly formatted Unicode strings.
    except KeyError:
        print("Error in response data structure")


# Capture the image
image_path = '/home/lito/Desktop/photo.jpg'
capture_image(image_path)

# Send the image to OpenAI's Vision API
result = send_to_openai_vision_api(image_path)

# Print the response
# print(json.dumps(result, indent=4))

# Display response
display_chinese(result)