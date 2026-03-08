from odoo import models
from pathlib import Path
from cryptography.fernet import Fernet
from odoo.modules.module import get_module_path

class EVEncrypt(models.AbstractModel):
    _name = "ev.tools.encrypt"

    def _get_cipher(self):
        module_path = Path(get_module_path("ev_tools"))
        key_path = module_path / "private" / "evapp.key"

        key_path.parent.mkdir(parents=True, exist_ok=True)

        if key_path.exists():
            key = key_path.read_bytes()
        else:
            key = Fernet.generate_key()
            key_path.write_bytes(key)

        return Fernet(key)

    def encrypt(self, text: str):
        """Encrypt text"""
        cipher = self._get_cipher()
        return cipher.encrypt(text.encode()).decode()

    def decrypt(self, encrypted_text: str):
        """Decrypt text"""
        cipher = self._get_cipher()
        return cipher.decrypt(encrypted_text.encode()).decode()