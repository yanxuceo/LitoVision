import os
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

if __name__ == "__main__":
    speech_file_path = Path(__file__).parent / "speech.mp3"
    text_to_convert = "看山是山，看水是水"
    create_speech_mp3(text_to_convert, speech_file_path)
