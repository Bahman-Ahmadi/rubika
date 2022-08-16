from pathlib import Path
from requests import get, post
from sys import exc_info

from rubika.configs import clients, makeData

def requestSendFile(bot, file:str, size:int=None) -> dict:
	return makeData(4, bot.auth, "requestSendFile", {"file_name": file.split("/")[-1], "mime": file.split(".")[-1], "size": str(size or Path(file).stat().st_size)}, clients.android)

def uploadFile(bot, file, frequest:dict=None, logging:bool=False):
	bytef:bytes    = open(file,"rb").read() if not "http" in file else get(file).content
	frequest:dict  = frequest or requestSendFile(bot, file, size=len(bytef))
	hash_send, file_id, url, size = frequest["access_hash_send"], frequest["id"], frequest["upload_url"], len(bytef)
	header   = {'auth': bot.auth, 'Host': url.replace("https://","").replace("/UploadFile.ashx",""), 'chunk-size': str(size), "part-number": "1", "total-part": "1", 'file-id': str(file_id), 'access-hash-send': hash_send, "content-type": "application/octet-stream", "content-length": str(size), "accept-encoding": "gzip", "user-agent": "okhttp/3.12.1"}

	if size <= 131072:
		while True:
			try: return [frequest, post(data=bytef,url=url,headers=header).json()['data']['access_hash_rec']]
			except Exception as e:
				if logging: print(e)
	else:
		t = size // 131072 + 1
		for i in range(1, t + 1):
			k = (i - 1) * 131072
			header["chunk-size"], header["part-number"], header["total-part"], data = "131072" if i != t else str(len(bytef[k:])), str(i),str(t), bytef[k:k + 131072] if i != t else bytef[k:]
			while True:
				try:
					response = post(data=data,url=url,headers=header).json()
					break
				except Exception as e:
					if logging: print(e)
			if i == t: return [frequest, response['data']['access_hash_rec']]

def uploadFileStepByStep(bot, file, frequest, logging:bool=True):
	bytef:bytes    = open(file,"rb").read() if not "http" in file else get(file).content
	frequest:dict  = frequest or requestSendFile(bot, file, size=len(bytef))
	hash_send, file_id, url, size = frequest["access_hash_send"], frequest["id"], frequest["upload_url"], len(bytef)
	header   = {'auth': bot.auth, 'Host': url.replace("https://","").replace("/UploadFile.ashx",""), 'chunk-size': str(size), "part-number": "1", "total-part": "1", 'file-id': str(file_id), 'access-hash-send': hash_send, "content-type": "application/octet-stream", "content-length": str(size), "accept-encoding": "gzip", "user-agent": "okhttp/3.12.1"}

	if size <= 131072:
		while True:
			try: yield [frequest, post(data=bytef,url=url,headers=header).json()['data']['access_hash_rec'], 1, 1]
			except Exception as e:
				if logging: print(e)
	else:
		t = size // 131072 + 1
		for i in range(1, t + 1):
			k = (i - 1) * 131072
			header["chunk-size"], header["part-number"], header["total-part"], data = "131072" if i != t else str(len(bytef[k:])), str(i),str(t), bytef[k:k + 131072] if i != t else bytef[k:]
			while True:
				try:
					yield [frequest, post(data=data,url=url,headers=header).json(), i, t]
					break
				except Exception as e:
					if logging: print(e)

def download(bot, chat_id:str, message_id:str, save:bool=True, saveAs:str=None, logging:bool=True) -> bytes :
	# download(Bot("APP", "AUTH"), chat_id="chatID", message="MessageID")
	result:bytes  = b""
	message       = bot.getMessagesInfo(chat_id, [str(message_id)])[0]
	
	size          = message["file_inline"]["size"]
	dc_id         = str(message["file_inline"]["dc_id"])
	fileID        = str(message["file_inline"]["file_id"])
	filename      = saveAs or message["file_inline"]["file_name"]
	accessHashRec = message["file_inline"]["access_hash_rec"]

	header = {'auth': bot.auth, 'file-id':fileID, "start-index": "0", "last-index": str(size), 'access-hash-rec':accessHashRec}
	server = bot.downloadURL.replace("X", str(dc_id))
	
	while True:
		try:
			if size <= 131072:
				result += get(url=server,headers=header).content
			else:
				for i in range(0,size,131072):
					header["start-index"], header["last-index"] = str(i), str(i+131072 if i+131072 <= size else size)
					result += get(url=server,headers=header).content
			break
		except Exception as e:
			if logging: print(e, exc_info()[2].tb_lineno)

	if save: open(filename, "wb").write(result)
	return result