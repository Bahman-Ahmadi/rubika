from re import findall
from threading import Thread
from datetime import datetime
from rubika.client import Bot, Socket

bot = None
socket = None
lockTime = None

class Tools:
	def __init__(self, auth):
		global bot
		global socket
		bot = Bot(auth)
		socket = Socket(auth)

	def antiInsult(self, msg):
		return any(word in open("dontReadMe.txt").read().split("\n") for word in msg.split())
	
	def antiAD(self, msg):
		links = list(map(lambda ID: ID.strip()[1:],findall(r"@[\w|_|\d]+", msg))) + list(map(lambda link:link.split("/")[-1],findall(r"rubika\.ir/\w+",msg)))
		joincORjoing = "joing" in msg or "joinc" in msg
	
		if joincORjoing: return True
		else:
			for link in links:
				try:
					Type = bot.getInfoByUsername(link)["data"]["chat"]["abs_object"]["type"]
					if Type == "Channel": return True
				except KeyError: return False

	def antiSpam(self, messages):
		hasSpam, beforeIter = False, messages[0]
		for msg in messages[1:]: hasSpam, beforeIter = msg == beforeIter, msg
		return hasSpam

	class lockSchedule:
		def __init__(self): pass

		def setLockTime(self, h, m):
			global lockTime
			lockTime = f"{h}:{m}"

		def getLockTime(self):
			global lockTime
			return lockTime
	
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