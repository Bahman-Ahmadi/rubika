import re
from re import findall
from rich import print
from threading import Thread
from datetime import datetime

bot = None
socket = None
lockTime = None
unlockTime = None


class Tools:
    def __init__(self, auth):
        from rubika import Bot, Socket
        bot = Bot("", auth=auth)
        socket = Socket(auth)

    def hasInsult(self, msg):
        return any(word in open("dontReadMe.txt").read().split("\n") for word in msg.split())

    def hasAD(self, msg):
        result = False
        links = list(map(lambda ID: ID.strip()[1:], findall(r"@[\w|_|\d]+", msg))) + list(
            map(lambda link: link.split("/")[-1], findall(r"rubika\.ir/\w+", msg)))
        joincORjoing = "joing" in msg or "joinc" in msg

        if joincORjoing:
            result = True
        else:
            for link in links:
                try:
                    Type = bot.getInfoByUsername(
                        link)["data"]["chat"]["abs_object"]["type"]
                    if Type == "Channel":
                        result = True
                except KeyError:
                    result = False

        return result

    def hasSpam(self, messages):
        result, beforeIter = {"isExist": False, "spams": []}, 0
        for Iter in range(0, len(messages)):
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

        def checkUnlockTime(self, guid, accesses=["ViewMembers", "ViewAdmins", "SendMessages", "AddMember"]):
            global lockTime
            if datetime.now().strftime("%H:%M") == lockTime:
                bot.setMembersAccess(guid, accesses)

    def commandHandler(self, message, command, method: callable):
        if message == command:
            method()

    def isJoin(self, user_guid: str, channel_guid: str) -> bool:
        userInfo = bot.getInfo(user_guid)
        haveUserName = 'username' in userInfo.keys()
        def channelMembers(keyword): return bot.getMembers(
            channel_guid, search_text=keyword) if keyword != None else []

        if haveUserName:
            result = [True for i in channelMembers(userInfo.get(
                'username')) if i['member_guid'] == user_guid][0]
        else:
            result = [True for i in channelMembers(userInfo.get(
                'first_name')) if i['member_guid'] == user_guid][0]
            result = [True for i in channelMembers(userInfo.get(
                'last_name')) if i['member_guid'] == user_guid][0]

        return result == True

    # func can be __import__("jdatetime").datetime.fromtimestamp THEN you must install jdatetime using `pip install jdatetime`
    loadTime = lambda timestamp, func=__import__(
        "datetime").datetime.fromtimestamp: func(int(timestamp))

    @staticmethod
    def chatDetection(chat_id: str) -> str:
        return "Group" if chat_id.startswith("g") else "Channel" if chat_id.startswith("c") else "User" if chat_id.startswith("u") else "Bot" if chat_id.startswith("b") else "Service"

    @staticmethod
    def parse(mode, text):
        pattern = r'`(.*)`|\*\*(.*)\*\*|__(.*)__|\[(.*)\]\((\S+)\)'
        conflict = 0
        meta_data_parts = []
        for markdown in re.finditer(pattern, value):
            span = markdown.span()
            if markdown.group(0).startswith('`'):
                value = re.sub(pattern, r'\1', value, count=1)
                meta_data_parts.append(
                    {
                        'type': 'Mono',
                        'from_index': span[0] - conflict,
                        'length': span[1] - span[0] - 2
                    }
                )
                conflict += 2

            elif markdown.group(0).startswith('**'):
                value = re.sub(pattern, r'\2', value, count=1)
                meta_data_parts.append(
                    {
                        'type': 'Bold',
                        'from_index': span[0] - conflict,
                        'length': span[1] - span[0] - 4
                    }
                )
                conflict += 4

            elif markdown.group(0).startswith('__'):
                value = re.sub(pattern, r'\3', value, count=1)
                meta_data_parts.append(
                    {
                        'type': 'Italic',
                        'from_index': span[0] - conflict,
                        'length': span[1] - span[0] - 4
                    }
                )
                conflict += 4

            else:
                value = re.sub(pattern, r'\4', value, count=1)

                mention_text_object_type = 'User'
                mention_text_object_guid = markdown.group(5)
                if mention_text_object_guid.startswith('g'):
                    mention_text_object_type = 'Group'

                elif mention_text_object_guid.startswith('c'):
                    mention_text_object_type = 'Channel'

                meta_data_parts.append(
                    {
                        'type': 'MentionText',
                        'from_index': span[0] - conflict,
                        'length': len(markdown.group(4)),
                        'mention_text_object_guid': mention_text_object_guid,
                        'mention_text_object_type': mention_text_object_type
                    }
                )
                conflict += 4 + len(mention_text_object_guid)

        return dict(realText=value, metadata=dict(meta_data_parts=meta_data_parts))

    @staticmethod
    def getThumbInline(image_bytes: bytes) -> str:
        import io
        import base64
        import PIL.Image
        im, output = PIL.Image.open(io.BytesIO(image_bytes)), io.BytesIO()
        width, height = im.size
        im.save(output, format='PNG')
        im_data = output.getvalue()
        image_data = base64.b64encode(im_data)
        if not isinstance(image_data, str):
            image_data = image_data.decode()
        return image_data

    @staticmethod
    def getImageSize(image_bytes: bytes) -> list:
        import io
        import PIL.Image
        im = PIL.Image.open(io.BytesIO(image_bytes))
        width, height = im.size
        return [width, height]
