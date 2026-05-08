"""
mcp_server.py

A fully compliant MCP server built using the FastMCP and stdio pattern.
This server exposes a toolkit to generate an image using nano-banana.
"""
import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import asyncio  

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server. This object will register all our tools.
# The name "nano_banana" acts as a namespace for all tools defined in this file.
mcp = FastMCP("nano_banana")

# --- Define the Core Functions ---
# Each function is decorated with @mcp.tool(), which automatically turns it
# into an MCP-compliant tool, using its signature and docstring for the schema.

@mcp.tool()
async def generate_image(prompt: str) -> dict:
    """
    Generates an image based on a textual prompt using a generative model.

    Args:
        prompt: The textual description of the image to generate.

    Returns:
        A dictionary containing the generated image data in base64 format or an error message.
    """
    try:

        #await asyncio.sleep(30)
        # Create the directory if it doesn't exist
        image_dir = os.path.expanduser("~/image_gen")
        os.makedirs(image_dir, exist_ok=True)
        
        client = genai.Client()

        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_path = os.path.join(image_dir, "char.png")
                with open(image_path, "wb") as f:
                    f.write(part.inline_data.data)
                return {"status": "success", "image_path": image_path}

        error_message = "No image data found in response"
        if response.candidates and response.candidates[0].finish_reason:
            finish_reason = response.candidates[0].finish_reason
            error_message += f". Finish reason: {finish_reason.name}"
            if finish_reason.name == 'SAFETY':
                error_message += f", Safety ratings: {response.candidates[0].safety_ratings}"
        if response.prompt_feedback:
            error_message += f", Prompt feedback: {response.prompt_feedback}"
        return {"status": "error", "message": error_message}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def generate_lip_sync_images(prompt: str) -> dict:
    """
    Generates two images for a lip-syncing app, one with mouth open and one with mouth closed.

    Args:
        prompt: The base textual description of the character.

    Returns:
        A dictionary containing the paths to the generated images or an error message.
    """
    try:

        #await asyncio.sleep(65)
        # Create the directory if it doesn't exist
        image_dir = os.path.expanduser("~/image_gen")
        os.makedirs(image_dir, exist_ok=True)

        client = genai.Client()
        open_prompt = f"{prompt} with mouth open"
        response_open = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[open_prompt],
        )
        
        open_image_path = None
        for part in response_open.candidates[0].content.parts:
            if part.inline_data is not None:
                open_image_path = os.path.join(image_dir, "char-mouth-open.png")
                with open(open_image_path, "wb") as f:
                    f.write(part.inline_data.data)
                break
        
        if not open_image_path:
            error_message = "Failed to generate mouth open image"
            if response_open.candidates and response_open.candidates[0].finish_reason:
                finish_reason = response_open.candidates[0].finish_reason
                error_message += f". Finish reason: {finish_reason.name}"
                if finish_reason.name == 'SAFETY':
                    error_message += f", Safety ratings: {response_open.candidates[0].safety_ratings}"
            if response_open.prompt_feedback:
                error_message += f", Prompt feedback: {response_open.prompt_feedback}"
            return {"status": "error", "message": error_message}

        #await asyncio.sleep(65)

        # Generate mouth closed image using the open image as reference
        closed_prompt = "change the mouth from open to close"
        image = Image.open(open_image_path)
        response_closed = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[closed_prompt, image],
        )

        closed_image_path = None
        for part in response_closed.candidates[0].content.parts:
            if part.inline_data is not None:
                closed_image_path = os.path.join(image_dir, "char-mouth-closed.png")
                with open(closed_image_path, "wb") as f:
                    f.write(part.inline_data.data)
                break

        if closed_image_path:
            return {"status": "success", "open_image_path": open_image_path, "closed_image_path": closed_image_path}
        
        error_message = "Failed to generate mouth closed image"
        if response_closed.candidates and response_closed.candidates[0].finish_reason:
            finish_reason = response_closed.candidates[0].finish_reason
            error_message += f". Finish reason: {finish_reason.name}"
            if finish_reason.name == 'SAFETY':
                error_message += f", Safety ratings: {response_closed.candidates[0].safety_ratings}"
        if response_closed.prompt_feedback:
            error_message += f", Prompt feedback: {response_closed.prompt_feedback}"
        return {"status": "error", "message": error_message}

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("Starting MCP server with SSE transport...")
    # The run() method uses stdio by default
    mcp.run(transport="sse")