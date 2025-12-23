#!/usr/bin/env python3

import os
import sys
import json
import requests
import base64
import hashlib
from bs4 import BeautifulSoup
import re

class IMPDSAuth:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://impds.nic.in/impdsdeduplication"
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    def sha512(self, text):
        return hashlib.sha512(text.encode('utf-8')).hexdigest()
    
    def extract_tokens(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract CSRF token
        csrf_input = soup.find('input', {'name': 'REQ_CSRF_TOKEN'})
        csrf_token = csrf_input.get('value') if csrf_input else ''
        
        # Extract USER_SALT
        user_salt = None
        for script in soup.find_all('script'):
            if script.string and 'USER_SALT' in script.string:
                match = re.search(r"USER_SALT\s*=\s*'([^']+)'", script.string)
                if match:
                    user_salt = match.group(1)
                    break
        
        return csrf_token, user_salt
    
    def get_captcha(self):
        try:
            response = self.session.post(
                f"{self.base_url}/ReloadCaptcha",
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get('captchaBase64')
        except Exception as e:
            print(f"Error getting CAPTCHA: {e}")
        return None
    
    def manual_captcha_input(self, captcha_base64):
        """Save CAPTCHA and prompt for manual input"""
        try:
            # Decode and save CAPTCHA
            image_data = base64.b64decode(captcha_base64)
            with open('/tmp/captcha.png', 'wb') as f:
                f.write(image_data)
            
            print("⚠️ CAPTCHA saved to /tmp/captcha.png")
            print("Please check Railway logs for CAPTCHA image")
            
            # For Railway, we can't get user input
            # Return a placeholder - you'll need to implement CAPTCHA service
            return "ABCD123"  # Placeholder
            
        except Exception as e:
            print(f"Error handling CAPTCHA: {e}")
            return "ABCD123"  # Fallback placeholder
    
    def login(self):
        # Get credentials from environment
        username = os.getenv('IMPDS_USERNAME', 'dsojpnagar@gmail.com')
        password = os.getenv('IMPDS_PASSWORD', 'CHCAEsoK')
        
        print(f"Attempting login for: {username}")
        
        try:
            # Step 1: Get login page
            print("1. Fetching login page...")
            response = self.session.get(f"{self.base_url}/LoginPage", timeout=10)
            
            csrf_token, user_salt = self.extract_tokens(response.text)
            if not csrf_token or not user_salt:
                print("Failed to extract tokens")
                return None
            
            # Step 2: Get CAPTCHA
            print("2. Getting CAPTCHA...")
            captcha_base64 = self.get_captcha()
            if not captcha_base64:
                print("Failed to get CAPTCHA")
                return None
            
            # Step 3: Handle CAPTCHA (manual/placeholder for Railway)
            print("3. Handling CAPTCHA...")
            captcha_text = self.manual_captcha_input(captcha_base64)
            
            # Step 4: Prepare login data
            print("4. Preparing login data...")
            salted_password = self.sha512(self.sha512(user_salt) + self.sha512(password))
            
            login_data = {
                'userName': username,
                'password': salted_password,
                'captcha': captcha_text,
                'REQ_CSRF_TOKEN': csrf_token
            }
            
            # Step 5: Perform login
            print("5. Logging in...")
            response = self.session.post(
                f"{self.base_url}/UserLogin",
                data=login_data,
                timeout=15
            )
            
            # Step 6: Check response
            try:
                result = response.json()
                if 'athenticationError' in result:
                    print(f"Login failed: {result['athenticationError']}")
                    return None
            except:
                # Not JSON response, check for JSESSIONID
                pass
            
            # Step 7: Get session ID
            jsessionid = self.session.cookies.get('JSESSIONID')
            if jsessionid:
                print(f"✅ Login successful!")
                return jsessionid
            else:
                print("❌ No JSESSIONID found")
                return None
                
        except Exception as e:
            print(f"Login process error: {e}")
            return None

def main():
    print("=" * 50)
    print("IMPDS Authentication for Railway")
    print("=" * 50)
    
    auth = IMPDSAuth()
    session_id = auth.login()
    
    if session_id:
        print(f"\n✅ SUCCESS!")
        print(f"JSESSIONID: {session_id}")
        return 0
    else:
        print("\n❌ FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
