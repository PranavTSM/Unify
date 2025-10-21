"""
Quick diagnostic to check if MCP server is working
"""

import requests
import sys

MCP_URL = "http://localhost:8000"

def check_service(url, name):
    """Check if a service is responding"""
    try:
        print(f"Checking {name}...", end=" ")
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ RUNNING")
            return True
        else:
            print(f"❌ BAD RESPONSE ({response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ NOT RUNNING")
        print(f"   Start with: cd mcp_server && python app.py")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT (not responding)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_endpoints():
    """Test critical endpoints"""
    print("\n" + "="*60)
    print("Testing MCP Endpoints")
    print("="*60)
    
    endpoints = [
        ("/gmail/messages", "Gmail Messages"),
        ("/outlook/messages", "Outlook Messages"),
        ("/teams/chats/all/messages", "Teams Messages"),
    ]
    
    for endpoint, name in endpoints:
        try:
            print(f"\n{name}: {MCP_URL}{endpoint}")
            print("  Fetching...", end=" ")
            response = requests.get(f"{MCP_URL}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    count = len(data)
                elif isinstance(data, dict) and 'value' in data:
                    count = len(data['value'])
                else:
                    count = '?'
                print(f"✅ OK ({count} messages)")
            elif response.status_code == 401:
                print("🔐 NEEDS AUTH")
                print(f"     Authenticate at: {MCP_URL}/google/auth or {MCP_URL}/msgraph/auth")
            elif response.status_code == 404:
                print("❌ ENDPOINT NOT FOUND")
            else:
                print(f"❌ ERROR ({response.status_code})")
                
        except requests.exceptions.Timeout:
            print("⏱️ TIMEOUT")
            print("     MCP server is slow or hanging")
        except requests.exceptions.ConnectionError:
            print("🔌 CONNECTION ERROR")
            break
        except Exception as e:
            print(f"❌ ERROR: {e}")

def main():
    print("\n" + "="*60)
    print("MCP SERVER DIAGNOSTIC")
    print("="*60 + "\n")
    
    # Check if MCP server is running
    if not check_service(MCP_URL, "MCP Server (port 8000)"):
        print("\n❌ MCP Server is not running!")
        print("\n💡 To start MCP server:")
        print("   cd mcp_server")
        print("   python app.py")
        print("\nThen run this diagnostic again.")
        return False
    
    # Check other services
    check_service("http://localhost:8001", "Aggregator (port 8001)")
    check_service("http://localhost:8002", "LLM Service (port 8002)")
    
    # Test endpoints
    test_endpoints()
    
    print("\n" + "="*60)
    print("AUTHENTICATION CHECK")
    print("="*60)
    print("\nIf you see '🔐 NEEDS AUTH' above, authenticate at:")
    print(f"  Google:    {MCP_URL}/google/auth")
    print(f"  Microsoft: {MCP_URL}/msgraph/auth")
    
    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)

