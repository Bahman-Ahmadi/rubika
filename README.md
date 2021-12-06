#rubika
this is a **unofficial** library for making bots in rubika
using this library you can make your own0 rubika bot and control that
those bots that makes with this library, will be run on your account;
so you should get your account's **API key**.
and another point is it.. you are only allowed to run the bot in one chat at a time.
so you should get chat's **GUID**.

##introductions
1. unix or windows system
2. python 3
3. libraries :
   - pycryptodome
   - requests
   - urllib3
   - tqdm

*note: libraries automatically will be installed when you install rubika library*


##install
enter this command on your command line to install the library
```bash
pip install rubika
```

*first introductions will be installed then rubika library*


##use
enter this example code in a file or enter line-to-line in the python3 shell:
```py3
from rubika import Bot

bot = Bot("<AUTH-KEY>")
target = "<CHAT-ID>"

bot.sendMessage(target, '<YOUR-MESSAGE>')
```
 as result your message will be sent in the target chat.


##document
for reading more about this library, you can visit site:
🌐 http://rublib.ir
