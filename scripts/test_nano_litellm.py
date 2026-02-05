import os
import base64
from pathlib import Path
from litellm import image_generation


from dotenv import load_dotenv

# This looks for a .env file and loads the variables
load_dotenv()

# Now you can access it like a normal environment variable
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")


def generate_and_save_image():
    print("Generating image... please wait.")

    response = image_generation(
        model="gemini/gemini-2.5-flash-image",
        prompt="A futuristic cyberpunk city with neon lights and rainy streets",
    )

    # LiteLLM image_generation returns data list; each item may have b64_json
    item = response["data"][0]
    if not item.get("b64_json"):
        raise RuntimeError(f"No image bytes in response: {item}")

    image_bytes = base64.b64decode(item["b64_json"])

    filename = "cyberpunk_city.png"
    Path(filename).write_bytes(image_bytes)
    print(f"Success! Image saved as {filename}")

if __name__ == "__main__":
    generate_and_save_image()