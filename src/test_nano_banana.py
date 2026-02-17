import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt = (
    "Create a picture of my cat eating a nano-banana in a "
    "fancy restaurant under the Gemini constellation",
)

image = Image.open("/media/hirani/New Volume/Manthan/I_Love_Images/test_images/1.jpeg")

from google.genai.errors import ClientError

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, image],
    )

    for part in response.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = part.as_image()
            image.save("generated_image.png")
except ClientError as e:
    print(f"Error calling Gemini API: {e}")