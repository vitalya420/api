from cryptography.fernet import Fernet

from app.config import Config

fernet = Fernet(Config()['FERNET_KEY'].encode())
