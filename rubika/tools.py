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
    def chatDetection(chat_id:str) -> str:
        return "Group" if chat_id.startswith("g") else "Channel" if chat_id.startswith("c") else "User" if chat_id.startswith("u") else "Bot" if chat_id.startswith("b") else "Service"

    @staticmethod
    def parse(mode, text):
        results = []
        
        replaces = ["**", "__", "`", "[", "]", "(", ")", "~~", "--"] if mode.lower() == "markdown" else ["<b>", "<i>", "<pre>", "<s>", "<u>", "<link href='", "<a href='", "'>", "</a>", "</link>", "</u>", "</s>", "</pre>", "</i>", "</b>"] # the symbols
        realText = text
        for i in replaces:
            if i in text: realText = realText.replace(i, '')
        bolds    = findall(r"\*\*(.*?)\*\*",text) if mode.lower() == "markdown" else findall("<b>(.*?)</b>",text)
        italics  = findall(r"\_\_(.*?)\_\_",text) if mode.lower() == "markdown" else findall("<i>(.*?)</i>",text)
        monos    = findall(r"\`(.*?)\`",text) if mode.lower() == "markdown" else findall("<pre>(.*?)</pre>",text)
        strikes  = findall(r"\~\~(.*?)\~\~",text) if mode.lower() == "markdown" else findall("<s>(.*?)</s>",text)
        unders   = findall(r"\-\-(.*?)\-\-",text) if mode.lower() == "markdown" else findall("<u>(.*?)</u>",text)
        Mentions = findall(r"\[(.*?)\]\((.*?)\)", text) if mode.lower() == "markdown" else findall("<a href='(.*?)'>(.*?)</a>", text)

        bResult = [realText.index(i) for i in bolds]
        iResult = [realText.index(i) for i in italics]
        mResult = [realText.index(i) for i in monos]
        sResult = [realText.index(i) for i in strikes]
        uResult = [realText.index(i) for i in unders]

        for m in Mentions: realText = realText.replace(m[0], "") # removing guids & links from orginal text
        MResult = [realText.index(i[1]) for i in Mentions]
        
        for indexes,words,Types in ((bResult, bolds, ["Bold"]*len(bolds)), (iResult, italics, ["Italic"]*len(italics)), (mResult, monos, ["Mono"]*len(monos)), (sResult, strikes, ["Strike"]), (uResult, unders, ["Underline"]), (MResult, Mentions, ["MentionText"]*len(Mentions))):
            if indexes != [] and words != []:
                for index, word, Type in zip(indexes, words, Types):
                    result = {"from_index": index,"length": len(word if Type != "MentionText" else word[1]),"type": Type}
                    if Type == "MentionText":
                        if word[0].startswith('http'): result["type"], result["link"] = "Link", {"hyperlink_data": {"url": word[0]}, "type": "hyperlink"}
                        else: result["mention_text_object_guid"], result["mention_text_object_type"] = word[0], Tools.chatDetection(word[0])
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