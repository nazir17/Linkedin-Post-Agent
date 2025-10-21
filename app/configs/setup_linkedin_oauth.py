# FILE: app/configs/setup_linkedin_oauth.py

import os
from dotenv import load_dotenv, set_key
import webbrowser
from urllib.parse import urlencode, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8888/callback"
SCOPES = ["openid", "profile", "w_member_social"]


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if '?' in self.path:
            query = parse_qs(self.path.split('?')[1])
            auth_code = query.get('code', [None])[0]
            error = query.get('error', [None])[0]
            
            if error:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                error_desc = query.get('error_description', ['Unknown error'])[0]
                # ✅ FIX: Convert to bytes with .encode()
                self.wfile.write(f"<h1>❌ Authorization failed!</h1><p>{error}: {error_desc}</p>".encode())
                self.server.auth_code = None
            elif auth_code:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                # ✅ FIX: Convert to bytes with .encode()
                self.wfile.write("<h1>✅ Authorization successful!</h1><p>You can close this window.</p>".encode())
                self.server.auth_code = auth_code
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                # ✅ FIX: Convert to bytes with .encode()
                self.wfile.write("<h1>No authorization code received!</h1>".encode())
                self.server.auth_code = None
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass


def get_linkedin_access_token():
    """Complete OAuth flow"""
    print("=" * 60)
    print("LinkedIn OAuth Setup")
    print("=" * 60)
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("\n❌ Please add LinkedIn credentials to .env file")
        return
    
    print(f"\n✅ Client ID: {CLIENT_ID[:10]}...")
    print(f"✅ Redirect URI: {REDIRECT_URI}")
    
    auth_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES)
    }
    
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(auth_params)}"
    
    print("\n🌐 Opening browser...")
    print(f"URL: {auth_url}\n")
    
    try:
        webbrowser.open(auth_url)
    except:
        print("⚠️ Could not open browser. Please copy URL above.")
    
    print("Waiting for authorization...")
    
    try:
        server = HTTPServer(('localhost', 8888), CallbackHandler)
        server.auth_code = None
        server.handle_request()
        
        if not server.auth_code:
            print("\n❌ Authorization failed!")
            return
        
        print("✅ Authorization code received")
        
    except OSError as e:
        print(f"\n❌ Server error: {e}")
        return

    print("\n🔄 Exchanging code for token...")
    
    token_params = {
        "grant_type": "authorization_code",
        "code": server.auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    try:
        response = requests.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data=token_params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            
            print(f"\n✅ Access token obtained!")
            
            set_key(".env", "LINKEDIN_ACCESS_TOKEN", access_token)
            print(f"✅ Token saved to .env")
            
            test_response = requests.get(
                "https://api.linkedin.com/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            )
            
            if test_response.status_code == 200:
                user_data = test_response.json()
                print(f"\n✅ Token verified!")
                print(f"   Name: {user_data.get('name', 'N/A')}")
                print(f"   Email: {user_data.get('email', 'N/A')}")
                print("\n🎉 Setup complete!")
            else:
                print(f"\n⚠️ Token test failed: {test_response.status_code}")
        else:
            print(f"\n❌ Token exchange failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    get_linkedin_access_token()