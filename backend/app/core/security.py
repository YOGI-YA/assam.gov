import hashlib
import hmac
import base64
import json
import time
from typing import Optional, Dict, Any
from app.core.config import settings

# Robust, zero-dependency cryptographic password hasher (PBKDF2-HMAC-SHA256)
# Fully compatible across Python 3.10 - 3.14 on all platforms without external compilation issues

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    salt_b64 = base64.b64encode(salt).decode('ascii')
    key_b64 = base64.b64encode(key).decode('ascii')
    return f"pbkdf2:sha256:100000${salt_b64}${key_b64}"

import os

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        parts = hashed_password.split("$")
        if len(parts) != 3:
            return False
        salt = base64.b64decode(parts[1])
        target_key = base64.b64decode(parts[2])
        test_key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
        return hmac.compare_digest(target_key, test_key)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta_seconds: Optional[int] = None) -> str:
    to_encode = data.copy()
    now = int(time.time())
    if expires_delta_seconds:
        expire = now + expires_delta_seconds
    else:
        expire = now + (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    to_encode.update({"iat": now, "exp": expire})
    
    # Base64url encoded header and payload
    header = {"alg": "HS256", "typ": "JWT"}
    header_bytes = base64.urlsafe_b64encode(json.dumps(header).encode('utf-8')).rstrip(b'=')
    payload_bytes = base64.urlsafe_b64encode(json.dumps(to_encode).encode('utf-8')).rstrip(b'=')
    signing_input = header_bytes + b'.' + payload_bytes
    
    signature = hmac.new(settings.SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    signature_bytes = base64.urlsafe_b64encode(signature).rstrip(b'=')
    
    return (signing_input + b'.' + signature_bytes).decode('utf-8')

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        signing_input = f"{parts[0]}.{parts[1]}".encode('utf-8')
        signature = base64.urlsafe_b64decode(parts[2] + "==")
        expected_sig = hmac.new(settings.SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
        
        if not hmac.compare_digest(signature, expected_sig):
            return None
            
        payload_data = base64.urlsafe_b64decode(parts[1] + "==")
        payload = json.loads(payload_data.decode('utf-8'))
        
        # Check expiration
        if "exp" in payload and payload["exp"] < time.time():
            return None
            
        return payload
    except Exception:
        return None
