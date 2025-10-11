"""
Action Item Extraction using LLMs
"""

import logging
import os
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Load prompt template
PROMPTS_DIR = Path(__file__).parent / "prompts"

def load_prompt(prompt_name: str) -> str:
    """Load a prompt template from file."""
    prompt_file = PROMPTS_DIR / f"{prompt_name}.txt"
    if prompt_file.exists():
        return prompt_file.read_text()
    logger.warning(f"Prompt file {prompt_file} not found")
    return ""

def extract_action_items(text: str, context: str = "") -> List[Dict[str, Any]]:
    """
    Extract actionable items from text using an LLM.
    
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
        
    TODO: Implement LLM integration
    Similar to summarizer, but with structured output parsing:
    
    1. Use a prompt that requests JSON output
    2. Parse LLM response into structured action items
    3. Validate and normalize the output
    
    Example prompt structure:
    \"\"\"
    Analyze the following text and extract actionable items.
    For each action, provide:
    - description: What needs to be done
    - due_date: When it's due (if mentioned)
    - priority: low/medium/high
    - assignee: Who should do it (if mentioned)
    
    Return as JSON array.
    
    Text:
    {text}
    \"\"\"
    """
    logger.info(f"Extracting actions from text of length {len(text)}")
    
    # Load action extraction prompt
    prompt_template = load_prompt("extract_actions_prompt")
    
    # TODO: Replace with actual LLM call
    logger.warning("LLM action extraction not implemented yet")
    raise NotImplementedError("LLM action extraction not yet implemented")
    
    # Placeholder response
    # return [
    #     {
    #         "description": "Example action item",
    #         "due_date": None,
    #         "priority": "medium",
    #         "assignee": None,
    #         "category": "task"
    #     }
    # ]

def parse_llm_response(llm_output: str) -> List[Dict[str, Any]]:
    """
    Parse LLM response into structured action items.
    
    TODO: Implement robust JSON parsing with fallbacks
    - Handle different LLM output formats
    - Validate required fields
    - Provide defaults for missing fields
    """
    import json
    
    try:
        actions = json.loads(llm_output)
        # Validate and normalize
        return actions
    except json.JSONDecodeError:
        logger.error("Failed to parse LLM response as JSON")
        return []

