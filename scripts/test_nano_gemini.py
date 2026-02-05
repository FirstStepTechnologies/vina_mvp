
import os
from dotenv import load_dotenv

# This looks for a .env file and loads the variables
load_dotenv()

# Now you can access it like a normal environment variable
api_key = os.getenv("GEMINI_API_KEY")

# Or if you specifically need to ensure it's set in os.environ:
# os.environ["GEMINI_API_KEY"] is now automatically populated
print(f"Key loaded: {os.environ.get('GEMINI_API_KEY')[:5]}...")

import os
from pathlib import Path
from google import genai
from google.genai import types

def generate_9x16_image():
    print("Generating 9:16 image... please wait.")

    client = genai.Client(api_key=api_key)

    prompt = "A futuristic cyberpunk indian city with neon lights and rainy streets"

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio="9:16",
            ),
        ),
    )

    out_path = Path("cyberpunk_indian_9x16.png")
    image_found = False

    for part in response.parts:
        # Official docs: call as_image() on parts that have inline_data
        if getattr(part, "inline_data", None) is not None:
            img = part.as_image()  # returns a Pillow Image object
            img.save(out_path)
            image_found = True
            break
        # You may also see plain text parts; just ignore those
        if getattr(part, "text", None):
            print("Text part from model:", part.text)

    if not image_found:
        raise RuntimeError("No image part returned by model.")

    print(f"Success! Image saved as {out_path}")

if __name__ == "__main__":
    generate_9x16_image()