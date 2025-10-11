#!/usr/bin/env python3
"""
Test script for Aggregator + LLM Service integration
Tests the new summarization and action extraction endpoints
"""

import requests
import json
import sys
from typing import Dict, Any

# Service URLs
AGGREGATOR_URL = "http://localhost:8001"
LLM_SERVICE_URL = "http://localhost:8002"

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test(name: str):
    """Print test name"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}🧪 Testing: {name}{Colors.RESET}")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message: str):
    """Print info message"""
    print(f"ℹ️  {message}")

def test_health_checks() -> bool:
    """Test health endpoints for both services"""
    print_test("Service Health Checks")
    
    all_healthy = True
    
    # Test Aggregator
    try:
        response = requests.get(f"{AGGREGATOR_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Aggregator is healthy")
            
            # Check LLM service status from aggregator
            llm_healthy = data.get("dependencies", {}).get("llm_service", {}).get("healthy", False)
            if llm_healthy:
                print_success("LLM service is healthy (via aggregator)")
            else:
                print_warning("LLM service reported as unhealthy by aggregator")
                all_healthy = False
        else:
            print_error(f"Aggregator health check failed: {response.status_code}")
            all_healthy = False
    except Exception as e:
        print_error(f"Failed to connect to Aggregator: {e}")
        all_healthy = False
    
    # Test LLM Service directly
    try:
        response = requests.get(f"{LLM_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("LLM service is healthy (direct check)")
        else:
            print_error(f"LLM service health check failed: {response.status_code}")
            all_healthy = False
    except Exception as e:
        print_error(f"Failed to connect to LLM service: {e}")
        all_healthy = False
    
    return all_healthy

def test_unified_inbox() -> Dict[str, Any]:
    """Test getting unified inbox"""
    print_test("Get Unified Inbox")
    
    try:
        response = requests.get(
            f"{AGGREGATOR_URL}/unified/inbox",
            params={"max_per_source": 10},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            priority_count = len(data.get("priority_messages", []))
            unread_count = len(data.get("unread_messages", []))
            
            print_success(f"Retrieved unified inbox")
            print_info(f"Priority messages: {priority_count}")
            print_info(f"Unread messages: {unread_count}")
            
            return data
        else:
            print_error(f"Failed to get unified inbox: {response.status_code}")
            return {}
    except Exception as e:
        print_error(f"Error getting unified inbox: {e}")
        return {}

def test_summarize_auto_fetch() -> bool:
    """Test summarization with auto-fetch (no message IDs)"""
    print_test("Summarize Priority Messages (Auto-fetch)")
    
    try:
        payload = {
            "mode": "bullets",
            "max_words": 200
        }
        
        response = requests.post(
            f"{AGGREGATOR_URL}/unified/inbox/summarize",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            message_count = data.get("message_count", 0)
            summary = data.get("summary", "")
            bullets = data.get("bullets", [])
            
            print_success(f"Summarization successful")
            print_info(f"Messages summarized: {message_count}")
            print_info(f"Summary length: {len(summary)} chars")
            print_info(f"Bullet points: {len(bullets)}")
            
            if summary:
                print(f"\n{Colors.BOLD}Summary:{Colors.RESET}")
                print(f"  {summary[:200]}..." if len(summary) > 200 else f"  {summary}")
            
            if bullets:
                print(f"\n{Colors.BOLD}Bullets:{Colors.RESET}")
                for i, bullet in enumerate(bullets[:3], 1):
                    print(f"  {i}. {bullet}")
                if len(bullets) > 3:
                    print(f"  ... and {len(bullets) - 3} more")
            
            return True
        elif response.status_code == 503:
            print_warning("LLM service unavailable")
            return False
        else:
            print_error(f"Summarization failed: {response.status_code}")
            try:
                print_error(f"Error: {response.json()}")
            except:
                print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error during summarization: {e}")
        return False

def test_summarize_with_ids(inbox_data: Dict[str, Any]) -> bool:
    """Test summarization with specific message IDs"""
    print_test("Summarize Specific Messages")
    
    # Get some message IDs from inbox
    priority_messages = inbox_data.get("priority_messages", [])
    if not priority_messages:
        print_warning("No priority messages available for testing")
        return True  # Not a failure, just no data
    
    # Take first 3 message IDs
    message_ids = [msg.get("id") for msg in priority_messages[:3] if msg.get("id")]
    
    if not message_ids:
        print_warning("No message IDs found")
        return True
    
    try:
        payload = {
            "message_ids": message_ids,
            "mode": "executive",
            "max_words": 150,
            "include_messages": True
        }
        
        response = requests.post(
            f"{AGGREGATOR_URL}/unified/inbox/summarize",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Summarized {len(message_ids)} specific messages")
            print_info(f"Summary: {data.get('summary', '')[:100]}...")
            return True
        else:
            print_error(f"Failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_extract_actions_auto_fetch() -> bool:
    """Test action extraction with auto-fetch"""
    print_test("Extract Actions from Unread (Auto-fetch)")
    
    try:
        payload = {
            "priority_mode": "hybrid",
            "min_priority": "medium"
        }
        
        response = requests.post(
            f"{AGGREGATOR_URL}/unified/inbox/extract-actions",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            actions = data.get("actions", [])
            summary = data.get("summary", {})
            
            print_success(f"Action extraction successful")
            print_info(f"Total actions: {summary.get('total_actions', 0)}")
            print_info(f"High priority: {summary.get('by_priority', {}).get('high', 0)}")
            print_info(f"Medium priority: {summary.get('by_priority', {}).get('medium', 0)}")
            print_info(f"Low priority: {summary.get('by_priority', {}).get('low', 0)}")
            
            if actions:
                print(f"\n{Colors.BOLD}Sample Actions:{Colors.RESET}")
                for i, action in enumerate(actions[:3], 1):
                    desc = action.get("description", "")
                    priority = action.get("priority", "")
                    due = action.get("due_date", "No due date")
                    print(f"  {i}. [{priority.upper()}] {desc}")
                    print(f"     Due: {due}")
                if len(actions) > 3:
                    print(f"  ... and {len(actions) - 3} more")
            
            return True
        elif response.status_code == 503:
            print_warning("LLM service unavailable")
            return False
        else:
            print_error(f"Action extraction failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error during action extraction: {e}")
        return False

def test_extract_actions_with_ids(inbox_data: Dict[str, Any]) -> bool:
    """Test action extraction with specific message IDs"""
    print_test("Extract Actions from Specific Messages")
    
    # Get some message IDs
    unread_messages = inbox_data.get("unread_messages", [])
    if not unread_messages:
        print_warning("No unread messages available for testing")
        return True
    
    message_ids = [msg.get("id") for msg in unread_messages[:5] if msg.get("id")]
    
    if not message_ids:
        print_warning("No message IDs found")
        return True
    
    try:
        payload = {
            "message_ids": message_ids,
            "context": "Project management and team coordination",
            "priority_mode": "hybrid",
            "include_messages": True
        }
        
        response = requests.post(
            f"{AGGREGATOR_URL}/unified/inbox/extract-actions",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            actions = data.get("actions", [])
            print_success(f"Extracted {len(actions)} actions from {len(message_ids)} messages")
            return True
        else:
            print_error(f"Failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"  Aggregator + LLM Service Integration Tests")
    print(f"{'='*60}{Colors.RESET}\n")
    
    print_info(f"Aggregator URL: {AGGREGATOR_URL}")
    print_info(f"LLM Service URL: {LLM_SERVICE_URL}")
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }
    
    # Test 1: Health checks
    results["total"] += 1
    if test_health_checks():
        results["passed"] += 1
    else:
        results["failed"] += 1
        print_error("\n❌ Services are not healthy. Please check configuration and try again.")
        sys.exit(1)
    
    # Test 2: Get unified inbox
    results["total"] += 1
    inbox_data = test_unified_inbox()
    if inbox_data:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 3: Summarize (auto-fetch)
    results["total"] += 1
    if test_summarize_auto_fetch():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 4: Summarize (with IDs)
    results["total"] += 1
    if test_summarize_with_ids(inbox_data):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 5: Extract actions (auto-fetch)
    results["total"] += 1
    if test_extract_actions_auto_fetch():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 6: Extract actions (with IDs)
    results["total"] += 1
    if test_extract_actions_with_ids(inbox_data):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Print summary
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"  Test Summary")
    print(f"{'='*60}{Colors.RESET}\n")
    
    print_info(f"Total tests: {results['total']}")
    print_success(f"Passed: {results['passed']}")
    if results['failed'] > 0:
        print_error(f"Failed: {results['failed']}")
    if results['skipped'] > 0:
        print_warning(f"Skipped: {results['skipped']}")
    
    success_rate = (results['passed'] / results['total']) * 100 if results['total'] > 0 else 0
    print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.RESET}\n")
    
    if results['failed'] == 0:
        print_success("🎉 All tests passed! Integration is working correctly.")
        sys.exit(0)
    else:
        print_error("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(130)

