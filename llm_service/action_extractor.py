"""
Action Item Extraction using LangChain + OpenAI
"""

import logging
import os
import json
from typing import List, Dict, Any
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

# Load prompt template
PROMPTS_DIR = Path(__file__).parent / "prompts"

def load_prompt(prompt_name: str) -> str:
    """Load a prompt template from file."""
    prompt_file = PROMPTS_DIR / f"{prompt_name}.txt"
    if prompt_file.exists():
        return prompt_file.read_text().strip()
    logger.warning(f"Prompt file {prompt_file} not found")
    return ""

def extract_action_items(text: str, context: str = "") -> List[Dict[str, Any]]:
    """
    Extract actionable items from text using LangChain + OpenAI.
    
    Args:
        text: Input text to analyze
        context: Additional context (e.g., email thread, meeting notes)
        
    Returns:
        List of extracted action items with structure:
        [
            {
                "description": str,
                "due_date": str (ISO format) or None,
                "priority": str (low/medium/high),
                "assignee": str or None,
                "category": str (task/meeting/followup/etc)
            }
        ]
    """
    logger.info(f"Extracting actions from text of length {len(text)}")
    
    try:
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set, returning empty actions")
            return []
        
        # Initialize LangChain ChatOpenAI
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.0,  # Low temperature for structured extraction
            openai_api_key=api_key
        )
        
        # Load system prompt
        system_prompt = load_prompt("extract_actions_prompt")
        if not system_prompt:
            system_prompt = """Analyze the following text and extract actionable items.
For each action, provide:
- description: What needs to be done
- due_date: When it's due (if mentioned, in ISO format)
- priority: low/medium/high
- assignee: Who should do it (if mentioned)
- category: task/meeting/followup/decision

Return ONLY a JSON array of action items. No additional text."""
        
        # Prepare input
        full_text = text
        if context:
            full_text = f"Context: {context}\n\nText: {text}"
        
        # Create messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=full_text)
        ]
        
        # Generate extraction
        response = llm.invoke(messages)
        llm_output = response.content.strip()
        
        # Parse response
        actions = parse_llm_response(llm_output)
        
        logger.info(f"Extracted {len(actions)} action items")
        return actions
        
    except Exception as e:
        logger.error(f"Error in LangChain action extraction: {e}", exc_info=True)
        return []

def parse_llm_response(llm_output: str) -> List[Dict[str, Any]]:
    """
    Parse LLM response into structured action items.
    
    Handles different LLM output formats with robust JSON parsing.
    
    Args:
        llm_output: Raw LLM output
        
    Returns:
        List of action items
    """
    try:
        # Try to extract JSON from the response
        # Sometimes LLMs wrap JSON in markdown code blocks
        if "```json" in llm_output:
            # Extract JSON from markdown code block
            start = llm_output.find("```json") + 7
            end = llm_output.find("```", start)
            json_str = llm_output[start:end].strip()
        elif "```" in llm_output:
            # Extract from generic code block
            start = llm_output.find("```") + 3
            end = llm_output.find("```", start)
            json_str = llm_output[start:end].strip()
        else:
            json_str = llm_output.strip()
        
        # Parse JSON
        actions = json.loads(json_str)
        
        # Validate and normalize
        if not isinstance(actions, list):
            logger.warning("LLM response is not a list, wrapping in list")
            actions = [actions]
        
        # Normalize each action
        normalized_actions = []
        for action in actions:
            if isinstance(action, dict):
                normalized = {
                    "description": action.get("description", ""),
                    "due_date": action.get("due_date"),
                    "priority": action.get("priority", "medium"),
                    "assignee": action.get("assignee"),
                    "category": action.get("category", "task")
                }
                if normalized["description"]:  # Only add if has description
                    normalized_actions.append(normalized)
        
        return normalized_actions
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.debug(f"LLM output: {llm_output}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error parsing LLM response: {e}")
        return []
