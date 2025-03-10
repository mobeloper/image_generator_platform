# 🎬 NetflixART  -  Netflix Movie Art Creator
An app to create Netflix campaing artwork from text.

## Key Features:

Uses DALL-E 3 for high-quality 1024x1024 HD images.

Prefaces prompts with "Netflix campaign artwork" for brand consistency.

Maximum requests per minute to avoid abuse

User promt validation and sanitization

Watermark to brand our app

Authentication of users to prevent malicious use of the app

Shows download button for saving images.

Runs on port 7860 with public sharing enabled.


## Setup

run this in terminal to install dependencies:
```
# For MacOS:
brew install libraqm
then,
pip install -r requirements.txt
then,
export OPENAI_API_KEY="your-key"

For testing without auth:
export DEV_MODE="true"
```

## Run the Application

```
python app.py
```

Expected outcome:
```
Running on local URL:  http://0.0.0.0:7860
Running on public URL: https://xxxxxxxx-xxxx-xxxx.gradio.live
```

### Run on specific port
python app.py --port 9000



## Usage Example:

Enter your prompt, for example: "Action movie poster with exploding spaceships, cinematic lighting".

Output: Get professional-grade artwork in 20 seconds...

![Sample generated image](https://raw.githubusercontent.com/mobeloper/image_generator_platform/refs/heads/main/generated-sample.webp)

Download generated images to your device.

If you want to iterate designs please refine your prompt.


## Typical workflow
(1) Edit code -> (2) Save -> (3) App auto-reloads in browser


## Troubleshooting Tips:

If you get API errors, verify your OpenAI key

For port conflicts: sudo lsof -i :7860 then kill -9 PID

For image generation failures: Check prompt guidelines

### error: RPC failed; HTTP 400 curl 22 The requested URL returned error: 400

Fix by increasing Git buffer size (run before pushing):

git config --global http.postBuffer 1048576000  # 1GB buffer

git config --global pack.windowMemory 256m

git config --global pack.packSizeLimit 256m

-----------------
Build by:
Eric Michel
