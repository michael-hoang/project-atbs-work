import random
from pprint import pprint


class EnDeCrypt:
    """Encryption/decryption algorithm by M.H. 11/22/2022"""

    def __init__(self):
        """Initialize secret keys for encryption."""
        self.key_d =  # [some secret key]
        self.key_s =  # [some secret key]

    def mirror(self, message: str) -> str:
        """Returns a mirror of a string."""
        # [some algorithm to mirror message]
        return mirrorMessage

    def caesar(self, message: str, shift, cipher=1) -> str:
        """Returns string with Caesar Cipher encryption."""
        shift = abs(int(shift))
        if cipher == -1:
            shift *= -1

        encryptedMessage = ''
        for char in message:
            charIndex = self.key_s.index(char)

            newCharIndex = charIndex + shift

            if newCharIndex > len(self.key_s) - 1:
                newCharIndex = newCharIndex % len(self.key_s)

            newChar = self.key_s[newCharIndex]
            encryptedMessage += newChar

        return encryptedMessage

    def substitution(self, message: str) -> str:
        """Substitutes each character in message by a 2-char key."""
        # [some algorithm for substitution]
        return newMessage

    def revSubstitution(self, message: str) -> str:
        """Reverse substituted message."""
        # [some algorithm for reverse substitution]
        return decryptedMessage

    def encrypt(self, message, shiftNum=5):
        """Encrypt message using my secret algorithm."""
        # [some algorithm to encrypt message]
        return encrypted_message

    def decrypt(self, encryptedMessage, shiftNum=5):
        """Decrypt message using my secret algorithm."""
        # [some algorithm to decrypt message]
        return decrypted_message


if __name__ == '__main__':
    edc = EnDeCrypt()
