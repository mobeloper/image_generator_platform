





#=================================


## !pip install gradio openai requests pillow
##

import os
import io
import doten import load_dotenv

import gradio as gr
import openai
import requests
from PIL import Image


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
        label="Creative Brief"
    ),
    outputs=gr.Image(
        label="Generated Artwork",
        type="pil",
        show_download_button=True
    ),
    title="🎬 Netflix Campaign Creator",
    description="Generate on-brand visuals for Netflix campaigns using AI. Example prompts: 'Stranger Things retro poster with neon lights' or 'The Crown dramatic royal portrait'"
)

interface.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=True  # Creates public link for collaboration
)
