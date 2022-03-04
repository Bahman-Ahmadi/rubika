from re import findall
from pathlib import Path
from random import randint, choice
from json import loads, dumps, JSONDecodeError
from requests import post,get
import datetime, rubika.encryption

class accesses:
	class admin:
		pin               = "PinMessages"
		newAdmin          = "SetAdmin"
		editInfo          = "ChangeInfo"
		banMember         = "BanMember"
		changeLink        = "SetJoinLink"
		editMembersAccess = "SetMemberAccess"
		deleteMessages    = "DeleteGlobalAllMessages"

	class user:
		viewMembers = "ViewMembers"
		viewAdmins  = "ViewAdmins"
		sendMessage = "SendMessages"
		addMember   = "AddMember"

class clients:
	web = {
		"app_name"    : "Main",
		"app_version" : "3.2.2",
		"platform"    : "Web",
		"package"     : "web.shad.ir",
		"lang_code"   : "fa"
	}

	android = {
		"app_name"    : "Main",
		"app_version" : "2.9.8",
		"platform"    : "Android",
		"package"     : "ir.medu.shad",
		"lang_code"   : "fa"
	}

defaultDevice = {
	"app_version":"MA_2.9.8",
	"device_hash":"CEF34215E3E610825DC1C4BF9864D47A",
	"device_model":"rubika-library",
	"is_multi_account": False,
	"lang_code":"fa",
	"system_version":"SDK 22",
	"token":"cgpzI3mbTPKddhgKQV9lwS:APA91bE3ZrCdFosZAm5qUaG29xJhCjzw37wE4CdzAwZTawnHZM_hwZYbPPmBedllAHlm60v5N2ms-0OIqJuFd5dWRAqac2Ov-gBzyjMx5FEBJ_7nbBv5z6hl4_XiJ3wRMcVtxCVM9TA-",
	"token_type":"Firebase"
}

__version__ = "5.3.4"
__license__ = "MIT license"
__copyright__ = "Copyright (C) 2022 Bahman Ahmadi <github.com/Bahman-Ahmadi>"

class Bot:
	def __init__(self, app_name, phone_number=None, auth=None, displayWelcome=True, device=defaultDevice):
		if displayWelcome : print(f"welcome to rubika library version {__version__}\n{__copyright__}\n☞ docs : http://rubikalib.ml\n\nexecuting codes...\n")
		self.app_name = app_name
		try:
			with open(f"{app_name}.json", "r") as account:
				account = loads(account.read())
				self.auth = account["data"]["auth"]
		except FileNotFoundError:
				if auth != None:
					self.auth = auth
				elif phone_number != None:
					try:
						code = Bot.sendCode(phone_number).get("data").get("phone_code_hash")
						account = Bot.signIn(phone_number, code, input("please enter activation code : "))
						with open(f"{app_name}.json", "w") as file:
							file.write(dumps(account, indent=4, ensure_ascii=False))
						self.auth = account["data"]["auth"]
						Bot.registerDevice(self.auth, device=device)
					except KeyboardInterrupt:
						exit()
				else:
					try:
						phone_number = input("please enter your phone number : ")
						code = Bot.sendCode(phone_number).get("data").get("phone_code_hash")
						account = Bot.signIn(phone_number, code, input("please enter activation code : "))
						self.auth = account["data"]["auth"]
						with open(f"{app_name}.json", "w") as file:
							file.write(dumps(account, indent=4, ensure_ascii=False))
						Bot.registerDevice(self.auth, device=device)
					except KeyboardInterrupt:
						exit()
		except JSONDecodeError:
			raise RuntimeError(f"file is invalid. please login again to your account and then DO NOT modify the {app_name}.json")

		self.enc = rubika.encryption.encryption(self.auth)

	@staticmethod
	def _getURL():
		return "https://shadmessenger60.iranlms.ir/"
		'''
		return f"https://shadmessenger{randint(10,99)}.iranlms.ir/"
		'''

	@staticmethod
	def _tmpGeneration():
		tmp_session = ""
		choices = [*"abcdefghijklmnopqrstuvwxyz0123456789"]
		for i in range(32): tmp_session += choice(choices)
		return tmp_session

	@staticmethod
	def sendCode(phone_number):
		tmp = Bot._tmpGeneration()
		enc = rubika.encryption.encryption(tmp)
		while True:
			try:
				return loads(enc.decrypt(post(json={"api_version":"5","tmp_session": tmp,"data_enc": enc.encrypt(dumps({
					"method":"sendCode",
					"input":{
						"phone_number":f"98{phone_number[1:]}",
						"send_type":"SMS"
					},
					"client": clients.web
				}))},url=Bot._getURL()).json()["data_enc"]))
			except Exception as e: print(e)

	@staticmethod
	def signIn(phone_number,phone_code_hash,phone_code):
		'''
		phone_number : phone number of target's account : 09XXXXXXXXX
		phone_code_hash : hash of code sent to phone
		phone_code : code sent to phone
		'''
		while True:
			try:
				tmp = Bot._tmpGeneration()
				enc = rubika.encryption.encryption(tmp)
				return loads(enc.decrypt(post(json={"api_version":"5","tmp_session": tmp,"data_enc":enc.encrypt(dumps({
					"method":"signIn",
					"input":{
						"phone_number":f"98{phone_number[1:]}",
						"phone_code_hash":phone_code_hash,
						"phone_code":phone_code
					},
					"client": clients.web
				}))},url=Bot._getURL()).json().get("data_enc")))
			except Exception as e: print(e)

	@staticmethod
	def registerDevice(auth, device=defaultDevice):
		while True:
			try:
				enc = rubika.encryption.encryption(auth)
				response = loads(enc.decrypt(post(json={
					"api_version":"4",
					"auth":auth,
					"client": clients.android,
					"data_enc":enc.encrypt(dumps(device)),
					"method":"registerDevice",
				},url=Bot._getURL()).json()["data_enc"]))
				return response
			except JSONDecodeError: break

	@staticmethod
	def _parse(mode:str, text:str):
		results = []
		if mode.upper() == "HTML":
			realText = text.replace("<b>","").replace("</b>","").replace("<i>","").replace("</i>","").replace("<pre>","").replace("</pre>","")
			bolds = findall("<b>(.*?)</b>",text)
			italics = findall("<i>(.*?)</i>",text)
			monos = findall("<pre>(.*?)</pre>",text)

			bResult = [realText.index(i) for i in bolds]
			iResult = [realText.index(i) for i in italics]
			mResult = [realText.index(i) for i in monos]

			for bIndex,bWord in zip(bResult,bolds):
				results.append({
					"from_index": bIndex,
					"length": len(bWord),
					"type": "Bold"
				})
			for iIndex,iWord in zip(iResult,italics):
				results.append({
					"from_index": iIndex,
					"length": len(iWord),
					"type": "Italic"
				})
			for mIndex,mWord in zip(mResult,monos):
				results.append({
					"from_index": mIndex,
					"length": len(mWord),
					"type": "Mono"
				})

		elif mode.lower() == "markdown":
			realText = text.replace("**","").replace("__","").replace("`","")
			bolds = findall(r"\*\*(.*?)\*\*",text)
			italics = findall(r"\_\_(.*?)\_\_",text)
			monos = findall("`(.*?)`",text)

			bResult = [realText.index(i) for i in bolds]
			iResult = [realText.index(i) for i in italics]
			mResult = [realText.index(i) for i in monos]

			for bIndex,bWord in zip(bResult,bolds):
				results.append({
					"from_index": bIndex,
					"length": len(bWord),
					"type": "Bold"
				})
			for iIndex,iWord in zip(iResult,italics):
				results.append({
					"from_index": iIndex,
					"length": len(iWord),
					"type": "Italic"
				})
			for mIndex,mWord in zip(mResult,monos):
				results.append({
					"from_index": mIndex,
					"length": len(mWord),
					"type": "Mono"
				})

		return results

	def _requestSendFile(self, file):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"requestSendFile",
			"input":{
				"file_name": str(file.split("/")[-1]),
				"mime": file.split(".")[-1],
				"size": Path(file).stat().st_size
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))["data"]

	def _uploadFile(self, file):
		if not "http" in file:
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
				t = round(len(bytef) / 131072 + 1)
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
		else:
			frequest = loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
				"method":"requestSendFile",
				"input":{
					"file_name": file.split("/")[-1],
					"mime": file.split(".")[-1],
					"size": len(get(file).content)
				},
				"client": clients.web
			}))},url=Bot._getURL()).json()["data_enc"]))["data"]

			hash_send = frequest["access_hash_send"]
			file_id = frequest["id"]
			url = frequest["upload_url"]
			bytef = get(file).content

			header = {
				'auth':self.auth,
				'Host':url.replace("https://","").replace("/UploadFile.ashx",""),
				'chunk-size':str(len(get(file).content)),
				'file-id':str(file_id),
				'access-hash-send':hash_send,
				"content-type": "application/octet-stream",
				"content-length": str(len(get(file).content)),
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
				t = round(len(bytef) / 131072 + 1)
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

	@staticmethod
	def _getThumbInline(image_bytes:bytes):
		import io, base64, PIL.Image
		im = PIL.Image.open(io.BytesIO(image_bytes))
		width, height = im.size
		if height > width:
			new_height = 40
			new_width  = round(new_height * width / height)
		else:
			new_width  = 40
			new_height = round(new_width * height / width)
		im = im.resize((new_width, new_height), PIL.Image.ANTIALIAS)
		changed_image = io.BytesIO()
		im.save(changed_image, format='PNG')
		changed_image = changed_image.getvalue()
		return base64.b64encode(changed_image)

	@staticmethod
	def _getImageSize(image_bytes:bytes):
		import io, PIL.Image
		im = PIL.Image.open(io.BytesIO(image_bytes))
		width, height = im.size
		return [width , height]

	def sendMessage(self, chat_id, text, metadata=[], parse_mode=None, message_id=None):
		inData = {
			"method":"sendMessage",
			"input":{
				"object_guid":chat_id,
				"rnd":f"{randint(100000,999999999)}",
				"text":text,
				"reply_to_message_id":message_id
			},
			"client": clients.web
		}
		if metadata != [] : inData["input"]["metadata"] = {"meta_data_parts":metadata}
		if parse_mode != None :
			inData["input"]["metadata"] = {"meta_data_parts":Bot._parse(parse_mode, text)}
			inData["input"]["text"] = text.replace("<b>","").replace("</b>","").replace("<i>","").replace("</i>","").replace("<pre>","").replace("</pre>","") if parse_mode.upper() == "HTML" else text.replace("**","").replace("__","").replace("`","")

		return loads(self.enc.decrypt(post(json={"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps(inData))},url=Bot._getURL()).json()["data_enc"]))

	def editMessage(self, message_id, chat_id, newText, metadata=[], parse_mode=None):
		inData = {
			"method":"editMessage",
			"input":{
				"message_id": message_id,
				"object_guid": chat_id,
				"text": newText
			},
			"client": clients.web
		}
		if metadata != [] : inData["input"]["metadata"] = {"meta_data_parts":metadata}
		if parse_mode != None :
			inData["input"]["metadata"] = {"meta_data_parts":Bot._parse(parse_mode, text)}
			inData["input"]["text"] = text.replace("<b>","").replace("</b>","").replace("<i>","").replace("</i>","").replace("<pre>","").replace("</pre>","") if parse_mode.upper() == "HTML" else text.replace("**","").replace("__","").replace("`","")
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({inData}))},url=Bot._getURL()).json()["data_enc"]))

	def deleteMessages(self, chat_id, message_ids):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"deleteMessages",
			"input":{
				"object_guid":chat_id,
				"message_ids":message_ids,
				"type":"Global"
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def getUserInfo(self, chat_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getUserInfo",
			"input":{
				"user_guid":chat_id
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def getMessages(self, chat_id,min_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getMessagesInterval",
			"input":{
				"object_guid":chat_id,
				"middle_message_id":min_id
			},
			"client": clients.web
		}))},url=Bot._getURL()).json().get("data_enc"))).get("data").get("messages")

	def getInfoByUsername(self, username):
		''' username should be without @ '''
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getObjectByUsername",
			"input":{
				"username":username
			},
			"client": clients.web
		}))},url=Bot._getURL()).json().get("data_enc")))

	def banGroupMember(self, chat_id, user_id):
		return loads(enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"banGroupMember",
			"input":{
				"group_guid": chat_id,
				"member_guid": user_id,
				"action":"Set"
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def unbanGroupMember(self, chat_id, user_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"client": clients.android,
			"input":{
				"group_guid": chat_id,
				"member_guid": user_id,
				"action":"Unset"
			},
			"method":"banGroupMember"
		}))},url=Bot._getURL()).json()["data_enc"]))

	def invite(self, chat_id, user_ids):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"addGroupMembers",
			"input":{
				"group_guid": chat_id,
				"member_guids": user_ids
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def inviteChannel(self, chat_id, user_ids):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"addChannelMembers",
			"input":{
				"channel_guid": chat_id,
				"member_guids": user_ids
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def getGroupAdmins(self, chat_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"client": clients.android,
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
			"client": clients.web
		}))}, url=Bot._getURL()).json()["data_enc"])).get("data").get("messages")

	def setMembersAccess(self, chat_id, access_list):
		return post(json={
			"api_version": "4",
			"auth": self.auth,
			"client": clients.android,
			"data_enc": self.enc.encrypt(dumps({
				"access_list": access_list,
				"group_guid": chat_id
			})),
			"method": "setGroupDefaultAccess"
		}, url=Bot._getURL())

	def getGroupMembers(self, chat_id, start_id=None):
		return loads(self.enc.decrypt(post(json={
			"api_version":"5",
				"auth": self.auth,
				"data_enc": self.enc.encrypt(dumps({
					"method":"getGroupAllMembers",
					"input":{
						"group_guid": chat_id,
						"start_id": start_id
					},
					"client": clients.web
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
					"client": clients.web
			}))}, url=Bot._getURL()).json()["data_enc"]))

	def getGroupLink(self, chat_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getGroupLink",
			"input":{
				"group_guid":chat_id
			},
			"client": clients.web
		}))},url=Bot._getURL()).json().get("data_enc"))).get("data").get("join_link")

	def changeGroupLink(self, chat_id):
		return loads(self.enc.decrypt(post(json={
			"api_version":"4",
			"auth":self.auth,
			"client": clients.android,
			"data_enc":self.enc.encrypt(dumps({
				"group_guid": chat_id
			})),
			"method":"setGroupLink",
		},url=Bot._getURL()).json()["data_enc"]))

	def setGroupTimer(self, chat_id, time):
		return loads(self.enc.decrypt(post(json={
			"api_version":"4",
			"auth":self.auth,
			"client": clients.android,
			"data_enc":self.enc.encrypt(dumps({
				"group_guid": chat_id,
				"slow_mode": time,
				"updated_parameters":["slow_mode"]
			})),
			"method":"editGroupInfo"
		},url=Bot._getURL()).json()["data_enc"]))

	def setGroupAdmin(self, chat_id, user_id, access_list=[]):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"setGroupAdmin",
			"input":{
				"group_guid": chat_id,
				"access_list": access_list,
				"action": "SetAdmin",
				"member_guid": user_id
			},
			"client": clients.android
		}))},url=Bot._getURL()).json()["data_enc"]))

	def deleteGroupAdmin(self, chat_id, user_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"setGroupAdmin",
			"input":{
				"group_guid": chat_id,
				"action": "UnsetAdmin",
				"member_guid": user_id
			},
			"client": clients.android
		}))},url=Bot._getURL()).json()["data_enc"]))

	def logout(self):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"logout",
			"input":{},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def forwardMessages(self, From, message_ids, to):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"forwardMessages",
			"input":{
				"from_object_guid": From,
				"message_ids": message_ids,
				"rnd": f"{randint(100000,999999999)}",
				"to_object_guid": to
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def seenChats(self, seenList):
		# seenList must be a dict , keys are object guids and values are last message’s id, {"guid":"msg_id"}
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"seenChats",
			"input":{
				"seen_list": seenList
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def sendChatAction(self, chat_id, action):
		#every some seconds before sending message this request should send
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"sendChatActivity",
			"input":{
				"activity": action,
				"object_guid": chat_id
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def pin(self, chat_id, message_id):
		return loads(self.enc.decrypt(post(json={"api_version": "4", "auth": self.auth, "client": clients.android,
			 "data_enc": self.enc.encrypt(dumps({
			 	"action":"Pin",
			 	"message_id": message_id,
			 	"object_guid": chat_id
			 })),
			"method": "setPinMessage"
		},url=Bot._getURL()).json()["data_enc"]))

	def unpin(self, chat_id, message_id):
		return loads(self.enc.decrypt(post(json={"api_version": "4", "auth": self.auth, "client": clients.android,
			 "data_enc": self.enc.encrypt(dumps({
			 	"action":"Unpin",
			 	"message_id": message_id,
			 	"object_guid": chat_id
			 })),
			"method": "setPinMessage"
		},url=Bot._getURL()).json()["data_enc"]))

	def joinGroup(self, link):
		hashLink = link.split("/")[-1]
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"joinGroup",
			"input":{
				"hash_link": hashLink
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def groupPreviewByJoinLink(self, link):
		hashLink = link.split("/")[-1]
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"groupPreviewByJoinLink",
			"input":{
				"hash_link": hashLink
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))["data"]

	def leaveGroup(self, chat_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"leaveGroup",
			"input":{
				"group_guid": chat_id
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def block(self, chat_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"setBlockUser",
			"input":{
				"action": "Block",
				"user_guid": chat_id
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def unblock(self, chat_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"setBlockUser",
			"input":{
				"action": "Unblock",
				"user_guid": chat_id
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def sendPhoto(self, chat_id, file, size=[], thumbnail=None, caption=None, message_id=None):
		uresponse = Bot._uploadFile(self, file)
		if thumbnail == None: thumbnail = "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"
		elif "." in thumbnail:thumbnail = str(Bot._getThumbInline(open(file,"rb").read() if not "http" in file else get(file).content))

		if size == []: size = Bot._getImageSize(open(file,"rb").read() if not "http" in file else get(file).content)

		file_inline = {
			"dc_id": uresponse[0]["dc_id"],
			"file_id": uresponse[0]["id"],
			"type":"Image",
			"file_name": file.split("/")[-1],
			"size": str(len(get(file).content if "http" in file else open(file,"rb").read())),
			"mime": file.split(".")[-1],
			"access_hash_rec": uresponse[1],
			"width": size[0],
			"height": size[1],
			"thumb_inline": thumbnail
		}
		inData = {
				"method":"sendMessage",
				"input":{
					"file_inline": file_inline,
					"object_guid": chat_id,
					"rnd": f"{randint(100000,999999999)}",
					"reply_to_message_id": message_id
				},
				"client": clients.web
			}
		if caption != None: inData["input"]["text"] = caption

		data = {"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps(inData))}
		return loads(self.enc.decrypt(post(json=data,url=Bot._getURL()).json()["data_enc"]))

	def sendVoice(self, chat_id, file, time, caption=None, message_id=None):
		# file's format must be ogg. time must be ms (type: float). 
		uresponse = Bot._uploadFile(self, file)
		inData = {
				"method":"sendMessage",
				"input":{
					"file_inline": {
						"dc_id": uresponse[0]["dc_id"],
						"file_id": uresponse[0]["id"],
						"type":"Voice",
						"file_name": file.split("/")[-1],
						"size": str(len(get(file).content if "http" in file else open(file,"rb").read())),
						"time": time,
						"mime": file.split(".")[-1],
						"access_hash_rec": uresponse[1],
					},
					"object_guid":chat_id,
					"rnd":f"{randint(100000,999999999)}",
					"reply_to_message_id":message_id
				},
				"client": clients.web
			}

		if caption != None: inData["input"]["text"] = caption

		data = {
			"api_version":"5",
			"auth":self.auth,
			"data_enc":self.enc.encrypt(dumps(inData))
		}

		return loads(self.enc.decrypt(post(json=data,url=Bot._getURL()).json()["data_enc"]))

	def sendDocument(self, chat_id, file, caption=None, message_id=None):
		# Bot.sendDocument("guid","./file.txt", caption="anything", message_id="12345678")
		uresponse = Bot._uploadFile(self, file)

		file_id = str(uresponse[0]["id"])
		mime = file.split(".")[-1]
		dc_id = uresponse[0]["dc_id"]
		access_hash_rec = uresponse[1]
		file_name = file.split("/")[-1]
		size = str(len(get(file).content if "http" in file else open(file,"rb").read()))

		inData = {
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
			"client": clients.web
		}

		if caption != None: inData["input"]["text"] = caption

		data = {
			"api_version":"5",
			"auth":self.auth,
			"data_enc":self.enc.encrypt(dumps(inData))
		}

		while True:
			try:
				return loads(self.enc.decrypt(loads(post(json=data,url=Bot._getURL()).text)['data_enc']))
				break
			except: continue

	def sendLocation(self, chat_id, location:list, message_id=None):
		# location = [float(x), float(y)]
		return loads(self.enc.decrypt(post(json={
			"api_version":"4",
			"auth":self.auth,
			"client": clients.android,
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
		},url=Bot._getURL()).json()["data_enc"]))

	def searchInChannelMembers(self, text, channel_guid):
		try:
			return loads(self.enc.decrypt(post(json={
				"api_version":"4",
				"auth":self.auth,
				"client": clients.android,
				"data_enc":self.enc.encrypt(dumps({
					"channel_guid": channel_guid,
					"search_text": text
				})),
				"method":"getChannelAllMembers"
			},url=Bot._getURL()).json()["data_enc"]))["in_chat_members"]

		except KeyError: return None

	def getChatsUpdate(self):
		time_stamp = str(round(datetime.datetime.today().timestamp()) - 200)
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getChatsUpdates",
			"input":{
				"state":time_stamp,
			},
			"client": clients.web
		}))},url=Bot._getURL()).json().get("data_enc"))).get("data").get("chats")

	def getChatUpdate(self, chat_id):
		time_stamp = str(round(datetime.datetime.today().timestamp()) - 200)
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getMessagesUpdates",
			"input":{
				"object_guid":chat_id,
				"state":time_stamp
			},
			"client": clients.web
		}))},url=Bot._getURL()).json().get("data_enc"))).get("data").get("updated_messages")

	def myStickerSet(self):
		time_stamp = str(round(datetime.datetime.today().timestamp()) - 200)
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getMyStickerSets",
			"input":{},
			"client": clients.web
		}))},url=Bot._getURL()).json().get("data_enc"))).get("data")

	def uploadAvatar(self,myguid,main,thumbnail=None):
		mainID = str(Bot._uploadFile(self, main)[0]["id"])
		thumbnailID = str(Bot._uploadFile(self, thumbnail or main)[0]["id"])
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"uploadAvatar",
			"input":{
				"object_guid":myguid,
				"thumbnail_file_id":thumbnailID,
				"main_file_id":mainID
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def startVoiceChat(self, chat_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"createGroupVoiceChat",
			"input":{
				"object_guid":chat_id,
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))	

	def editVoiceChat(self, chat_id,voice_chat_id, title):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"setGroupVoiceChatSetting",
			"input":{
				"object_guid":chat_id,
				"voice_chat_id" : voice_chat_id,
				"title" : title ,
				"updated_parameters": ["title"]
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def finishVoiceChat(self, chat_id, voice_chat_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth":self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"discardGroupVoiceChat",
			"input":{
				"object_guid":chat_id,
				"voice_chat_id" : voice_chat_id,
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def getAvatars(self,myguid):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getAvatars",
			"input":{
				"object_guid":myguid,
			},
			"client": clients.web
		}))},url=Bot._getURL()).json().get("data_enc"))).get("data").get("avatars")

	def deleteAvatar(self,myguid,avatar_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"deleteAvatar",
			"input":{
				"object_guid":myguid,
				"avatar_id":avatar_id
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def download(self, dl="message",save=False,**kwargs):
		result = b""
		if dl == "message":
			message = kwargs["message"]
			if type(message) != dict:
				message = Bot(self.app_name, displayWelcome=False).getMessagesInfo(kwargs["chat_id"], [str(message)])[0]
			fileID = str(message["file_inline"]["file_id"])
			size = message["file_inline"]["size"]
			dc_id = str(message["file_inline"]["dc_id"])
			accessHashRec = message["file_inline"]["access_hash_rec"]
			filename = message["file_inline"]["file_name"]
		else :
			fileID = str(kwargs.get("fileID"))
			size = kwargs.get("size")
			dc_id = str(kwargs.get("dc_id"))
			accessHashRec = kwargs.get("accessHashRec")

		header = {
			'auth':self.auth,
			'file-id':fileID,
			'access-hash-rec':accessHashRec
		}
		server = "https://shst"+dc_id+".iranlms.ir/GetFile.ashx"
		if size <= 131072:
			header["start-index"], header["last-index"] = "0",str(size)
			while True:
				try:
					result += get(url=server,headers=header).content
					#j = loads(j)['data']['access_hash_rec']
					break
				except Exception as e:
					print (e)
					continue
		else:
			lastnow = 0
			lastlast = 131072
			while True:
				try:
					if lastnow <= 131072:
						header["start-index"], header["last-index"] = "0", str(size)
						result += get(url=server,headers=header).content
					else:
						for i in range(0,size,131072):
							header["start-index"], header["last-index"] = str(i), str(i+131072 if i+131072 <= size else size)
							result += get(url=server,headers=header).content
					break
				except Exception as e:
					print(e)

		if save:
			with open(kwargs.get("saveAs") or f"{filename}","wb") as file: file.write(result)
		else:
			return result

	def editProfile(self, **kwargs):
		if "username" in list(kwargs.keys()):
			return loads(self.enc.decrypt(post(json={
				"api_version":"4",
				"auth":self.auth,
				"client": clients.android,
				"data_enc":self.enc.encrypt(dumps({
					"username": kwargs.get("username"),
					"updated_parameters":["username"]
				})),
				"method":"updateUsername"
			},url=Bot._getURL()).json()["data_enc"]))
			kwargs = kwargs.pop("username")

		if len(list(kwargs.keys())) > 0:
			return loads(self.enc.decrypt(post(json={
				"api_version":"4",
				"auth":self.auth,
				"client": clients.android,
				"data_enc":self.enc.encrypt(dumps({
					"first_name": kwargs.get("first_name"),
					"last_name": kwargs.get("last_name"),
					"bio": kwargs.get("bio"),
					"updated_parameters":list(kwargs.keys())
				})),
				"method":"updateProfile"
			},url=Bot._getURL()).json()["data_enc"]))

	def sendGIF(self, chat_id, file, width, height, thumbnail="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", caption=None, message_id=None):
		uresponse = Bot._uploadFile(self, file)

		file_id = str(uresponse[0]["id"])
		mime = file.split(".")[-1]
		dc_id = uresponse[0]["dc_id"]
		access_hash_rec = uresponse[1]
		file_name = file.split("/")[-1]
		size = str(len(get(file).content if "http" in file else open(file,"rb").read()))

		return loads(self.enc.decrypt(post(json={
			"api_version":"4",
			"auth":self.auth,
			"client": clients.android,
			"data_enc":self.enc.encrypt(dumps({
				"object_guid": chat_id,
				"is_mute": False,
				"rnd": randint(100000,999999999),
				"file_inline": {
					"access_hash_rec": upload[1],
					"dc_id": dc_id,
					"file_id": file_id,
					"auto_play": False,
					"file_name": file_name,
					"width": width,
					"height": height,
					"mime": mime,
					"size": size,
					"thumb_inline": thumbnail,
					"type": "Gif"
				},
				"text": caption,
				"reply_to_message_id":message_id
			})),
			"method":"sendMessage"
		},url=Bot._getURL()).json()["data_enc"]))

	def sendPoll(self, **kwargs):
		return loads(self.enc.decrypt(post(json={
			"api_version":"4",
			"auth":self.auth,
			"client": clients.android,
			"data_enc":self.enc.encrypt(dumps(kwargs)),
			"method": "createPoll"
		}, url=Bot._getURL()).json()["data_enc"]))

	def votePoll(self, poll_id, option_index):
		return loads(self.enc.decrypt(post(json={
			"api_version":"4",
			"auth":self.auth,
			"client": clients.android,
			"data_enc":self.enc.encrypt(dumps({
				"poll_id": poll_id,
				"selection_index": option_index
			})),
			"method": "createPoll"
		}, url=Bot._getURL()).json()["data_enc"]))

	def deleteChatHistory(self, chat_id, lastMessageId):
		return loads(self.enc.decrypt(post(json={
			"api_version":"4",
			"auth":self.auth,
			"client": clients.android,
			"data_enc":self.enc.encrypt(dumps({
				"object_guid": chat_id,
				"last_message_id": lastMessageId
			})),
			"method": "deleteChatHistory"
		}, url=Bot._getURL()).json()["data_enc"]))

	def search(self, text):
		return loads(self.enc.decrypt(post(json={
			"api_version":"4",
			"auth":self.auth,
			"client": clients.android,
			"data_enc":self.enc.encrypt(dumps({
				"search_text": text
			})),
			"method": "searchGlobalObjects"
		}, url=Bot._getURL()).json()["data_enc"]))

	def getPollStatus(self, poll_id):
		return loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getPollStatus",
			"input":{
				"poll_id":poll_id,
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))

	def getPollOptionVoters(self, poll_id, option_index, start_id=None):
		response = loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
			"method":"getPollOptionVoters",
			"input":{
				"poll_id":poll_id,
				"selection_index": option_index,
				"start_id": start_id
			},
			"client": clients.web
		}))},url=Bot._getURL()).json()["data_enc"]))["data"]

		if not response["has_continue"]: return response["voters_abs_objects"]
		else:
			result = []
			while True:
				if response["has_continue"]:
					res = loads(self.enc.decrypt(post(json={"api_version":"5","auth": self.auth,"data_enc":self.enc.encrypt(dumps({
						"method":"getPollOptionVoters",
						"input":{
							"poll_id":poll_id,
							"selection_index": option_index,
							"start_id": response["next_start_id"]
						},
						"client": clients.web
					}))},url=Bot._getURL()).json()["data_enc"]))
					#print(res)
					result.append([i for i in res["voters_abs_objects"]])
					response = res
				else:
					break
			return result

	def getMe(self):
		return Bot(self.app_name, displayWelcome=False).getUserInfo(loads(open(self.app_name+".json","rt").read()).get("data").get("user").get("user_guid"))

class Socket:
	data = {"error":[],"messages":[]}

	def __init__(self, auth):
		self.auth = auth
		self.enc = rubika.encryption.encryption(auth)

	def on_open(self, ws):
		def handShake(*args):
			ws.send(dumps({
				"api_version": "4",
				"auth": self.auth,
				"data_enc": "",
				"method": "handShake"
			}))

		import _thread
		_thread.start_new_thread(handShake, ())

	def on_error(self, ws, error):
		Socket.data["error"].append(error)

	def on_message(self, ws, message):
		try:
			parsedMessage = loads(message)
			Socket.data["messages"].append({"type": parsedMessage["type"], "data": loads(self.enc.decrypt(parsedMessage["data_enc"]))})
		except KeyError: pass

	def on_close(self, ws, code, msg):
		return {"code": code, "message": msg}

	def handle(self, OnOpen=None, OnError=None, OnMessage=None, OnClose=None, forEver=True):
		import websocket # pip install websocket-client

		ws = websocket.WebSocketApp(
			"wss://shsocket8.iranlms.ir:80",
			on_open=OnOpen or Socket(self.auth).on_open,
			on_message=OnMessage or Socket(self.auth).on_message,
			on_error=OnError or Socket(self.auth).on_error,
			on_close=OnClose or Socket(self.auth).on_close
		)

		if forEver : ws.run_forever()