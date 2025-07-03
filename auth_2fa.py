import pyotp
import base64

def generate_2fa_secret():
    """Generiert einen neuen 2FA-Secret-Key (Base32)"""
    return pyotp.random_base32()

def get_totp_uri(username: str, secret: str, issuer_name="EduClass"):
    """Erstellt URI für QR-Code Scanner Apps"""
    return pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer_name)

def verify_2fa_code(secret: str, code: str):
    """Prüft, ob der eingegebene Code zum Secret passt"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)
