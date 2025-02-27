# image_generator_platform
An app to create Netflix campaing artwork from text.

## Key Features:

Uses DALL-E 3 for high-quality 1024x1024 HD images.

Prefaces prompts with "Netflix campaign artwork" for brand consistency.

Includes example prompts for your campaign inspiration.

Shows download button for saving images.

Runs on port 7860 with public sharing enabled.


## Setup

run this in terminal to install dependencies:
```
pip install -r requirements.txt
then,
export OPENAI_API_KEY="your-key"
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


-----------------
Build by:
Eric Michel
