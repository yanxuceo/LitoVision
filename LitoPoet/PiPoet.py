import subprocess
import base64
import requests
import json
import os

import openai

from pathlib import Path
from openai import OpenAI


def create_speech_mp3(input_text: str, file_path: Path) -> None:
    """
    Creates an MP3 file from the given text using OpenAI's text-to-speech model.

    Args:
    input_text (str): Text to convert to speech.
    file_path (Path): Path to save the MP3 file.
    """
    try:
        # Initialize OpenAI client
        openai_api_key = os.getenv('OPENAI_API_KEY')
        openai_api = OpenAI(api_key=openai_api_key)


        # Create text-to-speech audio file
        response = openai_api.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=input_text
        )
        
        # Stream response to file
        with open(file_path, 'wb') as f:
            for chunk in response.iter_bytes(chunk_size=4096):
                f.write(chunk)

        print(f"MP3 file created successfully at {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")



def capture_image(output_path):
    # Capture image with specified resolution 640x480
    subprocess.run(['libcamera-still', '-t', '50', '-o', output_path, '--width', '640', '--height', '480'])


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


def play_mp3(file_path):
    """
    Plays an MP3 file using the mpg123 command-line player.
    """
    try:
        # Use subprocess.run to call mpg123 with the file path
        result = subprocess.run(['mpg123', file_path], check=True)
        print("Playback finished.")
    except subprocess.CalledProcessError:
        print("Failed to play the file.")
    except FileNotFoundError:
        print("mpg123 is not installed. Please install it to play the file.")


# Capture the image
image_path = '/home/lito/Desktop/photo.jpg'
capture_image(image_path)

# Send the image to OpenAI's Vision API
result = send_to_openai_vision_api(image_path)

# Display response
display_chinese(result)


# TODO: faster gen&read by adding streaming ouput for vision api and audio api 
speech_file_path = Path(__file__).parent / "speech.mp3"
create_speech_mp3(result['choices'][0]['message']['content'], speech_file_path)

play_mp3(str(speech_file_path))