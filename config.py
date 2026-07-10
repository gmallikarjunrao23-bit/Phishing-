import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ultra-premium-secret-key-2025")
    
    # Database
    DATABASE = "data/credentials.db"
    
    # Admin Panel
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "SecurePass2025")
    
    # Email Notification (optional)
    EMAIL_ENABLED = os.environ.get("EMAIL_ENABLED", "false").lower() == "true"
    SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "")
    EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
    EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT", "")
