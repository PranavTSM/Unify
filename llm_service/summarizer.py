"""
Summarizer - Text summarization using LangChain and OpenAI
"""

import os
import logging
from pathlib import Path
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)
PROMPTS_DIR = Path(__file__).parent / "prompts"

def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt template from the prompts directory.
    
    Args:
        prompt_name: Name of the prompt file (without .txt extension)
        
    Returns:
        Prompt template string
    """
    try:
        prompt_file = PROMPTS_DIR / f"{prompt_name}.txt"
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        else:
            logger.warning(f"Prompt file not found: {prompt_file}")
            return ""
    except Exception as e:
        logger.error(f"Error loading prompt {prompt_name}: {e}")
        return ""

def generate_summary(text: str, max_length: int = 150) -> str:
    """
    Generate a concise summary of the input text using LangChain + OpenAI.
    
    Args:
        text: Input text to summarize
        max_length: Maximum length of summary (approximate)
        
    Returns:
        Summarized text
    """
    logger.info(f"Generating summary for text of length {len(text)}")
    
    # If text is already short, return as-is
    if len(text) <= max_length:
        return text
    
    try:
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set, using truncation")
            return text[:max_length] + "..."
        
        # Initialize LangChain ChatOpenAI with gpt-4o-mini
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=200,
            openai_api_key=api_key
        )
        
        # Load system prompt
        system_prompt = load_prompt("summarize_prompt")
        if not system_prompt:
            system_prompt = f"Summarize the following text concisely in under {max_length} characters:"
        
        # Create messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=text)
        ]
        
        # Generate summary
        response = llm.invoke(messages)
        summary = response.content.strip()
        
        logger.info(f"Generated summary of length {len(summary)}")
        return summary
        
    except Exception as e:
        logger.error(f"Error in LangChain summarization: {e}")
        # Fallback to truncation
        return text[:max_length] + "..."

def summarize_email(email_data: dict) -> str:
    """
    Summarize email content.
    
    Args:
        email_data: Dict with 'subject', 'body', 'from', etc.
        
    Returns:
        Email summary
    """
    try:
        subject = email_data.get("subject", "")
        body = email_data.get("body", "")
        from_addr = email_data.get("from", "unknown")
        
        # Combine subject and body
        full_text = f"Subject: {subject}\n\nFrom: {from_addr}\n\n{body}"
        
        return generate_summary(full_text, max_length=200)
        
    except Exception as e:
        logger.error(f"Error summarizing email: {e}")
        return email_data.get("subject", "Email")
