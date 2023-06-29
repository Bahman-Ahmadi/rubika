from re import findall


class filters:
    @staticmethod
    def me(bot, message): return message["chat_updates"][-1]["chat"]["last_message"]["is_mine"]

    @staticmethod
    def PV(bot, message): return message["message_updates"][-1]["type"] == "User"

    @staticmethod
    def bot(bot, message): return message["message_updates"][-1]["type"] == "Bot"

    @staticmethod
    def group(bot, message): return message["message_updates"][-1]["type"] == "Group"

    @staticmethod
    def channel(bot, message): return message["message_updates"][-1]["type"] == "Channel"

    @staticmethod
    def service(bot, message): return message["message_updates"][-1]["type"] == "Service"

    @staticmethod
    def gif(bot, message): return message["message_updates"][-1]["message"]["file_inline"]["type"] == "Gif"

    @staticmethod
    def poll(bot, message): return message["message_updates"][-1]["message"]["type"] == "Poll"

    @staticmethod
    def quiz(bot, message): return message["message_updates"][-1]["message"]["type"] == "Poll3"

    @staticmethod
    def text(bot, message): return message["message_updates"][-1]["message"]["type"] == "Text"

    @staticmethod
    def media(bot, message): return "file_inline" in message["message_updates"][-1]["message"].keys()

    @staticmethod
    def video(bot, message): return message["message_updates"][-1]["message"]["file_inline"]["type"] == "Video"

    @staticmethod
    def photo(bot, message): return message["message_updates"][-1]["message"]["file_inline"]["type"] == "Image"

    @staticmethod
    def voice(bot, message): return message["message_updates"][-1]["message"]["file_inline"]["type"] == "Voice"

    @staticmethod
    def music(bot, message): return message["message_updates"][-1]["message"]["file_inline"]["type"] == "Music"

    @staticmethod
    def rubino(bot, message): return message["message_updates"][-1]["message"]["type"] == "RubinoPost"

    @staticmethod
    def sticker(bot, message): return message["message_updates"][-1]["message"]["type"] == "Sticker"

    @staticmethod
    def document(bot, message): return message["message_updates"][-1]["message"]["file_inline"]["type"] == "File"

    @staticmethod
    def hasGroupLink(bot, message): return bool(findall(r"rubika.ir/joing/\w{32}", message["message_updates"][-1]["message"]["text"]))

    @staticmethod
    def hasChannelLink(bot, message): return bool(findall(r"rubika.ir/joinc/\w{32}", message["message_updates"][-1]["message"]["text"]))

    @staticmethod
    def hasUsername(bot, message): return any([bot.getInfoByUsername(i.replace("@", "")).get("data").get("user") is not None for i in findall(r"@[\w|\d]+", message["message_updates"][-1]["message"]["text"])])

    @staticmethod
    def bold(bot, message): return any([j["type"] == "Bold" for j in [i for i in message["message_updates"][-1]["message"]["metadata"]]])

    @staticmethod
    def mono(bot, message): return any([j["type"] == "Mono" for j in [i for i in message["message_updates"][-1]["message"]["metadata"]]])

    @staticmethod
    def italic(bot, message): return any([j["type"] == "Italic" for j in [i for i in message["message_updates"][-1]["message"]["metadata"]]])

    @staticmethod
    def mention(bot, message): return any([j["type"] == "Mention" for j in [i for i in message["message_updates"][-1]["message"]["metadata"]]])

    @staticmethod
    def metadata(bot, message): return "metadata" in message["message_updates"][-1]["message"]

    @staticmethod
    def onMessageSent(bot, message): return message["message_updates"][-1]["action"] == "New"

    @staticmethod
    def onMessageEdited(bot, message): return message["message_updates"][-1]["action"] == "Edit"

    @staticmethod
    def onMessageReplied(bot, message): return "reply_to_message_id" in message["message_updates"][-1]["message"].keys()

    @staticmethod
    def onMessageDeleted(bot, message): return message["message_updates"][-1]["action"] == "Delete"

    @staticmethod
    def onMessageForwarded(bot, message): return "forwarded_from" in message["message_updates"][-1]["message"].keys()

    @staticmethod
    def onMessageForwardedNoLink(bot, message): return "forwarded_no_link" in message["message_updates"][-1]["message"].keys()

    @staticmethod
    def event(bot, message): return message["message_updates"][-1]["message"]["type"] == "Event"

    @staticmethod
    def onMemberAdded(bot, message): return message["message_updates"][-1]["message"]["event_data"]["type"] == "AddedGroupMembers"

    @staticmethod
    def onMemberJoined(bot, message): return message["message_updates"][-1]["message"]["event_data"]["type"] == "JoinedGroupByLink"

    @staticmethod
    def onMemberLeaved(bot, message): return message["message_updates"][-1]["message"]["event_data"]["type"] == "LeaveGroup"

    @staticmethod
    def onMemberRemoved(bot, message): return message["message_updates"][-1]["message"]["event_data"]["type"] == "RemoveGroupMembers"

    @staticmethod
    def onMessagePinned(bot, message): return message["message_updates"][-1]["message"]["event_data"]["type"] == "PinnedMessageUpdated"

    @staticmethod
    def onVoiceChatStarted(bot, message): return message["message_updates"][-1]["message"]["event_data"]["type"] == "VoiceChatFinished"

    @staticmethod
    def onVoiceChatFinished(bot, message): return message["message_updates"][-1]["message"]["event_data"]["type"] == "VoiceChatStarted"

class types:
    ALL, ANY, INVERT = "all", "any", "invert"
