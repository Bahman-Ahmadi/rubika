from requests import post
from random import randint
from json import loads, dumps
import asyncio,base64,glob,json,math,urllib3,os,pathlib,random,sys,concurrent.futures,time
from tqdm import tqdm
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class encryption:
    def __init__(self, auth):
        self.key = bytearray(self.secret(auth), "UTF-8")
        self.iv = bytearray.fromhex('00000000000000000000000000000000')

    def replaceCharAt(self, e, t, i):
        return e[0:t] + i + e[t + len(i):]

    def secret(self, e):
        t = e[0:8]
        i = e[8:16]
        n = e[16:24] + t + e[24:32] + i
        s = 0
        while s < len(n):
            e = n[s]
            if e >= '0' and e <= '9':
                t = chr((ord(e[0]) - ord('0') + 5) % 10 + ord('0'))
                n = self.replaceCharAt(n, s, t)
            else:
                t = chr((ord(e[0]) - ord('a') + 9) % 26 + ord('a'))
                n = self.replaceCharAt(n, s, t)
            s += 1
        return n

    def encrypt(self, text):
        raw = pad(text.encode('UTF-8'), AES.block_size)
        aes = AES.new(self.key, AES.MODE_CBC, self.iv)
        enc = aes.encrypt(raw)
        result = base64.b64encode(enc).decode('UTF-8')
        return result

    def decrypt(self, text):
        aes = AES.new(self.key, AES.MODE_CBC, self.iv)
        dec = aes.decrypt(base64.urlsafe_b64decode(text.encode('UTF-8')))
        result = unpad(dec, AES.block_size).decode('UTF-8')
        return result


class Bot:
	def __init__(self, auth):
		self.auth = auth
		self.enc = encryption(auth)
		
	def sendMessage(self, chat_id, text, message_id=None):
		if message_id == None:
			return post(json={"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps({
				"method":"sendMessage",
				"input":{
					"object_guid":chat_id,
					"rnd":f"{randint(100000,900000)}",
					"text":text,
					"reply_to_message_id":message_id
				},
				"client":{
					"app_name":"Main",
					"app_version":"3.2.1",
					"platform":"Web",
					"package":"web.rubika.ir",
					"lang_code":"fa"
				}
			}))},url="https://messengerg2c17.iranlms.ir/")
		else:
			return post(json={"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps({
				"method":"sendMessage",
				"input":{
					"object_guid":chat_id,
					"rnd":f"{randint(100000,900000)}",
					"text":text,
					"reply_to_message_id":message_id
				},
				"client":{
					"app_name":"Main",
					"app_version":"3.2.1",
					"platform":"Web",
					"package":"web.rubika.ir",
					"lang_code":"fa"
				}
			}))},url="https://messengerg2c17.iranlms.ir/")
	
	def deleteMessages(self, chat_id, message_ids):
		return post(json={"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"deleteMessages",
			"input":{
				"object_guid":chat_id,
				"message_ids":message_ids,
				"type":"Global"
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url="https://messengerg2c66.iranlms.ir/")
	
	def getUserInfo(self, chat_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getUserInfo",
			"input":{
				"user_guid":chat_id
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url="https://messengerg2c37.iranlms.ir/").json()["data_enc"]))
	
	def getMessages(self, chat_id,min_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getMessagesInterval",
			"input":{
				"object_guid":chat_id,
				"middle_message_id":min_id
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url="https://messengerg2c67.iranlms.ir/").json().get("data_enc"))).get("data").get("messages")
		
	def getInfoByUsername(self, username):
		''' username should be without @ '''
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getObjectByUsername",
			"input":{
				"username":username
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url="https://messengerg2c23.iranlms.ir/").json().get("data_enc")))

	def banGroupMember(self, chat_id, user_id):
		return post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"banGroupMember",
			"input":{
				"group_guid": chat_id,
				"member_guid": user_id,
				"action":"Set"
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url="https://messengerg2c21.iranlms.ir/")

	def invite(self, chat_id, user_ids):
		return post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"addGroupMembers",
			"input":{
				"group_guid": chat_id,
				"member_guids": user_ids
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url="https://messengerg2c22.iranlms.ir/")
	
	def getGroupAdmins(self, chat_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"client":{
				"app_name":"Main",
				"app_version":"2.9.5",
				"lang_code":"fa",
				"package":"ir.resaneh1.iptv",
				"platform":"Android"
			},
			"input":{
				"group_guid":chat_id
			},
			"method":"getGroupAdminMembers"
		}))},url="https://messengerg2c22.iranlms.ir/").json().get("data_enc")))

	def getMessagesInfo(self, chat_id, message_ids):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getMessagesByID",
			"input":{
				"object_guid": chat_id,
				"message_ids": message_ids
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))}, url="https://messengerg2c24.iranlms.ir/").json()["data_enc"])).get("data").get("messages")

	def setMembersAccess(self, chat_id, access_list):
		return post(json={
			"api_version": "4",
			"auth": self.auth,
			"client": {
				"app_name": "Main",
				"app_version": "2.9.5",
				"lang_code": "fa",
				"package": "ir.resaneh1.iptv",
				"platform": "Android"
			},
			"data_enc": self.enc.encrypt(dumps({
				"access_list": access_list,
				"group_guid": chat_id
			})),
			"method": "setGroupDefaultAccess"
		}, url="https://messengerg2c24.iranlms.ir/")

	def getGroupMembers(self, chat_id):
		return loads(self.enc.decrypt(post(json={
			"api_version": "4",
			"auth": self.auth,
			"client": {
				"app_name": "Main",
				"app_version": "2.9.5",
				"lang_code": "fa",
				"package": "ir.resaneh1.iptv",
				"platform": "Android"
			},
			"data_enc": self.enc.encrypt(dumps({
				"group_guid": chat_id
			})),
			"method": "getGroupAllMembers"
		}, url="https://messengerg2c17.iranlms.ir/").json()["data_enc"]))["data"]["in_chat_members"]

	def getGroupInfo(self, chat_id):
		return loads(self.enc.decrypt(post(
			json={
				"api_version":"5",
				"auth": self.auth,
				"data_enc": self.enc.encrypt(dumps({
					"method":"getGroupInfo",
					"input":{
						"group_guid": chat_id,
					},
					"client":{
						"app_name":"Main",
						"app_version":"3.2.1",
						"platform":"Web",
						"package":"web.rubika.ir",
						"lang_code":"fa"
					}
			}))}, url="https://messengerg2c24.iranlms.ir/").json()["data_enc"]))
