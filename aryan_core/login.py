import requests
import json
import base64
import time
import random
import uuid
import string
import secrets
import os
from Cryptodome.Cipher import AES, PKCS1_v1_5
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from user_agent import generate_user_agent

# Session file for persisting login sessions
SESSION_FILE = "instagram_session.json"

def generate_jazoest(symbols: str) -> str:
    amount = sum(ord(s) for s in symbols)
    return f"2{amount}"

def gen_token(size=10, symbols=False) -> str:
    """Generate CSRF or other token."""
    chars = string.ascii_letters + string.digits
    if symbols:
        chars += string.punctuation
    return "".join(random.choice(chars) for _ in range(size))

def enc(pw):
    pki, pk = get_pks()
    sk = get_random_bytes(32)
    iv = get_random_bytes(12)
    ts = str(int(time.time()))
    dpk = base64.b64decode(pk.encode())
    rk = RSA.import_key(dpk)
    cr = PKCS1_v1_5.new(rk)
    re = cr.encrypt(sk)
    ca = AES.new(sk, AES.MODE_GCM, iv)
    ca.update(ts.encode())
    ae, tg = ca.encrypt_and_digest(pw.encode("utf8"))
    sb = len(re).to_bytes(2, byteorder="little")
    pl = base64.b64encode(
        b"".join(
            [
                b"\x01",
                pki.to_bytes(1, byteorder="big"),
                iv,
                sb,
                re,
                tg,
                ae,
            ]
        )
    )
    return f"#PWD_INSTAGRAM:4:{ts}:{pl.decode()}"

def get_pks():
    resp = requests.get("https://i.instagram.com/api/v1/qe/sync/", verify=False)
    publickeyid = int(resp.headers.get("ig-set-password-encryption-key-id"))
    publickey = resp.headers.get("ig-set-password-encryption-pub-key")
    return publickeyid, publickey

class InstagramLogin:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.requires_2fa = False
        self.two_factor_identifier = None
        self.requires_captcha = False
        self.captcha_url = None
        self.device_id = None
        self.phone_id = None
        self.guid = None
        self.adid = None
        
        # Load existing session if available
        self._load_session()
    
    def _load_session(self):
        """Load existing session from file"""
        try:
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, 'r') as f:
                    session_data = json.load(f)
                    self.device_id = session_data.get('device_id')
                    self.phone_id = session_data.get('phone_id')
                    self.guid = session_data.get('guid')
                    self.adid = session_data.get('adid')
                    self.auth_token = session_data.get('auth_token')
                    self.user_id = session_data.get('user_id')
                    # Load cookies if available
                    if 'cookies' in session_data:
                        self.session.cookies.update(session_data['cookies'])
        except Exception as e:
            print(f"Error loading session: {e}")
    
    def _save_session(self):
        """Save current session to file"""
        try:
            session_data = {
                'device_id': self.device_id,
                'phone_id': self.phone_id,
                'guid': self.guid,
                'adid': self.adid,
                'auth_token': self.auth_token,
                'user_id': self.user_id,
                'cookies': dict(self.session.cookies)
            }
            with open(SESSION_FILE, 'w') as f:
                json.dump(session_data, f)
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def _generate_device_ids(self):
        """Generate consistent device IDs"""
        if not self.device_id:
            self.device_id = f"android-{uuid.uuid4().hex[:16]}"
        if not self.phone_id:
            self.phone_id = str(uuid.uuid4())
        if not self.guid:
            self.guid = str(uuid.uuid4())
        if not self.adid:
            self.adid = str(uuid.uuid4())
    
    def _get_headers(self):
        """Get consistent headers for requests"""
        timestamp = int(time.time())
        return {
            "Host": "i.instagram.com",
            "Accept": "*/*",
            "X-IG-App-Locale": "en_US",
            "X-IG-Device-Locale": "en_US",
            "X-IG-Mapped-Locale": "en_US",
            "X-Pigeon-Session-Id": f"UFS-{uuid.uuid4()}",
            "X-Pigeon-Rawclienttime": str(timestamp),
            "X-IG-Bandwidth-Speed-KBPS": "2880.01",
            "X-IG-Bandwidth-TotalBytes-B": "82172548",
            "X-IG-Bandwidth-TotalTime-MS": "3917",
            "X-IG-App-Startup-Country": "US",
            "X-Bloks-Version-Id": "ce555e5500576acd8e84a66018f54a05720f2dce29f0bb5a1f97f0c10d6fac48",
            "X-IG-WWW-Claim": "0",
            "X-Bloks-Is-Layout-RTL": "false",
            "X-Bloks-Is-Panorama-Enabled": "true",
            "X-IG-Device-ID": self.device_id,
            "X-IG-Family-Device-ID": self.guid,
            "X-IG-Android-ID": self.device_id,
            "X-IG-Timezone-Offset": "-14400",
            "X-IG-Connection-Type": "WIFI",
            "X-IG-Capabilities": "3brTvx0=",
            "X-IG-App-ID": "567067343352427",
            "Priority": "u=3",
            "User-Agent": "Instagram 269.0.0.18.75 Android (26/8.0.0; 480dpi; 1080x1920; OnePlus; 6T Dev; devitron; qcom; en_US; 314665256)",
            "Accept-Language": "en-US",
            "X-MID": str(uuid.uuid4()),
            "X-FB-HTTP-Engine": "Liger",
            "Connection": "keep-alive",
            "X-FB-Client-IP": "True",
            "X-FB-Server-Cluster": "True",
            "IG-INTENDED-USER-ID": "0",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept-Encoding": "gzip, deflate"
        }
    
    def login(self, username: str, password: str, verification_code=None, captcha_response=None):
        """Login to Instagram with support for 2FA and captcha"""
        
        # Generate consistent device IDs
        self._generate_device_ids()
        
        enc_password = enc(password)
        
        data = {
            "jazoest": generate_jazoest(username),
            "country_codes": '[{"country_code":"1","source":["default"]}]',
            "phone_id": self.phone_id,
            "enc_password": enc_password,
            "username": username,
            "adid": self.adid,
            "guid": self.guid,
            "device_id": self.device_id,
            "google_tokens": "[]",
            "login_attempt_count": "0"
        }
        
        if verification_code and self.two_factor_identifier:
            data["verification_code"] = verification_code
            data["two_factor_identifier"] = self.two_factor_identifier
        
        if captcha_response:
            data["captcha_response"] = captcha_response
        
        headers = self._get_headers()
        
        try:
            # Add delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            res = self.session.post(
                "https://i.instagram.com/api/v1/accounts/login/",
                data=data,
                headers=headers,
                verify=False
            )
            
            response_data = res.json()
            
            if res.status_code == 200:
                self.auth_token = res.headers.get('ig-set-authorization')
                self.user_id = response_data.get("logged_in_user", {}).get("pk")
                self.requires_2fa = False
                self.requires_captcha = False
                
                # Save session
                self._save_session()
                
                return {
                    "success": True,
                    "auth_token": self.auth_token,
                    "user_id": self.user_id,
                    "message": "Login successful"
                }
            
            elif response_data.get("two_factor_required"):
                self.requires_2fa = True
                self.two_factor_identifier = response_data.get("two_factor_info", {}).get("two_factor_identifier")
                return {
                    "success": False,
                    "requires_2fa": True,
                    "two_factor_identifier": self.two_factor_identifier,
                    "message": "2FA required. Please provide verification code."
                }
            
            elif response_data.get("challenge_required"):
                challenge_url = response_data.get("challenge", {}).get("api_path")
                challenge_context = response_data.get("challenge", {}).get("challenge_context")
                return {
                    "success": False,
                    "requires_challenge": True,
                    "challenge_url": challenge_url,
                    "challenge_context": challenge_context,
                    "message": "Challenge required. Please complete the challenge."
                }
            
            elif response_data.get("checkpoint_required"):
                checkpoint_url = response_data.get("checkpoint_url")
                checkpoint_data = response_data.get("checkpoint_data")
                return {
                    "success": False,
                    "requires_checkpoint": True,
                    "checkpoint_url": checkpoint_url,
                    "checkpoint_data": checkpoint_data,
                    "message": "Checkpoint required. Please verify your account."
                }
            
            elif response_data.get("invalid_credentials"):
                return {
                    "success": False,
                    "message": "Invalid username or password. Please check your credentials."
                }
            
            elif response_data.get("inactive_user"):
                return {
                    "success": False,
                    "message": "Your account has been deactivated. Please contact Instagram support."
                }
            
            elif response_data.get("rate_limit_error"):
                return {
                    "success": False,
                    "message": "Rate limit exceeded. Please wait a few minutes and try again."
                }
            
            else:
                error_message = response_data.get("message", "Login failed")
                # Handle specific error messages
                if "email" in error_message.lower() or "help you get back" in error_message.lower():
                    return {
                        "success": False,
                        "message": "Instagram detected suspicious activity. Please try the following:\n1. Login to Instagram manually first\n2. Verify your email/phone\n3. Wait 24 hours and try again\n4. Use a different IP address or proxy",
                        "requires_manual_verification": True
                    }
                return {
                    "success": False,
                    "message": error_message,
                    "response": response_data
                }
        
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }
    
    def verify_2fa(self, username, password, verification_code):
        """Verify 2FA code"""
        return self.login(username, password, verification_code=verification_code)
    
    def get_session(self):
        """Get the current session"""
        return self.session
    
    def get_auth_token(self):
        """Get the current auth token"""
        return self.auth_token
    
    def get_user_id(self):
        """Get the current user ID"""
        return self.user_id
    
    def is_logged_in(self):
        """Check if currently logged in"""
        return self.auth_token is not None and self.user_id is not None
    
    def logout(self):
        """Logout and clear session"""
        self.auth_token = None
        self.user_id = None
        self.requires_2fa = False
        self.two_factor_identifier = None
        self.session.cookies.clear()
        
        # Remove session file
        try:
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
        except Exception as e:
            print(f"Error removing session file: {e}")

def login(username: str, password: str, verification_code=None):
    """Legacy login function for backward compatibility"""
    login_handler = InstagramLogin()
    result = login_handler.login(username, password, verification_code)
    
    if result["success"]:
        return [True, result["auth_token"], result["user_id"]]
    elif result.get("requires_2fa"):
        return [False, "2FA_REQUIRED", result.get("two_factor_identifier")]
    else:
        return [False, result.get("message")]
