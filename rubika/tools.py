from re import findall
from datetime import datetime

bot = None
lockTime = None

class Tools:
	def __init__(self, BOT):
		global bot
		bot = BOT

	def antiInsult(self, msg):
		return any(word in open("dontReadMe.txt").read().split("\n") for word in msg.split())
	
	def antiAD(self, msg):
		links = list(map(lambda ID: ID.strip()[1:],findall(r"@[\w|_|\d]+", msg))) + list(map(lambda link:link.split("/")[-1],findall(r"rubika\.ir/\w+",msg)))
		joincORjoing = "joing" in msg or "joinc" in msg
	
		if joincORjoing: return joincORjoing
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
			lockTime = f"{h}:{m}"

		def getLockTime(self):
			return lockTime
	
		def checkLockTime(self, guid, accesses=[]):
			if datetime.now().strftime("%H:%M") == lockTime:
				bot.setMembersAccess(guid, accesses)
	
		def checkUnlockTime(self, guid, accesses=["ViewMembers","ViewAdmins","SendMessages","AddMember"]):
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