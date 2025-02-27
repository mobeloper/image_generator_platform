
import os
import io
from dotenv import load_dotenv

import gradio as gr
import openai
import requests
import pandas as pd
import threading

from PIL import Image, ImageDraw, ImageFont

import re
import html

import time
from datetime import datetime
from functools import wraps
import hashlib

load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]

# Configuration
MAX_REQUESTS_PER_MINUTE = 1
WATERMARK_TEXT = "NetflixART Asset © 2025"



password = os.environ["NETFLIX_USER_PW"]
hashed_pw = hashlib.sha256(password.encode()).hexdigest()
print(hashed_pw)

USER_CREDENTIALS = {
    os.environ["NETFLIX_USER"]: hashed_pw
}

# Temporary in-memory credentials (not for production)
# USER_CREDENTIALS = {
#     # Format: "username": "hashed_password"
#     "test_user": hashed_pw,
# }



# Rate limiting store
request_log = {}
lock = threading.Lock()

# --- Security Middlewares ---

def rate_limit(fn):
    @wraps(fn)
    def wrapper(username, prompt):
        with lock:
            now = time.time()
            window = [t for t in request_log.get(username, []) if t > now - 60]
            if len(window) >= MAX_REQUESTS_PER_MINUTE:
                raise gr.Error("Rate limit exceeded - please wait 1 minute or upgrade to our premium service.")
            request_log[username] = window + [now]
        return fn(username, prompt)
    return wrapper

def check_content_moderation(prompt):
    response = openai.Moderation.create(
        input=prompt,
        model="text-moderation-latest"
    )
    if response.results[0].flagged:
        raise gr.Error("Content policy violation detected in prompt")



# --- Authentication System ---
def authenticate(username, password):
    if USER_CREDENTIALS.get(username) != hashlib.sha256(password.encode()).hexdigest():
        raise gr.Error("Invalid credentials")
    return username  # Return validated username for state



# --- Compliance Features ---

def log_usage(username, prompt, status):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user": username,
        "prompt": prompt[:500],  # Truncate for storage
        "status": status
    }
    pd.DataFrame([log_entry]).to_csv("usage_log.csv", mode="a", header=False)

def add_watermark(image, username):
    draw = ImageDraw.Draw(image)
    
    # Ultra subtle settings
    try:
        font = ImageFont.truetype("arialbd.ttf", 18)
    except:
        font = ImageFont.load_default(30)  # Minimal fallback size
    
    text = f"{WATERMARK_TEXT} | By {username}"
    
    # Get text dimensions
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Position in corner with minimal offset
    margin = 50
    x = image.width - text_width - margin
    y = image.height - text_height - margin
    
    # Nearly invisible text (10% opacity)
    draw.text(
        (x, y), 
        text, 
        fill=(255, 255, 0, 26),  # Yellow with 10% opacity
        font=font,
        # spacing=0,
        # features=["-liga"]  # Disable ligatures for simplicity
    )
    
    return image
    
    
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


# --- Image Generation ---

@rate_limit
def generate_image(username, prompt):
# def generate_image(prompt: str) -> Image.Image:
    try:
        # Validation chain
        validated_prompt = validate_and_sanitize_prompt(prompt)
        check_content_moderation(validated_prompt)
        
        # Generate image using DALL-E 3
        response = openai.Image.create(
            model="dall-e-3",
            prompt=f"You are an expert designer of artwork for movie banners and visual content campaings. Create Netflix movie banner for {validated_prompt}. Make sure the image is beautiful and represents all elements to atract eyeballs to the image.",
            n=1,
            size="1024x1024",
            quality="hd"
        )
        
        # Process image
        image_url = response.data[0].url
        image_data = requests.get(image_url).content
        image = Image.open(io.BytesIO(image_data))
        
        # Add watermark
        watermarked_image = add_watermark(image, username)
        
        # Log successful generation
        log_usage(username, prompt, "success")
        
        return watermarked_image

    except Exception as e:
        log_usage(username, prompt, f"error: {str(e)}")
        raise



# interface = gr.Interface(
#     fn=generate_image,
#     inputs=gr.Textbox(
#         lines=3,
#         placeholder="Describe your Netflix campaign visual...",
#         label="Describe the image you need",
#         max_lines=3
#     ),
#     outputs=gr.Image(
#         label="Generated Artwork",
#         type="pil",
#         show_download_button=True,
#         # show_flag_options=False  # Disables flagging functionality
#     ),
#     title="🎬 Netflix Campaign Creator",
#     description="Generate on-brand visuals for Netflix campaigns using AI. \n Example prompts: \n 1. 'Stranger Things retro poster with neon lights' or, \n 2. 'The Crown dramatic royal portrait in black and white.'",
#     allow_flagging="never"  # Completely disable flagging system
# )


# --- Gradio Interface ---


css = """
footer {display: none !important;}
.gradio-container {min-height: 0 !important;}
"""

with gr.Blocks(css=css, analytics_enabled=False) as interface:
    gr.Markdown("# NetflixART  -  Netflix Movie Art Creator")
    
    # Add state management
    authenticated_user = gr.State("")  # Hidden state component
    
    with gr.Row():
        with gr.Column():
            username = gr.Textbox(label="Netflix Employee ID")
            password = gr.Textbox(label="Password", type="password")
            prompt = gr.Textbox(label="Describe the image you want to create in detail:", lines=3)
            submit = gr.Button("Generate Image")
            
        output_image = gr.Image(label="Generated Image", type="pil")

    submit.click(
        fn=authenticate,
        inputs=[username, password],
        outputs=authenticated_user
    ).success(
        fn=generate_image,
        inputs=[authenticated_user, prompt],
        outputs=output_image
    )

# interface.launch(
#     server_name="0.0.0.0",
#     server_port=7860,
#     share=True  # Creates public link for collaboration
# )
# #interface.launch(share=False) # to disable sharing

interface.launch(
    server_name="0.0.0.0",
    server_port=7860,
    show_api=False,
    share=True,  # Creates public link for collaboration
    auth=(lambda u,p: authenticate(u,p)) if not os.getenv('DEV_MODE') else None
)


