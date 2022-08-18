from rubika.exceptions import InvalidInput
from rubika.configs import makeData
from rubika.tools import Tools

class DictToClass:
	def __init__(self, message):
		assert type(message) == dict
		[setattr(self, key, [DictToClass(x) if type(x) == dict else x for x in val]) if type(val) in (list, tuple) else setattr(self, key, DictToClass(val) if type(val) == dict else val) for key,val in message.items()]

def ClassToDict(dictToClassObject, result={}):
	for key,val in dictToClassObject.__dict__.items():
		if type(val) not in [DictToClass, dict]: result.setdefault(key, val)
		else:
			if type(val) == DictToClass: result[key] = val.__dict__
			else: result[key] = val
	return result

class Message:
	def __init__(self, auth:str, message:dict, **kwargs):
		self.auth    = auth
		self.chat_id = kwargs.get("chat_id")
		self.bot     = kwargs.get("bot")

		if type(message) != dict:
			try:
				from rubika.client import Bot
				self.bot = self.bot or Bot("", self.auth)
				message = self.bot.getMessagesInfo(self.chat_id, [str(message)])[0]
			except IndexError:
				raise InvalidInput("the auth/entered message id/chat id is incorrect")

		self.data = DictToClass(message)

	def edit(self, newText:str, metadata:list = [], parseMode:str = None) -> dict:
		return self.bot.editMessage(self.data.message_id, self.chat_id, newText, metadata, parseMode)

	def forward(self, to:str) -> dict:
		return self.bot.forwardMessages(self.chat_id, [str(self.data.message_id)], to)

	def getInfo(self) -> dict:
		return self.bot.getMessagesInfo(self.chat_id, [str(self.data.message_id)])[0]

	def getPollStatus(self) -> dict:
		return self.bot.getPollStatus(self.data.message.poll_id)

	def getPollOptionVoters(self, option_index:int, start_id=None):
		return self.bot.getPollOptionVoters(self.data.message.poll_id, int(option_index), start_id)

	def show(self) -> dict:
		try:
			from rich import print as Print
			Print(ClassToDict(self.data))
		except MoudleNotFoundError:
			print(ClassToDict(self.data))

	def reply(self, text:str, metadata:list=[], parseMode:str=None) -> dict:
		return self.bot.sendMessage(self.chat_id, str(text), metadata, parseMode, message_id=self.data.message_id)

	def reply_photo(self, photo:str, caption:str=None, metadata:list=[], parseMode:str=None, thumbnail:str=None, size:list=[], uresponse:list=None) -> dict:
		return self.bot.sendPhoto(self.chat_id, photo, size, thumbnail, metadata, parseMode, caption, message_id=self.data.message_id, uresponse=uresponse)

	def reply_video(self, video:str, caption:str=None, metadata:list=[], parseMode:str=None, thumbnail:str=None, size:list=[], uresponse:list=None) -> dict:
		return self.bot.sendVideo(self.chat_id, video, metadata, parseMode, caption, message_id=self.data.message_id, uresponse=uresponse)

	def reply_music(self, music:str, caption:str=None, metadata:list=[], parseMode:str=None, uresponse:list=None) -> dict:
		return self.bot.sendMusic(self.chat_id, music, metadata, parseMode, caption, message_id=self.data.message_id, uresponse=uresponse)

	def reply_voice(self, voice:str, caption:str, time:int=None, metadata:list=[], parseMode:str=None, uresponse:list=None) -> dict:
		return self.bot.sendVoice(self.chat_id, voice, time, metadata, parseMode, caption, message_id=self.data.message_id, uresponse=uresponse)

	def reply_document(self, file:str, caption:str, metadata:list=[], parseMode:str=None, uresponse:list=None) -> dict:
		return self.bot.sendDocument(self.chat_id, file, caption, metadata, parseMode, message_id=self.data.message_id, uresponse=uresponse)

	def reply_location(self, x:float, y:float) -> dict:
		return self.bot.sendLocation(self.chat_id, [x,y], message_id=self.data.message_id)

	def reply_gif(self, video:str, caption:str, width:int, height:int, time:int=None, metadata:list=[], parseMode:str=None, thumbnail:str=None, uresponse:list=None) -> dict:
		return self.bot.sendGIF(self.chat_id, video, width, height, time, metadata, parseMode, thumbnail, caption, message_id=self.data.message_id, uresponse=uresponse)

	def delete(self, *args) -> dict:
		#args can set for delete other message (out of current message)
		return self.bot.deleteMessages(self.chat_id, [str(self.data.message_id), *args])

	def ban(self) -> dict:
		return self.bot.banMember(self.chat_id, self.data.author_object_guid)

	def block(self) -> dict:
		return self.bot.block(self.data.author_object_guid)

	def unblock(self) -> dict:
		return self.bot.unblock(self.data.author_object_guid)

	def download(self, saveAs:str=None) -> bytes :
		return self.bot.download(self.chat_id, self.data.message_id, saveAs=saveAs)