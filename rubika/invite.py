from client import Bot
from time import sleep

bot = Bot("invite",auth="xbiuifzcwcuypxidalxvdmwugkojofjh")

def addAll(first,second,s=0):
    first = bot.getGroupMembers(first)
    print(first)
    for i in first:
        bot.invite(second,[i["member_guid"]])
        sleep(s)

From = input("from-> ")
To = input("to-> ")
andJoin = bool(int(input("join?(0/1)-> ")))
time4sleep = input("sleep(0,1,2,...)-> ") or 0

while True:
    try:
        #ID = input("ID-> ").replace("@","")
        if andJoin and "joing" in From:
            bot.joinGroup(From)
        if andJoin and "joing" in To:
            bot.joinGroup(To)

        fguid,tguid = bot.groupPreviewByJoinLink(From)["group"]["group_guid"], bot.groupPreviewByJoinLink(To)["group"]["group_guid"]
        addAll(fguid,tguid,s=int(time4sleep))
    except Exception as e:
        print(e)
