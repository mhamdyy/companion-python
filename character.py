import logging
import os
from google.adk.agents.llm_agent import LlmAgent

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define the instruction for the companion agent
instruction = """You are a friendly and efficient companion who will interact with user have start a conversation"""

# Create the LlmAgent instance
root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='companion_agent',
    instruction=instruction
)
