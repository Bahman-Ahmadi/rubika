import base64,urllib3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class encryption:
	def __init__(self, auth): self.key, self.iv = bytearray(self.secret(auth), "UTF-8"), bytearray.fromhex('00000000000000000000000000000000')

	def secret(self, e):
		t, n, s = e[0:8], e[16:24]+e[0:8]+e[24:32]+e[8:16], 0
		while s < len(n):
			t = chr((ord(n[s][0]) - ord('0') + 5) % 10 + ord('0')) if n[s] >= '0' and n[s] <= '9' else chr((ord(n[s][0]) - ord('a') + 9) % 26 + ord('a'))
			n, s = self.replaceCharAt(n, s, t), s+1
		return n

	replaceCharAt = lambda self, e, t, i: e[0:t] + i + e[t + len(i):]
	encrypt       = lambda self, text: base64.b64encode(AES.new(self.key, AES.MODE_CBC, self.iv).encrypt(pad(text.encode('UTF-8'), AES.block_size))).decode('UTF-8')
	decrypt       = lambda self, text: unpad(AES.new(self.key, AES.MODE_CBC, self.iv).decrypt(base64.urlsafe_b64decode(text.encode('UTF-8'))), AES.block_size).decode('UTF-8')