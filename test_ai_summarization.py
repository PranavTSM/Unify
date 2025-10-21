"""
Test AI Summarization by Source
Tests the new endpoint that summarizes 20 messages from each source (Gmail, Outlook, Teams)
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_health_checks():
    """Test that all services are running"""
    print_section("1. Health Checks")
    
    services = {
        "Aggregator": f"{BASE_URL}/health",
        "LLM Service": "http://localhost:8002/health",
        "MCP Server": "http://localhost:8000/health"
    }
    
    all_healthy = True
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name:15s} - Healthy")
            else:
                print(f"❌ {name:15s} - Unhealthy (Status: {response.status_code})")
                all_healthy = False
        except Exception as e:
            print(f"❌ {name:15s} - Not running ({str(e)})")
            all_healthy = False
    
    return all_healthy

def test_summarize_by_source(max_per_source=20, mode="executive"):
    """Test the new summarize-by-source endpoint"""
    print_section(f"2. AI Summarization by Source ({max_per_source} messages per source)")
    
    url = f"{BASE_URL}/unified/inbox/summarize-by-source"
    params = {
        "max_per_source": max_per_source,
        "mode": mode,
        "max_words": 200
    }
    
    print(f"\n📡 Calling: POST {url}")
    print(f"   Parameters: {json.dumps(params, indent=2)}")
    print("\n⏳ This may take 10-30 seconds (fetching + AI processing)...\n")
    
    try:
        response = requests.post(url, params=params, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None
        
        data = response.json()
        
        # Display results
        print("✅ Success!\n")
        print(f"📊 Total Messages: {data.get('total_messages', 0)}")
        print(f"📅 Timestamp: {data.get('timestamp', 'N/A')}")
        print(f"🎯 Mode: {data.get('mode', 'N/A')}")
        
        # Source breakdown
        print("\n📈 Messages by Source:")
        sources = data.get('sources', {})
        for source, count in sources.items():
            print(f"   • {source.capitalize():10s}: {count} messages")
        
        # Detailed summaries
        summaries = data.get('summaries_by_source', {})
        
        for source in ['gmail', 'outlook', 'teams']:
            print_section(f"{source.upper()} Summary")
            
            source_data = summaries.get(source, {})
            message_count = source_data.get('message_count', 0)
            summary = source_data.get('summary', 'N/A')
            bullets = source_data.get('bullets', [])
            messages = source_data.get('messages', [])
            status = source_data.get('status', 'unknown')
            
            if status == 'error':
                print(f"❌ Error: {source_data.get('error', 'Unknown error')}")
                continue
            
            if message_count == 0:
                print(f"ℹ️  {summary}")
                continue
            
            print(f"\n📊 Messages: {message_count}")
            print(f"\n📝 AI Summary:")
            print(f"   {summary}")
            
            if bullets:
                print(f"\n🎯 Key Points:")
                for i, bullet in enumerate(bullets, 1):
                    print(f"   {i}. {bullet}")
            
            if messages:
                print(f"\n✉️  Recent Messages (showing {len(messages)}):")
                for i, msg in enumerate(messages[:5], 1):  # Show top 5
                    subject = msg.get('subject', 'No Subject')
                    sender = msg.get('sender', 'Unknown')
                    importance = msg.get('importance_score', 0)
                    is_read = msg.get('is_read', False)
                    
                    read_icon = "📧" if not is_read else "📬"
                    priority_icon = "🔴" if importance >= 0.7 else "🟡" if importance >= 0.5 else "🟢"
                    
                    print(f"   {i}. {read_icon} {priority_icon} {subject[:50]}...")
                    print(f"      From: {sender}")
                    print(f"      Importance: {importance:.2f}")
        
        return data
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out. This might happen if:")
        print("   - Fetching messages is taking too long")
        print("   - OpenAI API is slow")
        print("   - You have many messages to process")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_different_modes():
    """Test different summarization modes"""
    print_section("3. Testing Different Summary Modes")
    
    modes = ["executive", "bullets", "paragraph"]
    
    for mode in modes:
        print(f"\n📝 Testing mode: {mode}")
        print("-" * 80)
        
        result = test_summarize_by_source(max_per_source=5, mode=mode)
        
        if result:
            gmail_summary = result.get('summaries_by_source', {}).get('gmail', {})
            if gmail_summary.get('message_count', 0) > 0:
                print(f"\n✅ {mode.capitalize()} mode summary:")
                print(f"   {gmail_summary.get('summary', 'N/A')[:200]}...")
        
        print()

def main():
    """Main test function"""
    print("\n" + "=" * 80)
    print("  AI INBOX SUMMARIZATION TEST")
    print("  Testing: POST /unified/inbox/summarize-by-source")
    print("=" * 80)
    print(f"\n🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Health checks
    if not test_health_checks():
        print("\n⚠️  WARNING: Some services are not running!")
        print("   Please ensure all services are started:")
        print("   - Aggregator (port 8001)")
        print("   - LLM Service (port 8002)")
        print("   - MCP Server (port 8000)")
        print("\n   Continuing with tests anyway...")
    
    # Test 2: Main summarization test
    result = test_summarize_by_source(max_per_source=20, mode="executive")
    
    if not result:
        print("\n❌ Main test failed!")
        return False
    
    # Test 3: Different modes (optional - commented out for speed)
    # test_different_modes()
    
    # Final summary
    print_section("✅ TEST COMPLETE")
    print(f"\n🕐 Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if result:
        total = result.get('total_messages', 0)
        sources = result.get('sources', {})
        print(f"\n📊 Summary:")
        print(f"   Total messages processed: {total}")
        print(f"   Gmail: {sources.get('gmail', 0)}")
        print(f"   Outlook: {sources.get('outlook', 0)}")
        print(f"   Teams: {sources.get('teams', 0)}")
        print("\n✅ AI summarization is working correctly!")
        return True
    else:
        print("\n❌ Test failed - check errors above")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

