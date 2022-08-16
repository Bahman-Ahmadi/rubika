from re import findall

class filters:
	me                       = lambda bot, message: message["chat_updates"][-1]["chat"]["last_message"]["is_mine"]
	PV                       = lambda bot, message: message["message_updates"][-1]["type"] == "User"
	bot                      = lambda bot, message: message["message_updates"][-1]["type"] == "Bot"
	group                    = lambda bot, message: message["message_updates"][-1]["type"] == "Group"
	channel                  = lambda bot, message: message["message_updates"][-1]["type"] == "Channel"
	service                  = lambda bot, message: message["message_updates"][-1]["type"] == "Service"

	gif                      = lambda bot, message: message["message_updates"][-1]["message"]["file_inline"]["type"] == "Gif"
	poll                     = lambda bot, message: message["message_updates"][-1]["message"]["type"] == "Poll"
	quiz                     = lambda bot, message: message["message_updates"][-1]["message"]["type"] == "Poll3"
	text                     = lambda bot, message: message["message_updates"][-1]["message"]["type"] == "Text"
	media                    = lambda bot, message: "file_inline" in message["message_updates"][-1]["message"].keys()
	video                    = lambda bot, message: message["message_updates"][-1]["message"]["file_inline"]["type"] == "Video"
	photo                    = lambda bot, message: message["message_updates"][-1]["message"]["file_inline"]["type"] == "Image"
	voice                    = lambda bot, message: message["message_updates"][-1]["message"]["file_inline"]["type"] == "Voice"
	music                    = lambda bot, message: message["message_updates"][-1]["message"]["file_inline"]["type"] == "Music"
	rubino                   = lambda bot, message: message["message_updates"][-1]["message"]["type"] == "RubinoPost"
	sticker                  = lambda bot, message: message["message_updates"][-1]["message"]["type"] == "Sticker"
	document                 = lambda bot, message: message["message_updates"][-1]["message"]["file_inline"]["type"] == "File"

	hasGroupLink             = lambda bot, message: bool(findall(r"rubika.ir/joing/\w{32}", message["message_updates"][-1]["message"]["text"]))
	hasChannelLink           = lambda bot, message: bool(findall(r"rubika.ir/joinc/\w{32}", message["message_updates"][-1]["message"]["text"]))
	hasUsername              = lambda bot, message: any([bot.getInfoByUsername(i.replace("@","")).get("data").get("user") is not None for i in findall(r"@[\w|\d]+", message["message_updates"][-1]["message"]["text"])])

	bold                     = lambda bot, message: any([j["type"] == "Bold" for j in [i for i in message["message_updates"][-1]["message"]["metadata"]]])
	mono                     = lambda bot, message: any([j["type"] == "Mono" for j in [i for i in message["message_updates"][-1]["message"]["metadata"]]])
	italic                   = lambda bot, message: any([j["type"] == "Italic" for j in [i for i in message["message_updates"][-1]["message"]["metadata"]]])
	mention                  = lambda bot, message: any([j["type"] == "Mention" for j in [i for i in message["message_updates"][-1]["message"]["metadata"]]])
	metadata                 = lambda bot, message: "metadata" in message["message_updates"][-1]["message"]

	onMessageSent            = lambda bot, message: message["message_updates"][-1]["action"] == "New"
	onMessageEdited          = lambda bot, message: message["message_updates"][-1]["action"] == "Edit"
	onMessageReplied         = lambda bot, message: "reply_to_message_id" in message["message_updates"][-1]["message"].keys()
	onMessageDeleted         = lambda bot, message: message["message_updates"][-1]["action"] == "Delete"
	onMessageForwarded       = lambda bot, message: "forwarded_from" in message["message_updates"][-1]["message"].keys()
	onMessageForwardedNoLink = lambda bot, message: "forwarded_no_link" in message["message_updates"][-1]["message"].keys()

	event                    = lambda bot, message: message["message_updates"][-1]["message"]["type"] == "Event"
	onMemberAdded            = lambda bot, message: message["message_updates"][-1]["message"]["event_data"]["type"] == "AddedGroupMembers"
	onMemberJoined           = lambda bot, message: message["message_updates"][-1]["message"]["event_data"]["type"] == "JoinedGroupByLink"
	onMemberLeaved           = lambda bot, message: message["message_updates"][-1]["message"]["event_data"]["type"] == "LeaveGroup"
	onMemberRemoved          = lambda bot, message: message["message_updates"][-1]["message"]["event_data"]["type"] == "RemoveGroupMembers"
	onMessagePinned          = lambda bot, message: message["message_updates"][-1]["message"]["event_data"]["type"] == "PinnedMessageUpdated"
	onVoiceChatStarted       = lambda bot, message: message["message_updates"][-1]["message"]["event_data"]["type"] == "VoiceChatFinished"
	onVoiceChatFinished      = lambda bot, message: message["message_updates"][-1]["message"]["event_data"]["type"] == "VoiceChatStarted"

class types: ALL, ANY, INVERT = "all", "any", "invert"