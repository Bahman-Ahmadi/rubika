from pathlib import Path
from requests import post
from random import randint
from json import loads, dumps
import random, datetime, rubika.encryption

# because should be exist !
adminsAccess = {
	"pin":"PinMessages",
	"newAdmin":"SetAdmin",
	"editInfo":"ChangeInfo",
	"banMember":"BanMember",
	"changeLink":"SetJoinLink",
	"changeMembersAccess":"SetMemberAccess",
	"deleteMessages":"DeleteGlobalAllMessages"
}
usersAccess = {
	"addMember":"AddMember",
	"viewAdmins":"ViewAdmins",
	"viewMembers":"ViewMembers",
	"sendMessage":"SendMessages"
}

class Bot:
	def __init__(self, auth):
		self.auth = auth
		self.enc = rubika.encryption.encryption(auth)

	@staticmethod
	def _getURL():
		result = []
		for i in range(11,99): result.append(f"https://messengerg2c{i}.iranlms.ir/")
		return random.choice(result)

	def _requestSendFile(self, file):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"requestSendFile",
			"input":{
				"file_name": str(file.split("/")[-1]),
				"mime": file.split(".")[-1],
				"size": Path(file).stat().st_size
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url="https://messengerg2c64.iranlms.ir/").json()["data_enc"]))["data"]

	def _uploadFile(self, file):
		frequest = Bot._requestSendFile(self, file)
		bytef = open(file,"rb").read()

		hash_send = frequest["access_hash_send"]
		file_id = frequest["id"]
		url = frequest["upload_url"]

		header = {
			'auth':self.auth,
			'Host':url.replace("https://","").replace("/UploadFile.ashx",""),
			'chunk-size':str(Path(file).stat().st_size),
			'file-id':str(file_id),
			'access-hash-send':hash_send,
			"content-type": "application/octet-stream",
			"content-length": str(Path(file).stat().st_size),
			"accept-encoding": "gzip",
			"user-agent": "okhttp/3.12.1"
		}

		if len(bytef) <= 131072:
			header["part-number"], header["total-part"] = "1","1"

			while True:
				try:
					j = post(data=bytef,url=url,headers=header).text
					j = loads(j)['data']['access_hash_rec']
					break
				except Exception as e:
					continue

			return [frequest, j]
		else:
			t = random._floor(len(bytef) / 131072 + 1)
			for i in range(1,t+1):
				if i != t:
					k = i - 1
					k = k * 131072
					while True:
						try:
							header["chunk-size"], header["part-number"], header["total-part"] = "131072", str(i),str(t)
							o = post(data=bytef[k:k + 131072],url=url,headers=header).text
							o = loads(o)['data']
							break
						except Exception as e:
							continue
				else:
					k = i - 1
					k = k * 131072
					while True:
						try:
							header["chunk-size"], header["part-number"], header["total-part"] = str(len(bytef[k:])), str(i),str(t)
							p = post(data=bytef[k:],url=url,headers=header).text
							p = loads(p)['data']['access_hash_rec']
							break
						except Exception as e:
							continue
					return [frequest, p]

	def sendMessage(self, chat_id, text, metadata=[], message_id=None):
		inData = {
			"method":"sendMessage",
			"input":{
				"object_guid":chat_id,
				"rnd":f"{randint(100000,999999999)}",
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
		}
		if metadata != [] : inData["input"]["metadata"] = {"meta_data_parts":metadata}
		return post(json={"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps(inData))},url=Bot._getURL())

	def editMessage(self, message_id, chat_id, newText):
		return post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"editMessage",
			"input":{
				"message_id": message_id,
				"object_guid": chat_id,
				"text": newText
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url=Bot._getURL())

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
		}))},url=Bot._getURL())

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
		}))},url=Bot._getURL()).json()["data_enc"]))

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
		}))},url=Bot._getURL()).json().get("data_enc"))).get("data").get("messages")

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
		}))},url=Bot._getURL()).json().get("data_enc")))

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
		}))},url=Bot._getURL())

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
		}))},url=Bot._getURL())

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
		}))},url=Bot._getURL()).json().get("data_enc")))

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
		}))}, url=Bot._getURL()).json()["data_enc"])).get("data").get("messages")

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
		}, url=Bot._getURL())

	def getGroupMembers(self, chat_id):
		return loads(self.enc.decrypt(post(json={
			"api_version":"5",
				"auth": self.auth,
				"data_enc": self.enc.encrypt(dumps({
					"method":"getGroupAllMembers",
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
			}))
		}, url=Bot._getURL()).json()["data_enc"]))["data"]["in_chat_members"]

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
			}))}, url=Bot._getURL()).json()["data_enc"]))

	def getGroupLink(self, chat_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getGroupLink",
			"input":{
				"group_guid":chat_id
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url=Bot._getURL()).json().get("data_enc"))).get("data").get("join_link")

	def changeGroupLink(self, chat_id):
		return post(json={
			"api_version":"4",
			"auth":self.auth,
			"client":{
				"app_name":"Main",
				"app_version":"2.8.1",
				"lang_code":"fa",
				"package":"ir.resaneh1.iptv",
				"platform":"Android"
			},
			"data_enc":self.enc.encrypt(dumps({
				"group_guid": chat_id
			})),
			"method":"setGroupLink",
		},url=Bot._getURL())

	def setGroupTimer(self, chat_id, time):
		return post(json={
			"api_version":"4",
			"auth":self.auth,
			"client":{
				"app_name":"Main",
				"app_version":"2.8.1",
				"platform":"Android",
				"package":"ir.resaneh1.iptv",
				"lang_code":"fa"
			},
			"data_enc":self.enc.encrypt(dumps({
				"group_guid": chat_id,
				"slow_mode": time,
				"updated_parameters":["slow_mode"]
			})),
			"method":"editGroupInfo"
		},url=Bot._getURL())

	def setGroupAdmin(self, chat_id, user_id, access_list=[]):
		return post(json={"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"setGroupAdmin",
			"input":{
				"group_guid": chat_id,
				"access_list": access_list,
				"action": "SetAdmin",
				"member_guid": user_id
			},
			"client":{
				"app_name":"Main",
				"app_version":"2.8.1",
				"platform":"Android",
				"package":"ir.resaneh1.iptv",
				"lang_code":"fa"
			}
		}))},url=Bot._getURL())

	def deleteGroupAdmin(self, chat_id, user_id, access_list=[]):
		return post(json={"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"setGroupAdmin",
			"input":{
				"group_guid": chat_id,
				"action": "UnsetAdmin",
				"member_guid": user_id
			},
			"client":{
				"app_name":"Main",
				"app_version":"2.8.1",
				"platform":"Android",
				"package":"ir.resaneh1.iptv",
				"lang_code":"fa"
			}
		}))},url=Bot._getURL())

	def logout(self):
		return post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"logout",
			"input":{},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url=Bot._getURL())

	def forwardMessages(self, From, message_ids, to):
		return post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"forwardMessages",
			"input":{
				"from_object_guid": From,
				"message_ids": message_ids,
				"rnd": f"{randint(100000,999999999)}",
				"to_object_guid": to
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url=Bot._getURL())

	def seenChats(self, seenList):
		# seenList should be a dict , keys are object guids and values are last message’s id, {"guid":"msg_id"}
		return post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"seenChats",
			"input":{
				"seen_list": seenList
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url=Bot._getURL())

	def sendChatAction(self, chat_id, action):
		#every some seconds before sending message this request should send
		return post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"sendChatActivity",
			"input":{
				"activity": action,
				"object_guid": chat_id
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url=Bot._getURL())

	def pin(self, chat_id, message_id):
		return post(json={"api_version": "4", "auth": self.auth, "client": {
				"app_name": "Main",
				"app_version": "2.9.5",
				"lang_code": "fa",
				"package": "ir.resaneh1.iptv",
				"platform": "Android"
			},
			 "data_enc": self.enc.encrypt(dumps({
			 	"action":"Pin",
			 	"message_id": message_id,
			 	"object_guid": chat_id
			 })),
			"method": "setPinMessage"
		},url=Bot._getURL())

	def unpin(self, chat_id, message_id):
		return post(json={"api_version": "4", "auth": self.auth, "client": {
				"app_name": "Main",
				"app_version": "2.9.5",
				"lang_code": "fa",
				"package": "ir.resaneh1.iptv",
				"platform": "Android"
			},
			 "data_enc": self.enc.encrypt(dumps({
			 	"action":"Unpin",
			 	"message_id": message_id,
			 	"object_guid": chat_id
			 })),
			"method": "setPinMessage"
		},url=Bot._getURL())

	def joinGroup(self, link):
		hashLink = link.split("/")[-1]
		return post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"joinGroup",
			"input":{
				"hash_link": hashLink
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url=Bot._getURL())

	def leaveGroup(self, chat_id):
		return post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"leaveGroup",
			"input":{
				"group_guid": chat_id
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url=Bot._getURL())

	def block(self, chat_id):
		return post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"setBlockUser",
			"input":{
				"action": "Block",
				"user_guid": chat_id
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url=Bot._getURL())
		
	def unblock(self, chat_id):
		return post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"setBlockUser",
			"input":{
				"action": "Unblock",
				"user_guid": chat_id
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url=Bot._getURL())

	def sendPhoto(self, chat_id, file, size, thumbnail=None, caption=None, message_id=None):
		uresponse = Bot._uploadFile(self, file)
		file_inline = {
			"dc_id": uresponse[0]["dc_id"],
			"file_id": uresponse[0]["id"],
			"type":"Image",
			"file_name": file.split("/")[-1],
			"size": str(Path(file).stat().st_size),
			"mime": file.split(".")[-1],
			"access_hash_rec": uresponse[1],
			"width": size[0],
			"height": size[1],
			"thumb_inline": thumbnail or "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"
		}
		inData = {
				"method":"sendMessage",
				"input":{
					"file_inline": file_inline,
					"object_guid": chat_id,
					"rnd": f"{randint(100000,999999999)}",
					"reply_to_message_id": message_id
				},
				"client":{
					"app_name":"Main",
					"app_version":"3.2.1",
					"platform":"Web",
					"package":"web.rubika.ir",
					"lang_code":"fa"
				}
			}
		if caption != None: data["input"]["text"] = caption

		data = {"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps(inData))}
		return post(json=data,url=Bot._getURL())

	def sendVoice(self, chat_id, file, time, caption=None, message_id=None):
		# file's format should be ogg. time should be ms (type: float). 
		uresponse = Bot._uploadFile(self, file)

		inData = {
				"method":"sendMessage",
				"input":{
					"file_inline": {
						"dc_id": uresponse[0]["dc_id"],
						"file_id": uresponse[0]["id"],
						"type":"Voice",
						"file_name": file.split("/")[-1],
						"size": str(Path(file).stat().st_size),
						"time": time,
						"mime": file.split(".")[-1],
						"access_hash_rec": uresponse[1],
					},
					"object_guid":chat_id,
					"rnd":f"{randint(100000,999999999)}",
					"reply_to_message_id":message_id
				},
				"client":{
					"app_name":"Main",
					"app_version":"3.2.1",
					"platform":"Web",
					"package":"web.rubika.ir",
					"lang_code":"fa"
				}
			}

		if caption != None: inData["input"]["text"] = caption

		data = {
			"api_version":"5",
			"auth":self.auth,
			"data_enc":self.enc.encrypt(dumps(inData))
		}

		return post(json=data,url=Bot._getURL())

	def sendDocument(self, chat_id, file, caption=None, message_id=None):
		# Bot.sendDocument("guid","./file.txt", caption="anything", message_id="12345678")
		uresponse = Bot._uploadFile(self, file)

		file_id = str(uresponse[0]["id"])
		mime = file.split(".")[-1]
		dc_id = uresponse[0]["dc_id"]
		access_hash_rec = uresponse[1]
		file_name = file.split("/")[-1]
		size = str(Path(file).stat().st_size)

		data = {
				"api_version":"5",
				"auth":self.auth,
				"data_enc":self.enc.encrypt(dumps({
					"method":"sendMessage",
					"input":{
						"object_guid":chat_id,
						"reply_to_message_id":message_id,
						"rnd":f"{randint(100000,999999999)}",
						"file_inline":{
							"dc_id":str(dc_id),
							"file_id":str(file_id),
							"type":"File",
							"file_name":file_name,
							"size":size,
							"mime":mime,
							"access_hash_rec":access_hash_rec
						}
					},
					"client":{
						"app_name":"Main",
						"app_version":"3.2.1",
						"platform":"Web",
						"package":"web.rubika.ir",
						"lang_code":"fa"
					}
				}))
			}

		if caption != None: data["input"]["text"] = caption
		while True:
			try:
				return loads(self.enc.decrypt(loads(post(json=data,url=Bot._getURL()).text)['data_enc']))
				break
			except: continue

	def sendLocation(self, chat_id, location, message_id=None):
		# location = [float(x), float(y)]
		return post(json={
			"api_version":"4",
			"auth":self.auth,
			"client":{
				"app_name":"Main",
				"app_version":"2.8.1",
				"platform":"Android",
				"package":"ir.resaneh1.iptv",
				"lang_code":"fa"
			},
			"data_enc":self.enc.encrypt(dumps({
				"is_mute": False,
				"object_guid":chat_id,
				"rnd":f"{randint(100000,999999999)}",
				"location":{
					"latitude": location[0],
					"longitude": location[1]
				},
				"reply_to_message_id":message_id
			})),
			"method":"sendMessage"
		},url=Bot._getURL())

	def searchInChannelMembers(self, text, channel_guid):
		try:
			return loads(self.enc.decrypt(post(json={
				"api_version":"4",
				"auth":self.auth,
				"client":{
					"app_name":"Main",
					"app_version":"2.8.1",
					"platform":"Android",
					"package":"ir.resaneh1.iptv",
					"lang_code":"fa"
				},
				"data_enc":self.enc.encrypt(dumps({
					"channel_guid": channel_guid,
					"search_text": text
				})),
				"method":"getChannelAllMembers"
			},url=Bot._getURL()).json()["data_enc"]))["in_chat_members"]

		except KeyError: return None

	def getChatsUpdate(self):
		time_stamp = str(random._floor(datetime.datetime.today().timestamp()) - 200)
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getChatsUpdates",
			"input":{
				"state":time_stamp,
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url=Bot._getURL()).json().get("data_enc"))).get("data").get("chats")

	def getChatUpdate(self, chat_id):
		time_stamp = str(random._floor(datetime.datetime.today().timestamp()) - 200)
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getMessagesUpdates",
			"input":{
				"object_guid":chat_id,
				"state":time_stamp
			},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url=Bot._getURL()).json().get("data_enc"))).get("data").get("updated_messages")

	def myStickerSet(self):
		time_stamp = str(random._floor(datetime.datetime.today().timestamp()) - 200)
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getMyStickerSets",
			"input":{},
			"client":{
				"app_name":"Main",
				"app_version":"3.2.1",
				"platform":"Web",
				"package":"web.rubika.ir",
				"lang_code":"fa"
			}
		}))},url=Bot._getURL()).json().get("data_enc"))).get("data")
