from os         import path
from threading  import Thread
from datetime   import datetime
from sys        import exc_info
from json       import loads, dumps
from random     import randint, choice
from requests   import get as GET, exceptions

from rubika.fileIO     import *
from rubika.filters    import *
from rubika.tools      import Tools
from rubika.encryption import encryption
from rubika.configs    import makeData, makeTmpData, defaultDevice, _getURL, welcome, __version__, __license__, __copyright__

welcome(f"rubika library version {__version__}\n{__copyright__}\n→ docs : https://rubikalib.github.io\n")

class Bot:
	downloadURL, DCsURL, getDCsURL, wsURL = "https://messengerX.iranlms.ir/GetFile.ashx", "https://messengerg2cX.iranlms.ir/", "https://getdcmess.iranlms.ir", "wss://msocket1.iranlms.ir:80"

	def __init__(self, appName:str, auth:str=None, phoneNumber:str=None, wantRegister:bool=True, device:dict=defaultDevice, appType="rubika"):
		self.appName, self.appType = appName, appType.lower()
		if self.appType.lower() == "shad": Bot.setAsShad(self)

		if auth is not None and len(auth) == 32 : self.auth = auth
		else :
			fileExist   = path.exists(f"{self.appName}.json")
			phoneNumber = phoneNumber if not fileExist and phoneNumber is not None and len(phoneNumber) == 11 else input("please enter your phone number (e.g. 09123456789) : ")
			account     = loads(open(f"{self.appName}.json").read()) if fileExist else Bot.signIn(phoneNumber, Bot.sendCode(phoneNumber)["data"]["phone_code_hash"], input("please enter activation code : "))
			self.auth   = account["data"]["auth"]
			if not fileExist and wantRegister :
				Bot.registerDevice(self.auth, device=device)
				open(f"{self.appName}.json", "w").write(dumps(account, indent=4, ensure_ascii=True))

		self.enc  = encryption(self.auth)

	_getURL    = lambda dc_id=None: _getURL(Bot.DCsURL, Bot.getDCsURL, dc_id)
	addContact = lambda self, first_name, last_name, phone: Bot._create(4, self.auth, "addAddressBook", {"first_name": first_name, "last_name": last_name, "phone": phone})
	addGroup   = lambda self, title, users_chat_id: Bot._create(5, self.auth, "addGroup", {"title": title, "member_guids": users_chat_id})
	addChannel = lambda self, title, channelType="Public", users_chat_id=None: Bot._create(5, self.auth, "addChannel", {"channel_type": channelType, "title": title, "member_guids": users_chat_id or []})
	addFolder  = lambda self, name, exclude_chat_types=[], exclude_object_guids=[], include_chat_types=[], include_object_guids=[], is_add_to_top=True, folder_id="": Bot._create(5, self.auth, "addFolder", dict(exclude_object_guids=exclude_object_guids, include_object_guids=include_object_guids, exclude_chat_types=exclude_chat_types, include_chat_types=include_chat_types, folder_id=folder_id, is_add_to_top=is_add_to_top, name=name), clients.android)

	banMember  = lambda self, chat_id, member_id: Bot._create(5, self.auth, f"ban{Bot._chatDetection(chat_id)}Member", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "member_guid": member_id, "action":"Set"})
	block      = lambda self, chat_id: Bot._create(5, self.auth, "setBlockUser", {"action": "Block","user_guid": chat_id})

	_create        = lambda api_version, auth, method, data, client=None: makeData(int(api_version), auth, method, dict(data), client or clients.web if api_version == 5 else clients.android, url=Bot._getURL(dc_id=64))
	_createTMP     = lambda method, data: makeTmpData(method, dict(data), url=Bot._getURL(dc_id=64))
	_chatDetection = lambda chat_id: "Group" if chat_id.startswith("g") else "Channel" if chat_id.startswith("c") else "User" if chat_id.startswith("u") else "Bot" if chat_id.startswith("b") else "Service"
	changeLink     = lambda self, chat_id: Bot._create(4, self.auth, f"set{Bot._chatDetection(chat_id)}Link", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id})
	changePassword = lambda self, hint, newPass, oldPass: Bot._create(4, self.auth, "changePassword", {"new_hint": hint, "new_password": newPass, "password": oldPass})
	checkPassword  = lambda self, password: Bot._create(4, self.auth, "checkTwoStepPasscode", {"password": password}).get("data").get("is_vaild")

	deleteMessages    = lambda self, chat_id, message_ids: Bot._create(5, self.auth, "deleteMessages", {"object_guid":chat_id,"message_ids":list(message_ids),"type":"Global"})
	deleteAdmin       = lambda self, chat_id, member_id: Bot._create(5, self.auth, f"set{Bot._chatDetection(chat_id)}Admin", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "action": "UnsetAdmin", "member_guid": member_id})
	deleteAvatar      = lambda self, chat_id, avatar_id: Bot._create(5, self.auth, "deleteAvatar", {"object_guid": chat_id,"avatar_id": avatar_id})
	deleteChatHistory = lambda self, chat_id, lastMessageId: Bot._create(4, self.auth, "deleteChatHistory", {"object_guid": chat_id,"last_message_id": lastMessageId})
	deleteFolder      = lambda self, folder_id: Bot._create(5, self.auth, "deleteFolder", dict(folder_id=folder_id), clients.android)
	deleteUserChat    = lambda self, chat_id, lastMessageID: Bot._create(5, self.auth, "deleteUserChat", {"last_deleted_message_id": lastMessageID, "user_guid": chat_id})
	download          = lambda self, chat_id, message_id, save=True, saveAs=None, logging=True: download(self, chat_id, message_id, save, saveAs, logging)
	disablePassword   = lambda self, password: Bot._create(4, self.auth, "turnOffTwoStep", {"password": password})

	def editMessage(self, message_id, chat_id:str, newText:str, metadata:list=None, parse_mode:str=None) -> dict:
		metadata, newText = Bot.loadMetadata(metadata, parse_mode, newText)
		return Bot._create(5, self.auth, "editMessage", {"message_id": message_id, "object_guid": chat_id, "text": newText, "metadata": metadata})
	def editFolder(self, **kwargs):
		'''
		exclude_chat_types: (list) types that should never apply
		include_chat_types: (list) types that should always apply
		exclude_object_guids: (list) items that should never apply
		include_object_guids: (list) items that should always apply
		folder_id: (str) id of the target folder
		name: (str) name of the target folder
		'''
		kwargs["update_parameters"] = [i for i in kwargs.keys() if "clude" in i]
		return Bot._create(5, self.auth, "editFolder", kwargs, clients.android)
	editVoiceChat = lambda self, chat_id, voice_chat_id, title: Bot._create(5, self.auth, f"set{Bot._chatDetection(chat_id)}VoiceChatSetting", {f"{Bot._chatDetection(chat_id).lower()}_guid":chat_id, "voice_chat_id" : voice_chat_id, "title" : title, "updated_parameters": ["title"]})
	def editChatInfo(self, chat_id, **kwargs):
		chat = Bot._chatDetection(chat_id)
		data, result = {f"{chat.lower()}_guid": chat_id}, []
		if "username" in list(kwargs.keys()):
			result.append(Bot._create(4, self.auth, "updateChannelUsername", {"channel_guid": chat_id, "username": kwargs.get("username").replace("@", ""), "updated_parameters":["username"]}))
			kwargs.pop("username")
		if kwargs != {} and not 'username' in kwargs.keys():
			for k,v in kwargs.items(): data[k] = v
			result.append(Bot._create(5, self.auth, f"edit{chat}Info", dict(channel_guid=chat_id, **kwargs, updated_parameters=list(kwargs.keys()))))
		return result
	def editProfile(self, **kwargs) -> list :
		result:list = []
		if "username" in list(kwargs.keys()):
			result.append(Bot._create(4, self.auth, "updateUsername", {"username": kwargs.get("username"), "updated_parameters":["username"]}))
			kwargs.pop("username")
		if kwargs != {} and not 'username' in kwargs.keys(): result.append(Bot._create(4, self.auth, "updateProfile", {"first_name": kwargs.get("first_name"),"last_name": kwargs.get("last_name"),"bio": kwargs.get("bio"),"updated_parameters":list(kwargs.keys())}))
		return result

	forwardMessages = lambda self, From, message_ids, to: Bot._create(5, self.auth, "forwardMessages", {"from_object_guid": From,"message_ids": message_ids,"rnd": f"{randint(100000,999999999)}","to_object_guid": to})
	finishVoiceChat = lambda self, chat_id, voice_chat_id: Bot._create(5, self.auth, f"discard{Bot._chatDetection(chat_id)}VoiceChat", {f"{Bot._chatDetection(chat_id).lower()}_guid":chat_id, "voice_chat_id" : voice_chat_id})

	getMe                      = lambda self, myGuid=None: Bot.getInfo(self, myGuid or loads(open(self.appName+".json","rt").read()).get("data").get("user").get("user_guid"))
	getChats                   = lambda self, start_id=None: Bot._create(5, self.auth, "getChats", {"start_id": start_id})
	getMessages                = lambda self, chat_id, min_id, start_id=None: Bot._create(5, self.auth, "getMessagesInterval", {"object_guid": chat_id,"middle_message_id": min_id,"start_id": start_id}).get("data").get("messages")
	getLastMessage             = lambda self, chat_id:                Bot.getMessages(self, chat_id, Bot.getInfo(self, chat_id)["chat"]["last_message"]["message_id"])[-1] # it isn't a server method , is a shortcut
	getInfoByUsername          = lambda self, username:               Bot._create(5, self.auth, "getObjectByUsername", {"username": username.replace("@","")})
	getBlacklist               = lambda self, chat_id, start_id=None: Bot._create(5, self.auth, f"getBanned{Bot._chatDetection(chat_id)}Members", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "start_id":start_id}).get("data")
	getMyBlacklist             = lambda self, start_id=None:          Bot._create(4, self.auth, "getBlockedUsers", {"start_id": start_id})
	getAdmins                  = lambda self, chat_id, start_id=None: Bot._create(5, self.auth, f"get{Bot._chatDetection(chat_id)}AdminMembers", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "start_id":start_id})
	getMessagesInfo            = lambda self, chat_id, message_ids:   Bot._create(5, self.auth, "getMessagesByID", {"object_guid": chat_id,"message_ids": list(message_ids)}).get("data").get("messages")
	getMembers                 = lambda self, chat_id, search_text=None, start_id=None: Bot._create(5, self.auth, f"get{Bot._chatDetection(chat_id)}AllMembers", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "search_text": search_text, "start_id": start_id})
	getInfo                    = lambda self, chat_id: Bot._create(5, self.auth, f"get{Bot._chatDetection(chat_id)}Info", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id}).get("data")
	getLink                    = lambda self, chat_id: Bot._create(5, self.auth, f"get{Bot._chatDetection(chat_id)}Link", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id}).get("data").get("join_link")
	getPreviewByJoinLink       = lambda self, link:    Bot._create(5, self.auth, f"{'group' if 'joing' in link else 'channel'}PreviewByJoinLink", {"hash_link": link.split("/")[-1]})
	getChatsUpdate             = lambda self:          Bot._create(5, self.auth, "getChatsUpdate", {"state":str(round(datetime.today().timestamp()) - 200)}).get("data")
	getChatUpdate              = lambda self, chat_id: Bot._create(5, self.auth, "getMessagesUpdates", {"object_guid":chat_id,"state":str(round(datetime.today().timestamp()) - 200)})
	getMyStickerSet            = lambda self:          Bot._create(5, self.auth, "getMyStickerSets", {})
	getAvatars                 = lambda self, chat_id: Bot._create(5, self.auth, "getAvatars", {"object_guid": chat_id})
	getPollStatus              = lambda self, poll_id: Bot._create(5, self.auth, "getPollStatus", {"poll_id":str(poll_id)})
	getPollOptionVoters        = lambda self, poll_id, option_index, start_id=None: Bot._create(5, self.auth, "getPollOptionVoters", {"poll_id":poll_id,"selection_index": option_index,"start_id": start_id})
	getPostByLink              = lambda self, link:    Bot._create(5, self.auth, "getLinkFromAppUrl", {"app_link": link})["data"]["chat"]["open_chat_data"]
	getUserCommonGroups        = lambda self, chat_id: Bot._create(4, self.auth, "getCommonGroups", {"user_guid": chat_id})
	getGroupOnlineMembersCount = lambda self, chat_id: Bot._create(4, self.auth, "getGroupOnlineCount", {"group_guid": chat_id}).get("online_count")
	getTwoPasscodeStatus       = lambda self:          Bot._create(4, self.auth, "getTwoPasscodeStatus", {})
	getPrivacySetting          = lambda self:          Bot._create(4, self.auth, "getPrivacySetting", {})
	getNotificationSetting     = lambda self:          Bot._create(4, self.auth, "getNotificationSetting", {}).get("notification_setting")
	getSuggestedFolders        = lambda self:          Bot._create(4, self.auth, "getSuggestedFolders", {}, clients.android)
	getFolders                 = lambda self:          Bot._create(4, self.auth, "getFolders", {}, clients.android).get("folders")
	getOwning                  = lambda self, chat_id: Bot._create(4, self.auth, "getPendingObjectOwner", {"object_guid": chat_id})
	getMySessions              = lambda self:          Bot._create(5, self.auth, "getMySessions", {})
	getContacts                = lambda self:          Bot._create(5, self.auth, "getContacts", {})

	invite = lambda self, chat_id, user_ids: Bot._create(5, self.auth, f"add{Bot._chatDetection(chat_id)}Members", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "member_guids": user_ids})

	join   = lambda self, value: Bot._create(5, self.auth, "joinChannelAction", {"action": "Join","channel_guid": value}) if value.startswith("c") else Bot._create(5, self.auth, "joinGroup", {"hash_link": value.split("/")[-1]})

	logout = lambda self: Bot._create(5, self.auth, "logout", {})
	leave  = lambda self, chat_id: Bot._create(5, self.auth, "joinChannelAction", {"action": "Leave","channel_guid": chat_id}) if chat_id.startswith("c") else Bot._create(5, self.auth, "leaveGroup", {"group_guid": chat_id})
	@staticmethod
	def loadMetadata(metadata, parse_mode, text) -> tuple:
		if metadata is not None : metadata = {"meta_data_parts":metadata}
		if parse_mode is not None :
			parsedResult = Tools.parse(parse_mode, text)
			metadata, text = {"meta_data_parts": parsedResult["metadata"]}, parsedResult["realText"]
		return metadata if metadata != {"meta_data_parts": []} else None, text

	muteChat = lambda self, chat_id: Bot._create(5, self.auth, "setActionChat", {"action": "Mute", "object_guid": chat_id})

	pin = lambda self, chat_id, message_id: Bot._create(4, self.auth, "setPinMessage", {"action":"Pin","message_id": message_id,"object_guid": chat_id})

	registerDevice  = lambda auth, device=defaultDevice: Bot._create(5, auth, "registerDevice", device)
	reportChat      = lambda self, chat_id, reportType=106, description=None: Bot._create(4, self.auth, "reportObject", {"object_guid": chat_id, "report_description": description, "report_type": reportType, "report_type_object": "Object"})
	removeChat      = lambda self, chat_id: Bot._create(4, self.auth, f"remove{Bot._chatDetection(chat_id)}", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id})
	requestSendFile = lambda self, file, size=None: requestSendFile(self, file, int(size))

	sendCode = lambda phoneNumber: Bot._createTMP("sendCode", {"phone_number":f"98{phoneNumber[1:]}", "send_type":"SMS"})
	signIn   = lambda phoneNumber, phone_code_hash, phone_code: Bot._createTMP("signIn", { "phone_number": f"98{phoneNumber[1:]}", "phone_code_hash": phone_code_hash, "phone_code": phone_code })

	def setAsShad(self): clients.web["app_version"], clients.web["package"], clients.android["package"], Bot.wsURL, Bot.DCsURL, Bot.getDCsURL, Bot.downloadURL = "3.2.2", "web.shad.ir", "ir.medu.shad", "wss://shsocket1.iranlms.ir:80", "https://shadmessengerX.iranlms.ir/", "https://shgetdcmess.iranlms.ir", "https://shstX.iranlms.ir/GetFile.ashx"

	def sendMessage(self, chat_id:str, text:str, metadata:list=None, parse_mode:str=None, message_id=None) -> dict:
		metadata, text = Bot.loadMetadata(metadata, parse_mode, text)
		return Bot._create(5, self.auth, "sendMessage", {"object_guid":chat_id,"rnd":f"{randint(100000,999999999)}","text":text, "metadata":metadata,"reply_to_message_id":message_id})

	def sendPhoto(self, chat_id:str, file:str, size:list=None, thumbnail:str="iVBORw0KGgoAAAANSUhEUgAAABwAAAAoCAYAAADt5povAAAAAXNSR0IArs4c6QAACmpJREFUWEfNVwl0U1Ua/u57ycuetGmatOneJt0prWUpYEVBkB0dQFkcGQRRYZwB5AyLy3gAHSgqjqgjokg944oiCiguI6ioFbpQSimFlkK3hO5p0uzv3TkJTaciwsyZOZ6557yTd/Lu/b97/+X7v0vwKw/yK+Ph/xowsLnBT8g5AgDa/1zXYdc7YQggYChg+FqD6f94TfBrAYYMBICY+CHQxMch1WBAMsSItHhBHS60e7pQZ7Wi3laF7n7A0CavusGrAQ4syJloUAzPtRVk3uBdlGgWbtGoEe0lhJzpJWjsoyCEAjz87l5YeprwVWMpir/bha/73Ruw87PTXgkYBJsDkNwnkrKSRrhWac3dcyjvlfs9QKcLtLaH+m0eCCwDuCEibqJkfIxcRMUS8IKiu6sj+kBtif6llu1vlvTHPHDwAHBwDAYMgi3NV2nnptH5eaOFVfXDnAnnJRA4P/ztHrC1Lpa1IBItJBdNfBY6fFFw+pXUB4kfrIRCJmWIXiViFeJmtqL6ec+KzS+gudk9KLYDgAEw5pmbYBytx+qCFDzUlQpUZoLvlhLSzrPsjw69UNmR333OktFgd6ic4MQM4rUGkmyMITqNXBCDgvoovELgIYRle0lL29+FxY89gro6ewh0IM2fGA79bUl4aGQM1nnDCG3PA62Mp0yrn3F9eVx2/JtDxmJrGVOGTns3XK1NQQMmk0QplSZHJedOjkkZ+luanjj0fIqUt8RJBF7GssRPeklj2+vCsg3rcPq0P+Da4MkmGiArmoA7h4TjBV4EqS+V0LpsypSKcGHvO3j64B7sRiucMA6PA8+bcan8cH84BpIiT55nNEVmLkuIzf69PS1MWTFS7aseGcH0acVWlFRuxZ2rXgxgBU94bgFGqiXkpQglzaVK8H15YEq1qC4qxprP38Cn/e7gxIaZeUSpm8aLXRX8mbc+vKIMqE6nU+Sop842q5KKYjmZtsso9laO1QvnM1QnOoqeW+o4fLiaLDUadQvT2QdGJbg28MoOgYknxJJAzz7yBf5cvBPvA2BVKqPmxtvmLJw6Y/baEQXDdA2W5q4P93/27jsvPLkFbsvFwQyk1ZoUqZHjFiRpkp5JZgin8VO4ROhpE2yvvnhs83pSkTp2eHi4d3tswqVhQlyD4IqB/bSP7hy1BusDYMCI2El3zluz5L7bl44x29HTx/McQ5kezkg3f9773Z6181bCVlYxKONJetTNcRpV6toEbfrSBJGHalgR8fL+kv11ex8jlVk33ZOp4XbQyIsSJuMctUWTktm76NLDlagJAkrGxWeNmvRo/vS5C10RBqGqRcTGaCk1GQThZEPniR82zVuB7iPfBeKDAA1c/iUPZC8pdDOq112S6ASzROBZUGuTrelrcjRrzLYCteqPft1FwZd6pu+CnO4eshErBiWFFJEb5yK2cCfyC1koCIVHALzdvbCU7Man01f3F3aIxIOJuDHOlKhUmB7tVd6wsIYJEzIlgt8nCN3k1NDC/ely1WSfxiL0mqob32r1blq5F8X9O73Mh0pDJGdYeD8S71jPJ+VwqkgOUVxrl6V0317X969t93afPHUFkZD88HDV03FJi/TylKLt3gwfOIU8SQxKmnPHVhgkihyfsktwxNdU/anKtmp3aZAPA64JABKoJpmhLXwcKXPuQnoyYRQMI2MFKvG4qNR50WLmviwu3/3YNrvd3jnIM6LKQtPMeFHEayfs6eLXiYkoRTIpaRg2/lQ8y2X4xU449BeOLa66+OC+c6gctBDQry5gwsw75Lnjs0VmHbU51Yxe6qOpkk7UtzBEkUQ702yHdh7YsuiRQTRGTszUTojyad+Qd6VqD/sNfftpHMi6YQ+Xz+DsWfm0Hr2KnoolDWXL99WjfBAgo4yank5U+U+p0sdNl2cbhDq3mZWIKI2gF7uEH49YOyNuyVAMlZV6d81Y7mw6VtbvHXryXtwW7da/EdGYrfP7ON4J4iVTctaW5Ck1+TNR600Qztc9bq1Zs+NC++f9gMFemHdv8USX2/Dq+eaoaK85FdBKAIEKcF+qx6F1r4IkhkNfMB3tHz2LczsC8ScmE0TvTcRvMhnNLrY6Uyo4tJRhfYSMz/zDnhhl/B154j6+kD9rrb1UtnVBw5kgDV2OYaxUfNebc8AlvULrLRI+KoYiKRoEVAB/qZ4c2bqBP/Hch4BUD4gdQDCOzM35CH90BO67RaN40ldqBrHFgLC8QG5MW7bJoEpar2N5ZIqdzhTX6bemlb2/HECAbAODw5SjsyDSF6OpUUQ0OtCMbAqOoXBaK3Bw/gq0Hvl+kAQJlsXfFiNjiI48NUrMTfWVJQukPdntoW4LmZCx8g6pJOI1jmXCYiUiIZJ4Th6q/2DVUeuJf2Vq5O+GgjrmQVD1MQmz7gu/cWyMMVFCu9s6jze/PHU5bOUBpgkVPjEB4veKMM2kILvkDSKlUJdAXc2mC9/2WvaRkUn35Khk+i1qqWEiQ7xCDMd6xbxjz9PHNj2IQFO/PIIdWz/77dF5QxJemTIpP7Ozo8/n77tUVrRy8cP+lu8Hd3dmw0pkjDBiywQNmcSfYASmw0hcDRlfza8pXUF0ujRVRtTku7WymO2Mxw0pyyKMo229zvrn36zatTlEVQFQpSFFN+butUuih83Y0OnVMFG89dDOe4cuAGw9l3kXdNw0RM25FStnpWGVthwCbSFwuxXWqpMxfx1dWrs16G/lxNWZjDziL1qJYWpsaztvcPBMGPW3tjtqtn1c9/bz/RwZMIi8yfenRg4t2GDIGjbSWvLZzi9eXF0EwBeYkzMZsZOmYcX04ViRexZEfgrgbRA8DP4x5QAWfXsR1lDHF2HBtluhitghgig2vMfOx3a5GaPd2+vurP+o+sKXW63euuqQENJqtWqn0xnudrsDrQlIhDRvlGhkwXh+zbjhdHJaB2h6FSjOg/b5Sc07FXTdgz/g4EADDi6KzFSg8O67SFTKsxSCCpTnxX6B0booI+3tbrNfOn3A1l75Cd/edArE0Q51HKDWxMuzo28wj+iYPmbI6fGjozqVei+laY2UxlYCrjbSVN5Ki276GC+H6jqk2i6fNDlfhSFT55LotE2UMhHw+QRwIkApY6FWAWEyIFzkh4Z1ctJeJoY7Jc9gDzJZOIosro+Gi8Gr+0Dya8DSalw4VoeiCQcHwIJy5GcyEYmJnCR91ljGnPk4MUeOhpEIjBw+MeeiMrGdUaOFNfhPs0a+FGH+ehrJUr9JDaoWExZiyho9jDfuW/bH99+lTz50zB9irAHtczUhHCyDnAdG62OyHfOj09uXySQ2M/F6QLw8GH+QfihlgGgFIWlhBCqZAMoQoc8uOl9bzu34oIjZXXb2J53jqkI4lBM/Ech5MxAdZsbthgxMURtIDisjBk5MuCQZhUlOPX0OamltRGXtSXxa9g0+Of4NAhLyF+8X17rMXLmIRGZCIZXBwBCoFYFa8MDWY0VbezscVyq4X7q+Xe+6FrAT1CiDZMRgT4TeQ3NCMuNqc4L//TuAV7p6cGaHkmEgRr+IdIUGud68/9n3//SE/zXwrw74T3XSTDJjBhdXAAAAAElFTkSuQmCC", metadata:list=None, parse_mode:str=None, caption:str=None, message_id=None, uresponse:list=None) -> dict :
		# size = [width:int, height:int]
		uresponse = uresponse or Bot.uploadFile(self, file)
		if "."  in thumbnail: thumbnail = str(Tools.getThumbInline(open(file,"rb").read() if not "http" in file else GET(file).content))
		if size is None: size = Tools.getImageSize(open(file,"rb").read() if not "http" in file else GET(file).content)
		metadata, caption = Bot.loadMetadata(metadata, parse_mode, caption)
		return Bot._create(5, self.auth, "sendMessage", {"file_inline": {"dc_id": uresponse[0]["dc_id"],"file_id": uresponse[0]["id"],"type":"Image","file_name": file.split("/")[-1],"size": str(len(GET(file).content if "http" in file else open(file,"rb").read())),"mime": file.split(".")[-1],"access_hash_rec": uresponse[1],"width": size[0],"height": size[1],"thumb_inline": thumbnail},"object_guid": chat_id, "text": caption, "metadata": metadata,"rnd": f"{randint(100000,999999999)}","reply_to_message_id": message_id})

	def sendVideo(self, chat_id:str, file:str, width:int=720, height:int=720, metadata:list=None, parse_mode:str=None, caption=None, message_id=None, uresponse:list=None):
		from tinytag import TinyTag # pip install tinytag
		uresponse, metadata, caption = uresponse or Bot.uploadFile(self, file), *Bot.loadMetadata(metadata, parse_mode, caption)
		return Bot._create(4, self.auth, "sendMessage", {"file_inline":{"access_hash_rec":uresponse[1],"auto_play":False,"dc_id":uresponse[0]["dc_id"],"file_id":str(uresponse[0]["id"]),"file_name":file.split("/")[-1],"height":height,"mime":file.split(".")[-1],"size":str(len(GET(file).content if "http" in file else open(file,"rb").read())),"thumb_inline":file,"time":round(TinyTag.get(file).duration * 1000),"type":"Video","width":width},"is_mute":False,"object_guid":chat_id, "text": caption, "metadata": metadata, "rnd":str(randint(100000,999999999)), "reply_to_message_id":message_id})

	def sendMusic(self, chat_id:str, file:str, metadata:list=None, parse_mode:str=None, caption=None, message_id=None, uresponse:list=None):
		from tinytag import TinyTag # pip install tinytag
		uresponse, metadata, caption = uresponse or Bot.uploadFile(self, file), *Bot.loadMetadata(metadata, parse_mode, caption)
		return Bot._create(4, self.auth, "sendMessage", {"file_inline":{"access_hash_rec":uresponse[1], "auto_play":False, "dc_id":uresponse[0]["dc_id"], "file_id":str(uresponse[0]["id"]),"file_name":file.split("/")[-1],"height":0.0,"mime":file.split(".")[-1],"music_performer": str(TinyTag.get(file).artist),"size": len(GET(file).content if "http" in file else open(file,"rb").read()),"time": round(TinyTag.get(file).duration),"type":"Music","width":0.0},"is_mute":False,"object_guid":chat_id, "text": caption, "metadata": metadata,"rnd":randint(100000,999999999),"reply_to_message_id":message_id})

	def sendVoice(self, chat_id:str, file:str, time:int=None, metadata:list=None, parse_mode:str=None, caption:str=None, message_id=None, uresponse:list=None) -> dict :
		# file's format must be ogg. time must be ms (type: float).
		uresponse, metadata, caption = uresponse or Bot.uploadFile(self, file), *Bot.loadMetadata(metadata, parse_mode, caption)
		if time is None:
			from tinytag import TinyTag # pip install tinytag
			time = round(TinyTag.get(file).duration)
		return Bot._create(5, self.auth, "sendMessage", {"file_inline": {"dc_id": str(uresponse[0]["dc_id"]),"file_id": uresponse[0]["id"],"type":"Voice","file_name": file.split("/")[-1],"size": len(GET(file).content if "http" in file else open(file,"rb").read()),"time": float(time),"mime": file.split(".")[-1],"access_hash_rec": str(uresponse[1])},"object_guid":chat_id, "text": caption, "metadata": metadata, "rnd":f"{randint(100000,999999999)}","reply_to_message_id":message_id})

	def sendDocument(self, chat_id:str, file:str, caption:str=None, metadata:list=None, parse_mode:str = None, message_id=None, uresponse:list=None) -> dict :
		# Bot.sendDocument("guid","./file.txt", caption="anything", message_id="12345678")
		uresponse, metadata, caption = uresponse or Bot.uploadFile(self, file), *Bot.loadMetadata(metadata, parse_mode, caption)
		return Bot._create(5, self.auth, "sendMessage", {"object_guid":chat_id, "metadata": metadata, "text": caption, "reply_to_message_id":message_id,"rnd":f"{randint(100000,999999999)}","file_inline":{"dc_id":str(uresponse[0]["dc_id"]),"file_id":str(uresponse[0]["id"]),"type":"File","file_name":file.split("/")[-1],"size":len(GET(file).content if "http" in file else open(file,"rb").read()),"mime":file.split(".")[-1],"access_hash_rec":uresponse[1]}})

	sendLocation = lambda self, chat_id, location, message_id: Bot._create(4, self.auth, "sendMessage", {"is_mute": False,"object_guid":chat_id,"rnd":f"{randint(100000,999999999)}","location":{"latitude": location[0],"longitude": location[1]},"reply_to_message_id":message_id})

	def sendGIF(self, chat_id:str, file:str, width:int, height:int, time:int=None, metadata:list=None, parse_mode:str=None, thumbnail:str=r"/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDACAWGBwYFCAcGhwkIiAmMFA0MCwsMGJGSjpQdGZ6eHJm\ncG6AkLicgIiuim5woNqirr7EztDOfJri8uDI8LjKzsb/2wBDASIkJDAqMF40NF7GhHCExsbGxsbG\nxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsb/wAARCAAyADIDASIA\nAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQA\nAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3\nODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWm\np6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEA\nAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSEx\nBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElK\nU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3\nuLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDXqCXo\nasVXk70DKwHNSBaRRzUgrnZqMUfMKtkcCq24KcmntdxgDmtIEyJ8UVB9ti9aKskmB4qJ/uk1L2qC\nZtsZpiII5P3hB6VDLOySZ7UyVJDEWWoXLGD5uoqFHQtvUnln3rkVB5bv3qqk3Y1filUKM09kCV2R\nfZ39aKtectFK7K5URwagzrila4klcJiqdtbsrA5q+jLE4ZhVXsyErq5bCFYAMVQuVYKVC9av/akc\ncGmy4ZeKaIaZgeWVlANX1jDKKbdRYYNQJQqdamRpAk8pfWiq/n+9FSWPtifM61LcdKKKctyIbEMJ\nO4c1oj7lFFUiWQXH+qNZLmiihjiNzRRRUlH/2Q==\n", caption:str=None, message_id:int=None, uresponse:list=None) -> dict :
		uresponse, metadata, caption = uresponse or Bot.uploadFile(self, file), *Bot.loadMetadata(metadata, parse_mode, caption)
		if time is None :
			from tinytag import TinyTag # pip install TinyTag
			time = round(TinyTag.get(file).duration * 1000)
		return Bot._create(4, self.auth, "sendMessage", {"object_guid": chat_id,"is_mute": False,"rnd": randint(100000,999999999),"file_inline": {"access_hash_rec": str(uresponse[1]),"dc_id": str(uresponse[0]["dc_id"]),"file_id": int(uresponse[0]["id"]),"auto_play": False,"file_name": file.split("/")[-1],"width": width,"height": height,"mime": file.split(".")[-1],"size": len(GET(file).content if "http" in file else open(file,"rb").read()),"thumb_inline": thumbnail, "time": time, "type": "Gif"},"text": caption, "metadata": metadata, "reply_to_message_id": message_id})

	def sendContact(self, chat_id:str, user_guid:str, phone:str, firstName:str, lastName:str=None, avatarFile:str=None, uresponse:list=None) -> dict:
		'''
		chat_id: destination guid for sending the contact
		user_guid: contact's guid
		phone: contact's phone number
		first_name: contact's first name
		'''
		uresponse = Bot.uploadFile(self, avatarFile) if avatarFile is not None else uresponse or [{"dc_id": "702", "id": 2521972095}, "5653363141731050515439840306092021010915"]
		avatar = {"access_hash_rec": str(uresponse[1]), "file_id": int(uresponse[0]["id"]),"auto_play": False,"dc_id": str(uresponse[0]["dc_id"]),"height": 0,"mime": "none","size": 10025 if uresponse[0]["id"] == 2521972095 else len(GET(avatarFile).content if "http" in avatarFile else open(avatarFile,"rb").read()),"time": 5,"type": "File","width": 0}
		return Bot._create(4, self.auth, "sendMessage", {"is_mute": False, "message_contact": {"contactAbsObject": {"avatar_thumbnail": avatar,"first_name": firstName,"last_name": lastName or "","is_deleted": False,"is_verified": False,"object_guid": user_guid,"type": "User"},"first_name": firstName,"last_name": lastName or "","phone_number": "+98"+phone[1:],"user_guid": user_guid,"vcard": f"BEGIN:VCARD\nVERSION:3.0\nFN:{firstName}\nTEL;MOBILE:+98{phone[1:]}\nEND:VCARD"}, "object_guid": chat_id, "rnd": randint(100000, 999999999)})

	setMembersAccess    = lambda self, chat_id, access_list: Bot._create(4, self.auth, "setGroupDefaultAccess", {"access_list": access_list, "group_guid": chat_id})
	setGroupTimer       = lambda self, chat_id, time: Bot._create(5, self.auth, "editGroupInfo", {"group_guid": chat_id,"slow_mode": time,"updated_parameters":["slow_mode"]})
	setAdmin            = lambda self, chat_id, member_id, access_list=None: Bot._create(5, self.auth, f"set{Bot._chatDetection(chat_id)}Admin", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "access_list": access_list or [], "action": "SetAdmin", "member_guid": member_id})
	seenChats           = lambda self, seenList: Bot._create(5, self.auth, "seenChats", {"seen_list": dict(seenList)})
	sendChatAction      = lambda self, chat_id, action: Bot._create(5, self.auth, "sendChatActivity", {"activity": action,"object_guid": chat_id}) #every some seconds before sending message this request should send. action can be : Typing, Recording, Uploading
	sendPoll            = lambda self, chat_id, allows_multiple_answers, is_anonymous, options, question, Type="Regular", message_id=None: Bot._create(4, self.auth, "createPoll", {"allows_multiple_answers": bool(allows_multiple_answers), "is_anonymous": bool(is_anonymous), "object_guid": chat_id, "options": list(options), "question": question, "rnd": str(randint(100000, 999999999)), "type": Type, "reply_to_message_id": message_id})
	sendQuiz            = lambda self, chat_id, correct_option_index, is_anonymous, options, question, Type="Quiz", message_id=None: Bot._create(4, self.auth, "createPoll", {"correct_option_index": int(correct_option_index), "is_anonymous": bool(is_anonymous), "object_guid": chat_id, "options": list(options), "question": question, "rnd": str(randint(100000, 999999999)), "type": Type, "reply_to_message_id": message_id})
	searchGlobalObjects = lambda self, text, start_id=None: Bot._create(4, self.auth, "searchGlobalObjects", {"search_text":text, "start_id": start_id})
	setPhoneVisibility  = lambda self, mode="Nobody": Bot._create(4, self.auth, "setSetting", {"settings": {"show_my_phone_number": mode}, "update_parameters": ["show_my_phone_number"]}) #mode = Nobody/Everybody/MyContacts
	setOnlineVisibility = lambda self, mode="Everybody": Bot._create(4, self.auth, "setSetting", {"settings": {"show_my_last_online": mode}, "update_parameters": ["show_my_last_online"]}) #mode = Nobody/Everybody/MyContacts
	setAvatarVisibility = lambda self, mode="Everybody": Bot._create(4, self.auth, "setSetting", {"settings": {"show_my_profile_photo": mode}, "update_parameters": ["show_my_profile_photo"]}) #mode = Everybody/MyContacts
	setCallableBy       = lambda self, mode="MyContacts": Bot._create(4, self.auth, "setSetting", {"settings": {"can_called_by": mode}, "update_parameters": ["can_called_by"]}) #mode = Everybody/MyContacts
	setForwardableBy    = lambda self, mode="Everybody": Bot._create(4, self.auth, "setSetting", {"settings": {"link_forward_message": mode}, "update_parameters": ["link_forward_message"]}) #mode = Nobody/Everybody/MyContacts
	setJoinableBy       = lambda self, mode="MyContacts": Bot._create(4, self.auth, "setSetting", {"settings": {"can_join_chat_by": mode}, "update_parameters": ["can_join_chat_by"]}) #mode = Everybody/MyContacts
	setMyAutoDeleteTime = lambda self, time=24: Bot._create(4, self.auth, "setSetting", {"settings": {"delete_account_not_active_months": str(time)}, "update_parameters": ["show_my_phone_number"]}) #time = 3/6/12/24 , type: str/int, duration: months
	setNotifications    = lambda self, user_message_preview=True, group_message_preview=False, channel_message_preview=False, in_app_sound=True, new_contacts=False, user_notification=True, group_notification=False, channel_notification=False, update_parameters=["user_message_preview", "in_app_sound", "user_notification"] : Bot._create(4, self.auth, "setSetting", {"settings": {"user_message_preview": user_message_preview, "user_notification": user_notification, "group_message_preview": group_message_preview, "group_notification": group_notification, "channel_message_preview": channel_message_preview, "channel_notification": channel_notification, "in_app_sound": in_app_sound, "new_contacts": new_contacts}, "update_parameters": update_parameters})
	setOwning           = lambda self, chat_id, newOwnerGuid: Bot._create(4, self.auth, "requestChangeObjectOwner", {"object_guid": chat_id, "new_owner_user_guid": newOwnerGuid})

	terminateOtherSessions = lambda self: Bot._create(5, self.auth, "terminateOtherSessions", {})

	unbanMember  = lambda self, chat_id, member_id: Bot._create(5, self.auth, f"ban{Bot._chatDetection(chat_id)}Member", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "member_guid": member_id, "action":"Unset"})
	unpin        = lambda self, chat_id, message_id: Bot._create(4, self.auth, "setPinMessage", {"action":"Unpin","message_id": message_id,"object_guid": chat_id})
	unblock      = lambda self, chat_id: Bot._create(5, self.auth, "setBlockUser", {"action": "Unblock","user_guid": chat_id})
	unmuteChat   = lambda self, chat_id: Bot._create(5, self.auth, "setActionChat", {"action": "Unmute", "object_guid": chat_id})
	uploadAvatar = lambda self, chat_id, main, thumbnail="": Bot._create(5, self.auth, "uploadAvatar", {"object_guid": chat_id, "thumbnail_file_id": str(Bot.uploadFile(self, thumbnail or main)[0]["id"]), "main_file_id": str(Bot.uploadFile(self, main)[0]["id"])})
	uploadFile   = lambda self, file, frequest=None, logging=False: uploadFile(self, file, frequest, logging)

	votePoll     = lambda self, poll_id, option_index: Bot._create(4, self.auth, "votePoll", {"poll_id": poll_id,"selection_index": option_index})

class Socket:
	appliedFilters, chats, noChats, filtersType, func = *[[]]*3, "all", lambda msg: ...

	def __init__(self, auth, proxy:str=None, logging:bool=False): self.auth, self.enc, self.proxy, self.logging = auth, encryption(auth), proxy, logging

	def on_open(self, ws):
		Thread(target=ws.send(dumps({"api_version": "4","auth": self.auth,"data_enc": "","method": "handShake"})), args=()).start()

	on_error = lambda self, ws, error:     print(error) if self.logging else None
	on_close = lambda self, ws, code, msg: print({"code": code, "message": msg}) if self.logging else None
	on_ping  = lambda self, ws, msg :      print("ping") if self.logging else None
	on_pong  = lambda self, ws, msg :      print("pong") if self.logging else None

	def on_message(self, ws, message):
		try:
			from rubika.Types import Message
			bot, update, conditions = Bot("", self.auth), loads(self.enc.decrypt(loads(message)["data_enc"])), []
			if self.logging: print(update)
			parsedMessage = Message(self.auth, update["message_updates"][-1], chat_id=update["message_updates"][-1]["object_guid"], bot=bot)
			[conditions.append(condition(bot, update)) for condition in Socket.appliedFilters]
			if (Socket.chats == [] or (Socket.chats != [] and parsedMessage.chat_id in Socket.chats)) and (Socket.noChats == [] or (Socket.noChats != [] and not parsedMessage.chat_id in Socket.noChats)):
				if   Socket.filtersType == "any" and any(conditions):        Thread(target=Socket.func, args=(parsedMessage,)).start()
				elif Socket.filtersType == "invert" and not all(conditions): Thread(target=Socket.func, args=(parsedMessage,)).start()
				elif all(conditions):                                        Thread(target=Socket.func, args=(parsedMessage,)).start()
		except IndexError: pass
		except Exception as e: print("\n✘ ERROR at line : ", exc_info()[2].tb_lineno, "\n    ",e) if self.logging else None

	def handler(self, *args, **kwargs):
		def wrapper(func):
			import websocket

			Socket.func, Socket.appliedFilters, Socket.filtersType, Socket.chats, Socket.noChats = func, args, kwargs.get("Type") or types.ALL, kwargs.get("chats") or [], kwargs.get("blacklist") or []
			try: Bot.wsURL = choice(list(GET(Bot.getDCsURL).json()["data"]["socket"].values()))
			except exceptions.ConnectionError: ...
			ws = websocket.WebSocketApp(Bot.wsURL, on_open = Socket(self.auth).on_open, on_message = Socket(self.auth).on_message, on_error = Socket(self.auth).on_error, on_close = Socket(self.auth).on_close, on_ping = Socket(self.auth).on_ping, on_pong = Socket(self.auth).on_pong)
			websocket.enableTrace(self.logging)
			ws.run_forever(http_proxy_host = self.proxy[0] if self.proxy is not None else None, http_proxy_port = self.proxy[1] if self.proxy is not None else None, ping_interval=30, ping_timeout=10)

		return wrapper