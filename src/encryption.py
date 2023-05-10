import random
from pprint import pprint


# chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;?@[\]^_`{|}~'
# charList = list(chars)
# random.shuffle(charList)
# randChar = ''.join(charList)
# print(randChar)
# print(len(randChar)) # length=91

# x = 'O2H\m{)M\'h,u(?GyaT;B34i:f8gEvzRq[V/ZPr0}1-Q6%K5Xx&^!tJ]U*@+sCp#n|Y$_b7Aw9c.eNDj~dlkIW"`SoLF '

# KEY = {}
# for char in chars:
#     k = char
#     v = ''

#     for _ in range(2):
#         v += random.choice(x)

#     KEY[k] = v

# pprint(KEY)


class MyEncryption:
    """Encryption/decryption algorithm by M.H. 11/22/2022"""

    def __init__(self):
        """Initialize secret keys for encryption."""
        self.key_d = {'!': 'jQ',
                      '"': '-Z',
                      '#': '!J',
                      '$': 'G,',
                      '%': '8a',
                      '&': 'YL',
                      "'": ']y',
                      '(': ';5',
                      ')': '/@',
                      '*': '.*',
                      '+': 'JX',
                      ',': 'A9',
                      '-': 'h~',
                      '.': 'Op',
                      '/': 'wK',
                      '0': 'yJ',
                      '1': '[3',
                      '2': 'c~',
                      '3': 'Nz',
                      '4': ',|',
                      '5': 'tF',
                      '6': ')$',
                      '7': '+}',
                      '8': 'lX',
                      '9': 'R}',
                      ':': 'k7',
                      ';': 'Hj',
                      '?': '_I',
                      '@': ')p',
                      'A': '.|',
                      'B': 'NI',
                      'C': 'op',
                      'D': 'tk',
                      'E': '+b',
                      'F': 'g^',
                      'G': '`\\',
                      'H': 'ih',
                      'I': '__',
                      'J': '[m',
                      'K': 'ZF',
                      'L': '93',
                      'M': 'Zr',
                      'N': ':?',
                      'O': ')W',
                      'P': ',}',
                      'Q': '4K',
                      'R': 'E(',
                      'S': 'k/',
                      'T': 'Q*',
                      'U': "t'",
                      'V': 'Ra',
                      'W': '79',
                      'X': 'yO',
                      'Y': 'f$',
                      'Z': 'M{',
                      '[': 'D.',
                      '\\': 'Do',
                      ']': 'M[',
                      '^': '8t',
                      '_': 'g&',
                      '`': 'j6',
                      'a': 'y]',
                      'b': '!G',
                      'c': '._',
                      'd': "'T",
                      'e': '*F',
                      'f': ':Z',
                      'g': 'P9',
                      'h': '6r',
                      'i': 'H!',
                      'j': '_W',
                      'k': '8Z',
                      'l': 'GM',
                      'm': '$"',
                      'n': 'c,',
                      'o': 'R+',
                      'p': '`o',
                      'q': '*f',
                      'r': '@3',
                      's': 'X4',
                      't': '/0',
                      'u': 's8',
                      'v': 'FT',
                      'w': "2'",
                      'x': 'uk',
                      'y': 'i~',
                      'z': '[T',
                      '{': '7y',
                      '|': 'gR',
                      '}': 'N*',
                      '~': 'o*',
                      ' ': '.e',
                      '=': 'qL',
                      '<': 'i#',
                      '>': '(?',
                      '\t': '=t',
                      '\n': '>`', }
        self.key_s = 'O2H\m{)M\'h,u\n(?GyaT;B3\t4i:f8gEvzRq[V/ZPr0}1-Q6%K5Xx&^!tJ]U*@+sCp#n|Y$_b7Aw9c.eNDj~dlkIW"`SoLF =<>'

    def mirror(self, message: str) -> str:
        """Returns a mirror of a string."""
        mirrorMessage = ''
        messageList = list(message)
        for _ in range(len(messageList)):
            lastChar = messageList.pop()
            mirrorMessage += lastChar

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
        newMessage = ''
        for char in message:
            subChar = self.key_d[char]
            newMessage += subChar

        return newMessage

    def revSubstitution(self, message: str) -> str:
        """Reverse substituted message."""
        index1 = 0
        index2 = 1
        decryptedMessage = ''
        for _ in range(int(len(message)/2)):
            char1 = message[index1]
            char2 = message[index2]
            value = char1 + char2
            for k, v in self.key_d.items():
                if v == value:
                    decryptedMessage += k

            index1 += 2
            index2 += 2

        return decryptedMessage

    def encrypt(self, message, shiftNum=5):
        """Encrypt message using my secret algorithm."""
        stage1 = self.mirror(message)
        stage2 = self.caesar(stage1, shift=shiftNum)
        stage3 = self.substitution(stage2)
        return stage3

    def decrypt(self, encryptedMessage, shiftNum=5):
        """Decrypt message using my secret algorithm."""
        stage1 = self.revSubstitution(encryptedMessage)
        stage2 = self.caesar(stage1, cipher=-1, shift=shiftNum)
        stage3 = self.mirror(stage2)
        return stage3


if __name__ == '__main__':
    edc = MyEncryption()
