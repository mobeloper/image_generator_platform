
import os
import io
from dotenv import load_dotenv

import gradio as gr
import openai
import requests
from PIL import Image

import re
import html

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

#Prompt sanitization
def validate_and_sanitize_prompt(prompt: str) -> str:
    """
    Validate and sanitize user input for DALL-E image generation
    Returns sanitized prompt or raises ValueError
    """
    # Trim whitespace and check empty input
    prompt = prompt.strip()
    if not prompt:
        raise ValueError("Prompt cannot be empty")

    # Length validation (DALL-E 3 has 4000 char limit but we'll set safer limit)
    if len(prompt) > 500:
        raise ValueError("Prompt too long (max 500 characters)")

    # Remove HTML tags and escape special characters
    sanitized = html.escape(prompt)
    
    # Block common injection patterns using regex
    injection_patterns = [
        r"(http(s)?:\/\/)[^\s]+",  # URLs
        r"<[^>]*>",  # HTML tags
        r"\{.*\{.*\}.*\}",  # Nested JSON
        r"(\bexec\b|\bsystem\b|\bopen\b|\brm\b|\bdel\b)",  # Dangerous commands
        r"[<>{};`$\\]",  # Special shell characters
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, sanitized, re.IGNORECASE):
            raise ValueError("Invalid characters or patterns detected in prompt")

    # Block NSFW/abuse keywords (customize for Netflix brand safety)
    blocked_keywords = [
        "nude", "explicit", "violence", "blood", "hate", 
        "racist", "sex", "nsfw", "illegal", "copyright"
    ]
    
    if any(re.search(rf"\b{kw}\b", sanitized, re.IGNORECASE) for kw in blocked_keywords):
        raise ValueError("Prompt contains blocked content")

    return sanitized


#Generate image
def generate_image(prompt: str) -> Image.Image:
    
    try:
        validated_prompt = validate_and_sanitize_prompt(prompt)
    except ValueError as e:
        raise gr.Error(f"Validation error: {str(e)}") from None

    
    # Generate image using DALL-E 3
    response = openai.Image.create(
        model="dall-e-3",
        prompt=f"You are an expert designer of artwork for movie banners and visual content campaings. Create Netflix movie banner for {validated_prompt}. Make sure the image is beautiful and represents all elements to atract eyeballs to the image.",
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
        # show_flag_options=False  # Disables flagging functionality
    ),
    title="🎬 Netflix Campaign Creator",
    description="Generate on-brand visuals for Netflix campaigns using AI. \n Example prompts: \n 1. 'Stranger Things retro poster with neon lights' or, \n 2. 'The Crown dramatic royal portrait in black and white.'",
    allow_flagging="never"  # Completely disable flagging system
)


interface.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=True  # Creates public link for collaboration
)

#interface.launch(share=False) # to disable sharing
