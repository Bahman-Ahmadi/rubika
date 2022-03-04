from re import findall
from threading import Thread
from datetime import datetime
from rubika.client import Bot, Socket

bot = None
socket = None
lockTime = None
unlockTime = None

class Tools:
	def __init__(self, auth):
		global bot
		global socket
		bot = Bot(auth)
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

	def commandHandler(self, message, command, method):
		if message == command: method()

	def isJoin(self, user_guid, channel_guid):
		userInfo = bot.getUserInfo(user_guid)["data"]
		haveUserName = 'username' in userInfo['user']
		channelMembers = lambda keyword : bot.searchInChannelMembers(keyword, channel_guid)


		for i in (channelMembers(userInfo['user']['username'].replace("@","")) if haveUserName else []):
			if i['member_guid'] == user_guid: return True

		for i in channelMembers(userInfo['user']['first_name']):
			if i['member_guid'] == member_guid: return True

		for i in channelMembers(userInfo['user']['last_name']):
			if i['member_guid'] == member_guid: return True

		return False

	def faster(self, controller):
		def get(): socket.handle()
		def use(): controller(socket.data)
		
		while True:
			Thread(target=get).start()
			Thread(target=use).start()

	def parse(self, mode, text):
		results = []
		if mode == "HTML":
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

		return results