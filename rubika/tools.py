from re import findall
from threading import Thread
from datetime import datetime

bot = None
socket = None
lockTime = None
unlockTime = None

class Tools:
	def __init__(self, auth):
		from rubika.client import Bot, Socket
		bot = Bot("", auth=auth)
		socket = Socket(auth)

	def hasInsult(self, msg):
		return any(word in open("dontReadMe.txt").read().split("\n") for word in msg.split())
	
	def hasAD(self, msg):
		result = False
		links = list(map(lambda ID: ID.strip()[1:],findall(r"@[\w|_|\d]+", msg))) + list(map(lambda link:link.split("/")[-1],findall(r"rubika\.ir/\w+",msg)))
		joincORjoing = "joing" in msg or "joinc" in msg
	
		if joincORjoing: result = True
		else:
			for link in links:
				try:
					Type = bot.getInfoByUsername(link)["data"]["chat"]["abs_object"]["type"]
					if Type == "Channel": result = True
				except KeyError: result = False

		return result

	def hasSpam(self, messages):
		result, beforeIter = {"isExist":False, "spams":[]}, 0
		for Iter in range(0,len(messages)):
			if messages[beforeIter] == messages[Iter] and Iter != beforeIter:
				result["isExist"] = True
				result["spams"].append([beforeIter, Iter])
			beforeIter = Iter
		return result

	class lockSchedule:
		def __init__(self): pass

		def setLockTime(self, h, m):
			global lockTime
			lockTime = f"{h}:{m}"
	
		def setUnlockTime(self, h, m):
			global unlockTime
			unlockTime = f"{h}:{m}"

		def getLockTime(self):
			global lockTime
			return lockTime

		def getUnlockTime(self):
			global unlockTime
			return unlockTime
	
		def checkLockTime(self, guid, accesses=[]):
			global lockTime
			if datetime.now().strftime("%H:%M") == lockTime:
				bot.setMembersAccess(guid, accesses)
	
		def checkUnlockTime(self, guid, accesses=["ViewMembers","ViewAdmins","SendMessages","AddMember"]):
			global lockTime
			if datetime.now().strftime("%H:%M") == lockTime:
				bot.setMembersAccess(guid, accesses)

	def commandHandler(self, message, command, method:callable):
		if message == command: method()

	def isJoin(self, user_guid:str, channel_guid:str) -> bool:
		userInfo       = bot.getInfo(user_guid)
		haveUserName   = 'username' in userInfo.keys()
		channelMembers = lambda keyword : bot.getMembers(channel_guid, search_text=keyword) if keyword != None else []

		if haveUserName: result = [True for i in channelMembers(userInfo.get('username'))     if i['member_guid'] == user_guid][0]
		else:
			result = [True for i in channelMembers(userInfo.get('first_name'))   if i['member_guid'] == user_guid][0]
			result = [True for i in channelMembers(userInfo.get('last_name'))    if i['member_guid'] == user_guid][0]

		return result == True

	def faster(self, controller):
		def get(): socket.handle()
		def use(): controller(socket.data)
		
		while True:
			Thread(target=get).start()
			Thread(target=use).start()

	loadTime = lambda timestamp, func=__import__("datetime").datetime.fromtimestamp: func(int(timestamp)) # func can be __import__("jdatetime").datetime.fromtimestamp THEN you must install jdatetime using `pip install jdatetime`

	@staticmethod
	def parse(mode, text):
		results = []
		
		realText = text.replace("**","").replace("__","").replace("`","").replace("[","").replace("]","").replace("(","").replace(")","") if mode.lower() == "markdown" else text.replace("<b>","").replace("</b>","").replace("<i>","").replace("</i>","").replace("<pre>","").replace("</pre>","").replace("<a href='","").replace("'>","").replace("</a>", "")
		bolds    = findall(r"\*\*(.*?)\*\*",text) if mode.lower() == "markdown" else findall("<b>(.*?)</b>",text)
		italics  = findall("__(.*?)__",text) if mode.lower() == "markdown" else findall("<i>(.*?)</i>",text)
		monos    = findall("`(.*?)`",text) if mode.lower() == "markdown" else findall("<pre>(.*?)</pre>",text)
		Mentions = findall("\[(.*?)\]\((.*?)\)", text) if mode.lower() == "markdown" else findall("<a href='(.*?)'>(.*?)</a>", text)

		bResult = [realText.index(i) for i in bolds]
		iResult = [realText.index(i) for i in italics]
		mResult = [realText.index(i) for i in monos]
		MResult = [(realText.index(i),realText.index(j)) for i,j in Mentions]

		for i in findall(r"\w.{31}", realText): realText = realText.replace(i, "")

		for index,word,Type in ((bResult, bolds, ["Bold"]*len(bolds)), (iResult, italics, ["Italic"]*len(italics)), (mResult, monos, ["Mono"]*len(monos)), (MResult, Mentions, ["MentionText"]*len(Mentions))):
			if index != [] and word != []:
				result = {"from_index": index[0] if Type[0] != "MentionText" else index[0][0],"length": len(word[0] if Type[0] != "MentionText" else word[0][1]),"type": Type[0]}
				if Type[0] == "MentionText": result["mention_text_object_guid"], result["mention_text_object_type"] = word[0][0], "User"
				results.append(result)
		
		return dict(metadata=results, realText=realText)

	@staticmethod
	def getThumbInline(image_bytes:bytes) -> str:
		import io, base64, PIL.Image
		im, output = PIL.Image.open(io.BytesIO(image_bytes)), io.BytesIO()
		width, height = im.size
		im.save(output, format='PNG')
		im_data = output.getvalue()
		image_data = base64.b64encode(im_data)
		if not isinstance(image_data, str): image_data = image_data.decode()
		return image_data

	@staticmethod
	def getImageSize(image_bytes:bytes) -> list:
		import io, PIL.Image
		im = PIL.Image.open(io.BytesIO(image_bytes))
		width, height = im.size
		return [width , height]