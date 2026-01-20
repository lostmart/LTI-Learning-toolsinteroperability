from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import base64
import json
from pathlib import Path

# Directory to store keys
KEYS_DIR = Path(__file__).parent.parent.parent / "keys"
KEYS_DIR.mkdir(exist_ok=True)

PRIVATE_KEY_PATH = KEYS_DIR / "private_key.pem"
PUBLIC_KEY_PATH = KEYS_DIR / "public_key.pem"

def generate_rsa_keypair():
    """Generate RSA key pair and save to files"""
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Save private key
    with open(PRIVATE_KEY_PATH, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Save public key
    public_key = private_key.public_key()
    with open(PUBLIC_KEY_PATH, 'wb') as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    
    return private_key, public_key

def load_private_key():
    """Load private key from file"""
    if not PRIVATE_KEY_PATH.exists():
        generate_rsa_keypair()
    
    with open(PRIVATE_KEY_PATH, 'rb') as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )

def load_public_key():
    """Load public key from file"""
    if not PUBLIC_KEY_PATH.exists():
        generate_rsa_keypair()
    
    with open(PUBLIC_KEY_PATH, 'rb') as f:
        return serialization.load_pem_public_key(
            f.read(),
            backend=default_backend()
        )

def get_jwks():
    """Generate JWKS (JSON Web Key Set) from public key"""
    public_key = load_public_key()
    
    # Get public numbers (for JWK format)
    public_numbers = public_key.public_numbers()
    
    # Convert to base64url format (required by JWK spec)
    def int_to_base64url(num):
        num_bytes = num.to_bytes((num.bit_length() + 7) // 8, byteorder='big')
        return base64.urlsafe_b64encode(num_bytes).rstrip(b'=').decode('utf-8')
    
    # Build JWK
    jwk = {
        "kty": "RSA",
        "use": "sig",
        "kid": "lti-key-1",  # Key ID
        "alg": "RS256",
        "n": int_to_base64url(public_numbers.n),  # modulus
        "e": int_to_base64url(public_numbers.e),  # exponent
    }
    
    return {
        "keys": [jwk]
    }