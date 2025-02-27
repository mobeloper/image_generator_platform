
import os
import io
from dotenv import load_dotenv

import gradio as gr
import openai
import requests
from PIL import Image

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

def generate_image(prompt):
    # Generate image using DALL-E 3
    response = openai.Image.create(
        model="dall-e-3",
        prompt=f"Netflix campaign artwork: {prompt}",  # Contextual prompt
        n=1,
        size="1024x1024",
        quality="hd"
    )
    
    # Download and process the generated image
    image_url = response.data[0].url
    image_data = requests.get(image_url).content
    return Image.open(io.BytesIO(image_data))

interface = gr.Interface(
    fn=generate_image,
    inputs=gr.Textbox(
        lines=3,
        placeholder="Describe your Netflix campaign visual...",
        label="Describe the image you need"
    ),
    outputs=gr.Image(
        label="Generated Artwork",
        type="pil",
        show_download_button=True,
        show_flag_options=False  # Disables flagging functionality
    ),
    title="🎬 Netflix Campaign Creator",
    description="Generate on-brand visuals for Netflix campaigns using AI. \n Example prompts: \n 1. 'Stranger Things retro poster with neon lights' or, \n 2. 'The Crown dramatic royal portrait in black and white'",
    allow_flagging="never"  # Completely disable flagging system
)


interface.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=True  # Creates public link for collaboration
)

#interface.launch(share=False) # to disable sharing
