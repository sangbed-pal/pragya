import os
import requests
AZURE_API_KEY = os.getenv("AZURE_TTS_API_KEY")
AZURE_TTS_ENDPOINT = os.getenv("AZURE_TTS_ENDPOINT")
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AZURE_API_KEY}"
}

def speech_from_text(payload):
    
    response = requests.post(AZURE_TTS_ENDPOINT, headers=HEADERS, json=payload)
    return response

if __name__ == "__main__":
    # Example usage
    text= "Hello, this is a test."
    payload = {
            "model": "gpt-4o-mini-tts",
            "input": text,
            "voice": "ash"
        }
    response = speech_from_text(payload)
    print(response.status_code)
    output_path = "speech_output.mp3"
    with open(output_path, "wb") as f:
            f.write(response.content)