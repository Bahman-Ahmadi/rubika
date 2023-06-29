from os import path
from sys import exc_info
from base64 import b64decode
from threading import Thread
from datetime import datetime
from json import loads, dumps
from random import randint, choice
from requests import get as GET, exceptions

from rubika.fileIO import *
from rubika.filters import *
from rubika.tools import Tools
from rubika.exceptions import InvalidAuth
from rubika.encryption import encryption
from rubika.configs import makeData, makeTmpData, defaultDevice, _getURL, welcome, __version__, __license__, __copyright__

welcome(f"rubika library version {__version__}\n{__copyright__}\n→ docs : https://rubikalib.github.io\n")

class Bot:
    downloadURL, DCsURL, getDCsURL, wsURL = "https://messengerX.iranlms.ir/GetFile.ashx", "https://messengerg2cX.iranlms.ir/", "https://getdcmess.iranlms.ir", "wss://msocket1.iranlms.ir:80"

    def __init__(self, appName:str, auth:str=None, privateKey:str=None, \
                 b64decodePrivate:bool=True, userAgent:str="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0", \
                 wantRegister:bool=True, device:dict=defaultDevice):
        
        # Setting basic variables
        self.appName, self.enc = appName, encryption
    
        # Config the account
        if auth is not None and len(auth) == 32:
            self.auth = auth
        else:
            fileName = f"{self.appName}.json"
            fileExists = path.exists(fileName)
            if fileExists:
                self.auth = loads(open(fileName).read())["auth"]
                privateKey = loads(open(fileName).read())["private"]
                b64decodePrivate = False
            else:
                phoneNumber = input(">>> Enter the Phone number (e.g. 09123456789): ")
                sendCodeResp = Bot.sendCode(phoneNumber)
                
                if sendCodeResp.get('data') is None:
                    raise InvalidAuth('Unfortunately, your account has been suspended!')
                elif sendCodeResp['data']['status'] == 'SendPassKey':
                    passKey = input(f">>> Enter your 2FA pass key{'(' + sendCodeResp['data'].get('hint_pass_key') + ')' if sendCodeResp['data'].get('hint_pass_key') is not None else ''}: ")
                    sendCodeResp = Bot.sendCode(phoneNumber, passKey=passKey)
                    while sendCodeResp['data']['status'] == "InvalidPassKey":
                        passKey = input(f">>> Re-Enter your 2FA pass key{'(' + sendCodeResp['data'].get('hint_pass_key') + ')' if sendCodeResp['data'].get('hint_pass_key') is not None else ''}: ")
                        sendCodeResp = Bot.sendCode(phoneNumber, passKey=passKey)
                else:
                    tmp, codeHash = sendCodeResp['tmp'], sendCodeResp["data"]["phone_code_hash"]
                    otp = input(">>> Enter activation code: ")
                    account = Bot.signIn(tmp, phoneNumber, codeHash, otp)
                    while account['data']['status'] == 'CodeIsInvalid':
                        otp = input(">>> Re-Enter activation code: ")
                        account = Bot.signIn(tmp, phoneNumber, codeHash, otp)
                
                    self.auth = account['auth']
                    Bot.privateKey = privateKey = account['private']
                    open(f"{self.appName}.json", "w").write(dumps(account, indent=4, ensure_ascii=True))
                    
                    if wantRegister:
                        Bot.registerDevice(self.auth, device=device)
        
        # No matter that login is manually or automatically, this block will run anyway
        if b64decodePrivate:
            privateKey = loads(b64decode(privateKey).decode('utf-8'))['d']
     
        Bot.privateKey = self.privateKey = privateKey
        Bot.enc = self.enc = self.enc(self.enc.changeAuthType(self.auth), private_key=privateKey)

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_value, exc_tb): return self


    # _getURL    = lambda dc_id=None: _getURL(Bot.DCsURL, Bot.getDCsURL, dc_id)
    def addContact(self, first_name, last_name, phone):
        return Bot._create(self.auth, "addAddressBook", {"first_name": first_name, "last_name": last_name, "phone": phone})

    def addGroup(self, title, users_chat_id):
        return Bot._create(self.auth, "addGroup", {"title": title, "member_guids": users_chat_id})

    def addChannel(self, title, channelType="Public", users_chat_id=None):
        return Bot._create(self.auth, "addChannel", {"channel_type": channelType, "title": title, "member_guids": users_chat_id or []})

    def addFolder(self, name, exclude_chat_types=[], exclude_object_guids=[], include_chat_types=[], include_object_guids=[], is_add_to_top=True, folder_id=""):
        return Bot._create(self.auth, "addFolder", dict(exclude_object_guids=exclude_object_guids, include_object_guids=include_object_guids, exclude_chat_types=exclude_chat_types, include_chat_types=include_chat_types, folder_id=folder_id, is_add_to_top=is_add_to_top, name=name))


    def banMember(self, chat_id, member_id):
        return Bot._create(self.auth, f"ban{Bot._chatDetection(chat_id)}Member", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "member_guid": member_id, "action": "Set"})

    def block(self, chat_id):
        return Bot._create(self.auth, "setBlockUser", {"action": "Block", "user_guid": chat_id})


    @staticmethod
    def _create(auth, method, data, client=clients.web):
        return makeData(auth, encryption(encryption.changeAuthType(auth), private_key=Bot.privateKey), method, dict(data))

    @staticmethod
    def _createTMP(method, data, tmp=None):
        return makeTmpData(method, dict(data), tmp=tmp, url=_getURL(DCsURL=Bot.DCsURL, getDCsURL=Bot.getDCsURL, dc_id=None))

    @staticmethod
    def _chatDetection(chat_id):
        return Tools.chatDetection(chat_id)

    def changeLink(self, chat_id):
        return Bot._create(self.auth, f"set{Bot._chatDetection(chat_id)}Link", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id})

    def changePassword(self, hint, newPass, oldPass):
        return Bot._create(self.auth, "changePassword", {"new_hint": hint, "new_password": newPass, "password": oldPass})

    def checkPassword(self, password):
        return Bot._create(self.auth, "checkTwoStepPasscode", {"password": password}).get("data").get("is_vaild")


    def deleteContact(self, chat_id):
        return Bot._create(self.auth, "deleteContact", {"user_guid": chat_id})

    def deleteMessages(self, chat_id, message_ids):
        return Bot._create(self.auth, "deleteMessages", {"object_guid": chat_id, "message_ids": list(message_ids), "type": "Global"})

    def deleteAdmin(self, chat_id, member_id):
        return Bot._create(self.auth, f"set{Bot._chatDetection(chat_id)}Admin", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "action": "UnsetAdmin", "member_guid": member_id})

    def deleteAvatar(self, chat_id, avatar_id):
        return Bot._create(self.auth, "deleteAvatar", {"object_guid": chat_id, "avatar_id": avatar_id})

    def deleteChatHistory(self, chat_id, lastMessageId):
        return Bot._create(self.auth, "deleteChatHistory", {"object_guid": chat_id, "last_message_id": lastMessageId})

    def deleteFolder(self, folder_id):
        return Bot._create(self.auth, "deleteFolder", dict(folder_id=folder_id))

    def deleteUserChat(self, chat_id, lastMessageID):
        return Bot._create(self.auth, "deleteUserChat", {"last_deleted_message_id": lastMessageID, "user_guid": chat_id})

    def download(self, chat_id, message_id, save=True, saveAs=None, logging=True):
        return download(self, chat_id, message_id, save, saveAs, logging)

    def disablePassword(self, password):
        return Bot._create(self.auth, "turnOffTwoStep", {"password": password})


    def editMessage(self, message_id, chat_id: str, newText: str, metadata: list = None, parse_mode: str = None) -> dict:
        metadata, newText = Bot.loadMetadata(metadata, parse_mode, newText)
        return Bot._create(self.auth, "editMessage", {"message_id": message_id, "object_guid": chat_id, "text": newText, "metadata": metadata})

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
        return Bot._create(self.auth, "editFolder", kwargs)

    def editVoiceChat(self, chat_id, voice_chat_id, title):
        return Bot._create(self.auth, f"set{Bot._chatDetection(chat_id)}VoiceChatSetting", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "voice_chat_id": voice_chat_id, "title": title, "updated_parameters": ["title"]})

    def editChatInfo(self, chat_id, **kwargs):
        chat = Bot._chatDetection(chat_id)
        data, result = {f"{chat.lower()}_guid": chat_id}, []
        if "username" in list(kwargs.keys()):
            result.append(Bot._create(self.auth, "updateChannelUsername", {"channel_guid": chat_id, "username": kwargs.get(
                "username").replace("@", ""), "updated_parameters": ["username"]}))
            kwargs.pop("username")
        if kwargs != {} and not 'username' in kwargs.keys():
            for k, v in kwargs.items():
                data[k] = v
            result.append(Bot._create(self.auth, f"edit{chat}Info", dict(
                channel_guid=chat_id, **kwargs, updated_parameters=list(kwargs.keys()))))
        return result

    def editProfile(self, **kwargs) -> list:
        result: list = []
        if "username" in list(kwargs.keys()):
            result.append(Bot._create(self.auth, "updateUsername", {
                          "username": kwargs.get("username"), "updated_parameters": ["username"]}))
            kwargs.pop("username")
        if kwargs != {} and not 'username' in kwargs.keys():
            result.append(Bot._create(self.auth, "updateProfile", {"first_name": kwargs.get("first_name"), "last_name": kwargs.get(
                "last_name"), "bio": kwargs.get("bio"), "updated_parameters": list(kwargs.keys())}))
        return result


    def forwardMessages(self, From, message_ids, to):
        return Bot._create(self.auth, "forwardMessages", {"from_object_guid": From, "message_ids": message_ids, "rnd": f"{randint(100000,999999999)}", "to_object_guid": to})

    def finishVoiceChat(self, chat_id, voice_chat_id):
        return Bot._create(self.auth, f"discard{Bot._chatDetection(chat_id)}VoiceChat", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "voice_chat_id": voice_chat_id})


    def getMe(self):
        return Bot.getInfo(self)

    def getChats(self, start_id=None):
        return Bot._create(self.auth, "getChats", {"start_id": start_id})

    def getMessages(self, chat_id, min_id, start_id=None):
        return Bot._create(self.auth, "getMessagesInterval", {"object_guid": chat_id, "middle_message_id": min_id, "start_id": start_id}).get("data").get("messages")

    def getLastMessage(self, chat_id):
        return Bot.getMessages(self, chat_id, Bot.getInfo(self, chat_id)["chat"]["last_message"]["message_id"])[-1]  # it isn't a server method , is a shortcut

    def getInfoByUsername(self, username):
        return Bot._create(self.auth, "getObjectByUsername", {"username": username.replace("@", "")})

    def getBlacklist(self, chat_id, start_id=None):
        return Bot._create(self.auth, f"getBanned{Bot._chatDetection(chat_id)}Members", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "start_id": start_id}).get("data")

    def getContactsUpdates(self):
        return Bot._create(self.auth, "getContactsUpdates", {"state": round(datetime.today().timestamp()) - 200})

    def getMyBlacklist(self, start_id=None):
        return Bot._create(self.auth, "getBlockedUsers", {"start_id": start_id})

    def getAbsObjects(self, chat_ids):
        return Bot._create(self.auth, "getAbsObjects", {"object_guids": chat_ids})

    def getAdmins(self, chat_id, start_id=None):
        return Bot._create(self.auth, f"get{Bot._chatDetection(chat_id)}AdminMembers", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "start_id": start_id})

    def getAdminAccesses(self, chat_id, admin_guid):
        return Bot._create(self.auth, f"get{Bot._chatDetection(chat_id)}AdminAccessList", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "member_guid": admin_guid})

    def getMessagesInfo(self, chat_id, message_ids):
        return Bot._create(self.auth, "getMessagesByID", {"object_guid": chat_id, "message_ids": list(message_ids)}).get("data").get("messages")

    def getMembers(self, chat_id, search_text=None, start_id=None):
        return Bot._create(self.auth, f"get{Bot._chatDetection(chat_id)}AllMembers", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "search_text": search_text, "start_id": start_id})

    def getInfo(self, chat_id=None):
        return Bot._create(self.auth, f"get{'User' if chat_id is None else Bot._chatDetection(chat_id)}Info", {} if chat_id is None else {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id}).get("data")

    def getLink(self, chat_id):
        return Bot._create(self.auth, f"get{Bot._chatDetection(chat_id)}Link", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id}).get("data").get("join_link")

    def getPreviewByJoinLink(self, link):
        return Bot._create(self.auth, f"{'group' if 'joing' in link else 'channel'}PreviewByJoinLink", {"hash_link": link.split("/")[-1]})

    def getChatAds(self):
        return Bot._create(self.auth, "getChatAds", {"state": round(datetime.today().timestamp()) - 200}).get("data")

    def getChatsUpdate(self):
        return Bot._create(self.auth, "getChatsUpdates", {"state": round(datetime.today().timestamp()) - 200}).get("data")

    def getChatUpdate(self, chat_id):
        return Bot._create(self.auth, "getMessagesUpdates", {"object_guid": chat_id, "state": round(datetime.today().timestamp()) - 200})

    def getGroupMentionList(self, group_guid, mention_text):
        return Bot._create(self.auth, "getGroupMentionList", {"group_guid": group_guid, "search_mention": mention_text})

    def getGroupDefaultAccess(self, group_guid):
        return Bot._create(self.auth, "getGroupDefaultAccess", {"group_guid": group_guid})

    def getMyStickerSet(self):
        return Bot._create(self.auth, "getMyStickerSets", {})

    def getAvatars(self, chat_id):
        return Bot._create(self.auth, "getAvatars", {"object_guid": chat_id})

    def getPollStatus(self, poll_id):
        return Bot._create(self.auth, "getPollStatus", {"poll_id": str(poll_id)})

    def getPollOptionVoters(self, poll_id, option_index, start_id=None):
        return Bot._create(self.auth, "getPollOptionVoters", {"poll_id": poll_id, "selection_index": option_index, "start_id": start_id})

    def getPostByLink(self, link):
        return Bot._create(self.auth, "getLinkFromAppUrl", {"app_url": link})["data"]["link"]["open_chat_data"]

    def getUserCommonGroups(self, chat_id):
        return Bot._create(self.auth, "getCommonGroups", {"user_guid": chat_id})

    def getGroupOnlineMembersCount(self, chat_id):
        return Bot._create(self.auth, "getGroupOnlineCount", {"group_guid": chat_id}).get("online_count")

    def getTwoPasscodeStatus(self):
        return Bot._create(self.auth, "getTwoPasscodeStatus", {})

    def getPrivacySetting(self):
        return Bot._create(self.auth, "getPrivacySetting", {})

    def getNotificationSetting(self):
        return Bot._create(self.auth, "getNotificationSetting", {}).get("notification_setting")

    def getSuggestedFolders(self):
        return Bot._create(self.auth, "getSuggestedFolders", {})

    def getFolders(self):
        return Bot._create(self.auth, "getFolders", {}).get("folders")

    def getOwning(self, chat_id):
        return Bot._create(self.auth, "getPendingObjectOwner", {"object_guid": chat_id})

    def getMySessions(self):
        return Bot._create(self.auth, "getMySessions", {})

    def getContacts(self, start_id=None):
        return Bot._create(self.auth, "getContacts", {"start_id": start_id})


    def invite(self, chat_id, user_ids):
        return Bot._create(self.auth, f"add{Bot._chatDetection(chat_id)}Members", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "member_guids": user_ids})


    def join(self, value):
        return Bot._create(self.auth, "joinChannelAction", {"action": "Join", "channel_guid": value}) if value.startswith("c") else Bot._create(self.auth, "joinGroup", {"hash_link": value.split("/")[-1]})


    def logout(self):
        return Bot._create(self.auth, "logout", {})

    def leave(self, chat_id):
        return Bot._create(self.auth, "joinChannelAction", {"action": "Leave", "channel_guid": chat_id}) if chat_id.startswith("c") else Bot._create(self.auth, "leaveGroup", {"group_guid": chat_id})

    @staticmethod
    def loadMetadata(metadata, parse_mode, text) -> tuple:
        if metadata is not None:
            metadata = {"meta_data_parts": metadata}
        if parse_mode is not None:
            parsedResult = Tools.parse(parse_mode, text)
            metadata, text = {
                "meta_data_parts": parsedResult["metadata"]}, parsedResult["realText"]
        return metadata if metadata != {"meta_data_parts": []} else None, text


    def muteChat(self, chat_id):
        return Bot._create(self.auth, "setActionChat", {"action": "Mute", "object_guid": chat_id})


    def pin(self, chat_id, message_id):
        return Bot._create(self.auth, "setPinMessage", {"action": "Pin", "message_id": message_id, "object_guid": chat_id})

    @staticmethod
    def registerDevice(auth, device=defaultDevice):
        return Bot._create(auth, "registerDevice", device)

    def reportChat(self, chat_id, reportType=106, description=None):
        return Bot._create(self.auth, "reportObject", {"object_guid": chat_id, "report_description": description, "report_type": reportType, "report_type_object": "Object"})

    def removeChat(self, chat_id):
        return Bot._create(self.auth, f"remove{Bot._chatDetection(chat_id)}", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id})

    def requestSendFile(self, file, size=None):
        return requestSendFile(self, file, int(size))

    def resendMessage(self, From, message_id, To, **kwargs):
        message = Bot.getMessagesInfo(self, From, [str(message_id)])[0]
        for key, value in kwargs.items():
            message[key] = value
        return Bot._create(self.auth, "sendMessage", dict(object_guid=To, rnd=str(randint(100000, 999999999)), **message))

    @staticmethod
    def sendCode(phoneNumber, passKey=None, Type="SMS"):
        return Bot._createTMP("sendCode", {"phone_number": f"98{phoneNumber[1:]}", "pass_key": passKey, "send_type": Type})

    @staticmethod
    def signIn(tmp, phoneNumber, phone_code_hash, phone_code):
        public, private = encryption.rsaKeyGenerate()
        resp = Bot._createTMP("signIn", {"phone_number": f"98{phoneNumber[1:]}", "phone_code_hash": phone_code_hash, "phone_code": phone_code, "public_key": public}, tmp=tmp)
        if resp['status'] == "OK" and resp['data']['status'] == "OK":
            resp['auth'] = encryption.decryptRsaOaep(private, resp['data']['auth'])
            resp['private'] = private
        return resp

    def sendMessage(self, chat_id: str, text: str, metadata: list = None, parse_mode: str = None, message_id=None) -> dict:
        metadata, text = Bot.loadMetadata(metadata, parse_mode, text)
        return Bot._create(self.auth, "sendMessage", {"object_guid": chat_id, "rnd": f"{randint(100000,999999999)}", "text": text, "metadata": metadata, "reply_to_message_id": message_id})

    def sendPhoto(self, chat_id: str, file: str, size: list = None, thumbnail: str = "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", metadata: list = None, parse_mode: str = None, caption: str = None, message_id=None, uresponse: list = None) -> dict:
        # size = [width:int, height:int]
        uresponse = uresponse or Bot.uploadFile(self, file)
        if "." in thumbnail:
            thumbnail = str(Tools.getThumbInline(open(file, "rb").read() if path.isfile(file) else len(file) if not "http" in file else GET(file).content))
        if size is None:
            size = Tools.getImageSize(open(file, "rb").read() if path.isfile(file) else len(file) if not "http" in file else GET(file).content)
        metadata, caption = Bot.loadMetadata(metadata, parse_mode, caption)
        return Bot._create(self.auth, "sendMessage", {"file_inline": {"dc_id": uresponse[0]["dc_id"], "file_id": uresponse[0]["id"], "type": "Image", "file_name": file.split("/")[-1], "size": str(len(GET(file).content if "http" in file else open(file, "rb").read() if path.isfile(file) else len(file))), "mime": file.split(".")[-1], "access_hash_rec": uresponse[1], "width": size[0], "height": size[1], "thumb_inline": thumbnail}, "object_guid": chat_id, "text": caption, "metadata": metadata, "rnd": f"{randint(100000,999999999)}", "reply_to_message_id": message_id})

    def sendVideo(self, chat_id: str, file: str, width: int = 720, height: int = 720, metadata: list = None, parse_mode: str = None, caption=None, message_id=None, uresponse: list = None):
        from tinytag import TinyTag  # pip install tinytag
        uresponse, metadata, caption = uresponse or Bot.uploadFile(self, file), *Bot.loadMetadata(metadata, parse_mode, caption)
        return Bot._create(self.auth, "sendMessage", {"file_inline": {"access_hash_rec": uresponse[1], "auto_play": False, "dc_id": uresponse[0]["dc_id"], "file_id": str(uresponse[0]["id"]), "file_name": file.split("/")[-1], "height": height, "mime": file.split(".")[-1], "size": str(len(GET(file).content if "http" in file else open(file, "rb").read() if path.isfile(file) else len(file))), "thumb_inline": file, "time": round(TinyTag.get(file).duration * 1000), "type": "Video", "width": width}, "is_mute": False, "object_guid": chat_id, "text": caption, "metadata": metadata, "rnd": str(randint(100000, 999999999)), "reply_to_message_id": message_id})

    def sendMusic(self, chat_id: str, file: str, metadata: list = None, parse_mode: str = None, caption=None, message_id=None, uresponse: list = None):
        from tinytag import TinyTag  # pip install tinytag
        uresponse, metadata, caption = uresponse or Bot.uploadFile(self, file), *Bot.loadMetadata(metadata, parse_mode, caption)
        return Bot._create(self.auth, "sendMessage", {"file_inline": {"access_hash_rec": uresponse[1], "auto_play": False, "dc_id": uresponse[0]["dc_id"], "file_id": str(uresponse[0]["id"]), "file_name": file.split("/")[-1], "height": 0.0, "mime": file.split(".")[-1], "music_performer": str(TinyTag.get(file).artist), "size": len(GET(file).content if "http" in file else open(file, "rb").read() if path.isfile(file) else len(file)), "time": round(TinyTag.get(file).duration), "type": "Music", "width": 0.0}, "is_mute": False, "object_guid": chat_id, "text": caption, "metadata": metadata, "rnd": randint(100000, 999999999), "reply_to_message_id": message_id})

    def sendVoice(self, chat_id: str, file: str, time: int = None, metadata: list = None, parse_mode: str = None, caption: str = None, message_id=None, uresponse: list = None) -> dict:
        # file's format must be ogg. time must be ms (type: float).
        uresponse, metadata, caption = uresponse or Bot.uploadFile(
            self, file), *Bot.loadMetadata(metadata, parse_mode, caption)
        if time is None:
            from tinytag import TinyTag  # pip install tinytag
            time = round(TinyTag.get(file).duration)
        return Bot._create(self.auth, "sendMessage", {"file_inline": {"dc_id": str(uresponse[0]["dc_id"]), "file_id": uresponse[0]["id"], "type": "Voice", "file_name": file.split("/")[-1], "size": len(GET(file).content if "http" in file else open(file, "rb").read() if path.isfile(file) else len(file)), "time": float(time), "mime": file.split(".")[-1], "access_hash_rec": str(uresponse[1])}, "object_guid": chat_id, "text": caption, "metadata": metadata, "rnd": f"{randint(100000,999999999)}", "reply_to_message_id": message_id})

    def sendDocument(self, chat_id: str, file: str, caption: str = None, metadata: list = None, parse_mode: str = None, message_id=None, uresponse: list = None) -> dict:
        # Bot.sendDocument("guid","./file.txt", caption="anything", message_id="12345678")
        uresponse, metadata, caption = uresponse or Bot.uploadFile(
            self, file), *Bot.loadMetadata(metadata, parse_mode, caption)
        return Bot._create(self.auth, "sendMessage", {"object_guid": chat_id, "metadata": metadata, "text": caption, "reply_to_message_id": message_id, "rnd": f"{randint(100000,999999999)}", "file_inline": {"dc_id": str(uresponse[0]["dc_id"]), "file_id": str(uresponse[0]["id"]), "type": "File", "file_name": file.split("/")[-1], "size": len(GET(file).content if "http" in file else open(file, "rb").read() if path.isfile(file) else len(file)), "mime": file.split(".")[-1], "access_hash_rec": uresponse[1]}})

    def sendLocation(self, chat_id, location, message_id):
        return Bot._create(self.auth, "sendMessage", {"is_mute": False, "object_guid": chat_id, "rnd": f"{randint(100000,999999999)}", "location": {"latitude": location[0], "longitude": location[1]}, "reply_to_message_id": message_id})

    def sendGIF(self, chat_id: str, file: str, width: int, height: int, time: int = None, metadata: list = None, parse_mode: str = None, thumbnail: str = r"/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDACAWGBwYFCAcGhwkIiAmMFA0MCwsMGJGSjpQdGZ6eHJm\ncG6AkLicgIiuim5woNqirr7EztDOfJri8uDI8LjKzsb/2wBDASIkJDAqMF40NF7GhHCExsbGxsbG\nxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsb/wAARCAAyADIDASIA\nAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQA\nAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3\nODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWm\np6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEA\nAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSEx\nBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElK\nU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3\nuLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDXqCXo\nasVXk70DKwHNSBaRRzUgrnZqMUfMKtkcCq24KcmntdxgDmtIEyJ8UVB9ti9aKskmB4qJ/uk1L2qC\nZtsZpiII5P3hB6VDLOySZ7UyVJDEWWoXLGD5uoqFHQtvUnln3rkVB5bv3qqk3Y1filUKM09kCV2R\nfZ39aKtectFK7K5URwagzrila4klcJiqdtbsrA5q+jLE4ZhVXsyErq5bCFYAMVQuVYKVC9av/akc\ncGmy4ZeKaIaZgeWVlANX1jDKKbdRYYNQJQqdamRpAk8pfWiq/n+9FSWPtifM61LcdKKKctyIbEMJ\nO4c1oj7lFFUiWQXH+qNZLmiihjiNzRRRUlH/2Q==\n", caption: str = None, message_id: int = None, uresponse: list = None) -> dict:
        uresponse, metadata, caption = uresponse or Bot.uploadFile(
            self, file), *Bot.loadMetadata(metadata, parse_mode, caption)
        if time is None:
            from tinytag import TinyTag  # pip install TinyTag
            time = round(TinyTag.get(file).duration * 1000)
        return Bot._create(self.auth, "sendMessage", {"object_guid": chat_id, "is_mute": False, "rnd": randint(100000, 999999999), "file_inline": {"access_hash_rec": str(uresponse[1]), "dc_id": str(uresponse[0]["dc_id"]), "file_id": int(uresponse[0]["id"]), "auto_play": False, "file_name": file.split("/")[-1], "width": width, "height": height, "mime": file.split(".")[-1], "size": len(GET(file).content if "http" in file else open(file, "rb").read() if path.isfile(file) else len(file)), "thumb_inline": thumbnail, "time": time, "type": "Gif"}, "text": caption, "metadata": metadata, "reply_to_message_id": message_id})

    def sendContact(self, chat_id: str, user_guid: str, phone: str, firstName: str, lastName: str = None, avatarFile: str = None, uresponse: list = None) -> dict:
        '''
        chat_id: destination guid for sending the contact
        user_guid: contact's guid
        phone: contact's phone number
        first_name: contact's first name
        '''
        uresponse = Bot.uploadFile(self, avatarFile) if avatarFile is not None else uresponse or [
            {"dc_id": "702", "id": 2521972095}, "5653363141731050515439840306092021010915"]
        avatar = {"access_hash_rec": str(uresponse[1]), "file_id": int(uresponse[0]["id"]), "auto_play": False, "dc_id": str(uresponse[0]["dc_id"]), "height": 0, "mime": "none", "size": 10025 if str(uresponse[0]["id"]) == "2521972095" else len(GET(avatarFile).content if "http" in avatarFile else open(avatarFile, "rb").read() if path.isfile(avatarFile) else len(avatarFile)), "time": 0, "type": "File", "width": 0}
        return Bot._create(self.auth, "sendMessage", {"is_mute": False, "message_contact": {"contactAbsObject": {"avatar_thumbnail": avatar, "first_name": firstName, "last_name": lastName or "", "is_deleted": False, "is_verified": False, "object_guid": user_guid, "type": "User"}, "first_name": firstName, "last_name": lastName or "", "phone_number": "+98"+phone[1:], "user_guid": user_guid, "vcard": f"BEGIN:VCARD\nVERSION:3.0\nFN:{firstName}\nTEL;MOBILE:+98{phone[1:]}\nEND:VCARD"}, "object_guid": chat_id, "rnd": randint(100000, 999999999)})

    def setMembersAccess(self, chat_id, access_list):
        return Bot._create(self.auth, "setGroupDefaultAccess", {"access_list": access_list, "group_guid": chat_id})

    def setGroupTimer(self, chat_id, time):
        return Bot._create(self.auth, "editGroupInfo", {"group_guid": chat_id, "slow_mode": time, "updated_parameters": ["slow_mode"]})

    def setAdmin(self, chat_id, member_id, access_list=None):
        return Bot._create(self.auth, f"set{Bot._chatDetection(chat_id)}Admin", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "access_list": access_list or [], "action": "SetAdmin", "member_guid": member_id})

    def seenChats(self, seenList):
        return Bot._create(self.auth, "seenChats", {"seen_list": dict(seenList)})

    def sendChatAction(self, chat_id, action):
        # every some seconds before sending message this request should send. action can be : Typing, Recording, Uploading
        return Bot._create(self.auth, "sendChatActivity", {"activity": action, "object_guid": chat_id})

    def sendPoll(self, chat_id, allows_multiple_answers, is_anonymous, options, question, Type="Regular", message_id=None):
        return Bot._create(self.auth, "createPoll", {"allows_multiple_answers": bool(allows_multiple_answers), "is_anonymous": bool(is_anonymous), "object_guid": chat_id, "options": list(options), "question": question, "rnd": str(randint(100000, 999999999)), "type": Type, "reply_to_message_id": message_id})

    def sendQuiz(self, chat_id, correct_option_index, is_anonymous, options, question, Type="Quiz", message_id=None):
        return Bot._create(self.auth, "createPoll", {"correct_option_index": int(correct_option_index), "is_anonymous": bool(is_anonymous), "object_guid": chat_id, "options": list(options), "question": question, "rnd": str(randint(100000, 999999999)), "type": Type, "reply_to_message_id": message_id})

    def searchGlobalObjects(self, text, start_id=None):
        return Bot._create(self.auth, "searchGlobalObjects", {"search_text": text, "start_id": start_id})

    def searchChatMessages(self, chat_id, search_text):
        return Bot._create(self.auth, "searchChatMessages", {"object_guid": chat_id, "search_text": search_text})

    def setPhoneVisibility(self, mode="Nobody"):
        return Bot._create(self.auth, "setSetting", {"settings": {"show_my_phone_number": mode}, "update_parameters": ["show_my_phone_number"]})  # mode = Nobody/Everybody/MyContacts

    def setOnlineVisibility(self, mode="Everybody"):
        return Bot._create(self.auth, "setSetting", {"settings": {"show_my_last_online": mode}, "update_parameters": ["show_my_last_online"]})  # mode = Nobody/Everybody/MyContacts

    def setAvatarVisibility(self, mode="Everybody"):
        return Bot._create(self.auth, "setSetting", {"settings": {"show_my_profile_photo": mode}, "update_parameters": ["show_my_profile_photo"]})  # mode = Everybody/MyContacts

    def setCallableBy(self, mode="MyContacts"):
        return Bot._create(self.auth, "setSetting", {"settings": {"can_called_by": mode}, "update_parameters": ["can_called_by"]})  # mode = Everybody/MyContacts

    def setForwardableBy(self, mode="Everybody"):
        return Bot._create(self.auth, "setSetting", {"settings": {"link_forward_message": mode}, "update_parameters": ["link_forward_message"]})  # mode = Nobody/Everybody/MyContacts

    def setJoinableBy(self, mode="MyContacts"):
        return Bot._create(self.auth, "setSetting", {"settings": {"can_join_chat_by": mode}, "update_parameters": ["can_join_chat_by"]})  # mode = Everybody/MyContacts

    def setMyAutoDeleteTime(self, time=24):
        return Bot._create(self.auth, "setSetting", {"settings": {"delete_account_not_active_months": str(time)}, "update_parameters": ["show_my_phone_number"]})  # time = 3/6/12/24 , type: str/int, duration: months

    def setNotifications(self, user_message_preview=True, group_message_preview=False, channel_message_preview=False, in_app_sound=True, new_contacts=False, user_notification=True, group_notification=False, channel_notification=False, update_parameters=["user_message_preview", "in_app_sound", "user_notification"]):
        return Bot._create(self.auth, "setSetting", {"settings": {"user_message_preview": user_message_preview, "user_notification": user_notification, "group_message_preview": group_message_preview, "group_notification": group_notification, "channel_message_preview": channel_message_preview, "channel_notification": channel_notification, "in_app_sound": in_app_sound, "new_contacts": new_contacts}, "update_parameters": update_parameters})

    def setOwning(self, chat_id, newOwnerGuid):
        return Bot._create(self.auth, "requestChangeObjectOwner", {"object_guid": chat_id, "new_owner_user_guid": newOwnerGuid})

    def startVoiceChat(self, chat_id):
        return Bot._create(self.auth, f"create{Bot._chatDetection(chat_id)}VoiceChat", {"object_guid": chat_id})


    def terminateOtherSessions(self):
        return Bot._create(self.auth, "terminateOtherSessions", {})


    def unbanMember(self, chat_id, member_id):
        return Bot._create(self.auth, f"ban{Bot._chatDetection(chat_id)}Member", {f"{Bot._chatDetection(chat_id).lower()}_guid": chat_id, "member_guid": member_id, "action": "Unset"})

    def unpin(self, chat_id, message_id):
        return Bot._create(self.auth, "setPinMessage", {"action": "Unpin", "message_id": message_id, "object_guid": chat_id})

    def unblock(self, chat_id):
        return Bot._create(self.auth, "setBlockUser", {"action": "Unblock", "user_guid": chat_id})

    def unmuteChat(self, chat_id):
        return Bot._create(self.auth, "setActionChat", {"action": "Unmute", "object_guid": chat_id})

    def uploadAvatar(self, chat_id, main, thumbnail=""):
        return Bot._create(self.auth, "uploadAvatar", {"object_guid": chat_id, "thumbnail_file_id": str(Bot.uploadFile(self, thumbnail or main)[0]["id"]), "main_file_id": str(Bot.uploadFile(self, main)[0]["id"])})

    def uploadFile(self, file, frequest=None, logging=False):
        return uploadFile(self, file, frequest, logging)


    def votePoll(self, poll_id, option_index):
        return Bot._create(self.auth, "votePoll", {"poll_id": poll_id, "selection_index": option_index})

class Socket:
    appliedFilters, chats, noChats, filtersType, func = * \
        [[]]*3, "all", lambda msg: ...

    def __init__(self, auth, privateKey, proxy: str = None, logging: bool = False):
        self.auth, self.privateKey, self.enc, self.proxy, self.logging = auth, privateKey, oldEncryption(auth), proxy, logging

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_value, exc_tb): return self

    def on_open(self, ws):
        ws.send({"api_version": "5", "auth": self.auth, "data_enc": "", "method": "handShake"})

    def on_error(self, ws, error):
        print(error) if self.logging else None

    def on_close(self, ws, code, msg):
        print({"code": code, "message": msg}) if self.logging else None

    def on_ping(self, ws, msg):
        print("ping", ws.send(dumps({}))) if self.logging else ws.send(dumps({}))

    def on_pong(self, ws, msg):
        print("pong", msg) if self.logging else None

    def on_message(self, ws, message):
        try:
            from rubika.Types import Message
            bot, update, conditions = Bot("", auth=self.auth, privateKey=self.privateKey), loads(self.enc.decrypt(loads(message)["data_enc"])) if loads(message).get("data_enc") != None else {}, []
            if self.logging:
                print(update)
            parsedMessage = Message(
                self.auth, update["message_updates"][-1], chat_id=update["message_updates"][-1]["object_guid"], bot=bot)
            [conditions.append(condition(bot, update))
             for condition in Socket.appliedFilters]
            if (Socket.chats == [] or (Socket.chats != [] and parsedMessage.chat_id in Socket.chats)) and (Socket.noChats == [] or (Socket.noChats != [] and not parsedMessage.chat_id in Socket.noChats)):
                if Socket.filtersType == "any" and any(conditions):
                    Thread(target=Socket.func, args=(parsedMessage,)).start()
                elif Socket.filtersType == "invert" and not all(conditions):
                    Thread(target=Socket.func, args=(parsedMessage,)).start()
                elif all(conditions):
                    Thread(target=Socket.func, args=(parsedMessage,)).start()
        except IndexError:
            pass
        except Exception as e:
            print("\n✘ ERROR at line : ", exc_info()[2].tb_lineno, "\n    ", e)

    def handler(self, *args, **kwargs):
        def wrapper(func):
            import websocket

            Socket.func, Socket.appliedFilters, Socket.filtersType, Socket.chats, Socket.noChats = func, args, kwargs.get(
                "Type") or types.ALL, kwargs.get("chats") or [], kwargs.get("blacklist") or []
            try:
                Bot.wsURL = _getURL(key='default_sockets')
            except exceptions.ConnectionError:
                ...
            ws = websocket.WebSocketApp(Bot.wsURL, on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close, on_ping=self.on_ping, on_pong=self.on_pong)
            websocket.enableTrace(self.logging)
            Thread(target=ws.run_forever, kwargs=dict(http_proxy_host=self.proxy[0] if self.proxy is not None else None,
                   http_proxy_port=self.proxy[1] if self.proxy is not None else None, ping_interval=30, ping_timeout=5, host="web.rubika.ir")).start()

        return wrapper