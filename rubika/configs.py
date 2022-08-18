from asyncio import run
from random  import sample, choice
from json    import loads, dumps, decoder
from aiohttp import ClientSession, client_exceptions
from string  import ascii_lowercase, ascii_uppercase, digits

from rubika.encryption import encryption
from rubika.exceptions import *

__version__ , __license__ , __copyright__ = "6.0.3" , "GPLv3 license" , "Copyright (C) 2022 Bahman Ahmadi <github.com/Bahman-Ahmadi>"

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
		"app_version" : "4.0.7",
		"platform"    : "Web",
		"package"     : "web.rubika.ir",
		"lang_code"   : "fa"
	}
	android = {
		"app_name"    : "Main",
		"app_version" : "2.9.8",
		"platform"    : "Android",
		"package"     : "app.rbmain.a",
		"lang_code"   : "fa"
	}

class reports:
	OTHER       = 100
	VIOLENCE    = 101
	SPAM        = 102
	PORNOGRAPHY = 103
	CHILD_ABUSE = 104
	COPYRIGHT   = 105
	FISHING     = 106

class visibility:
	EVERYBODY  = "Everybody"
	MYCONTACTS = "MyContacts"
	NOBODY     = "Nobody"

randStr = lambda length, choices=[*ascii_lowercase, *ascii_uppercase, *digits, *"-_"]: "".join([choice(choices) for i in range(length)])

defaultDevice = {
	"app_version"      : "MA_2.9.8",
	"device_hash"      : randStr(32, [*ascii_uppercase, *digits]),
	"device_model"     : "rubikalib",
	"is_multi_account" : False,
	"lang_code"        : "fa",
	"system_version"   : "SDK 22",
	"token"            : f"{randStr(22, [*ascii_lowercase, *ascii_uppercase, *digits])}:{randStr(140)}",
	"token_type"       : "Firebase"
}

def post(json:dict, method, url:str=None, platform="rubika", enc:encryption=None, isEncrypted:bool=True) -> dict:
	async def POST(url, data):
		while 1:
			try:
				async with ClientSession() as session:
					async with session.post(url, json=data) as response:
						response = await response.text()
						response = loads(str(enc.decrypt(loads(response).get("data_enc")))) if "data_enc" in loads(response).keys() and isEncrypted else loads(response)
						if "status" in response.keys() and response.get("status") != "OK":
							print( data, url, response )
							if response.get("status_det") == "NOT_REGISTERED":
								raise NotRegistered("the auth is incorrect. please sure about your account's health then login again.")
							elif response.get("status_det") == "INVALID_INPUT" :
								raise InvalidInput(f"the inserted argument(s) is invaild in the {platform}/{method}. if you're sure about your argument(s), please report this message.")
							elif response.get("status_det") == "TOO_REQUESTS" :
								raise TooRequests(f"the {platform}/{method} method has been limited. please try again later.")
							elif response.get("status_det") == 'INVALID_AUTH':
								raise InvaildAuth(f"the inserted argument(s) in {platform}/{method} is vaild but is not related to other argument(s) or maybe for other reasons, anyway now this method can't run on server. please don't enter fake argument(s) and fix anything can return this exception")
						else:
							return response
			except decoder.JSONDecodeError: ...
			except client_exceptions.ClientConnectorError: url = _getURL(dc_id=64)
	return run(POST(url or _getURL(dc_id=64), json))

def _getURL(DCsURL:str="https://messengerg2cX.iranlms.ir/", getDCsURL:str="https://getdcmess.iranlms.ir", dc_id:int=None):
	from requests import get as GET, exceptions
	while 1:
		try:
			dc_id = dc_id or choice(loads(GET(getDCsURL).text).get("data").get("default_apis"))
			return DCsURL.replace("X", str(dc_id))
		except exceptions.ConnectionError: ...

def makeData(api_version:int, auth:str, method:str, data:dict, client:dict, url:str=_getURL()) -> dict :
	enc = encryption(auth)
	outerJson = {
		"api_version" : str(api_version),
		"auth"        : auth,
		"data_enc"    : enc.encrypt(dumps({
			"method"  : method,
			"input"   : data,
			"client"  : client
		}))
	}

	if int(api_version) == 4:
		outerJson["data_enc"] = enc.encrypt(dumps(data))
		outerJson["client"]   = client
		outerJson["method"]   = method

	return post(outerJson, url=url, platform=client.get('package'), method=method, enc=enc)

def makeTmpData(method:str, data:dict, url:str=_getURL()) -> dict:
	tmp = tmpGeneration()
	enc = encryption(tmp)
	outerJson = {
		"api_version": "5",
		"tmp_session": tmp,
		"data_enc"   : enc.encrypt(dumps({
			"method" : method,
			"input"  : data,
			"client" : clients.web
		}))
	}
	
	return post(outerJson, method, url=url, platform=clients.web.get("package"), enc=enc)

def makeRubinoData(auth:str, method:str, data:dict) -> dict:
	outerJson = {
		"api_version": "0",
		"auth"   : auth,
		"client" : clients.android,
		"data"   : data,
		"method" : method
	}
	return post(outerJson, method, url="https://rubino12.iranlms.ir/", platform="rubino", isEncrypted=False)

tmpGeneration = lambda: randStr(32, [*ascii_lowercase, *digits])

def welcome(text, time:float=0.035):
	from time import sleep
	try:
		from rich import print as Print
		Print(text)
	except ModuleNotFoundError:
		for char in text:
			print(char, end='', flush=True)
			sleep(float(time))
	print()