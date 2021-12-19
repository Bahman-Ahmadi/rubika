<h1>rubika</h1>
<br/>
this is a <b>unofficial</b> library for making bots in rubika
using this library you can make your own rubika bot and control that
those bots that makes with this library, will be run on your account;
so you should get your account's <b>API key</b>.
and another point is it.. you are only allowed to run the bot in one chat at a time.
so you should get chat's <b>GUID</b>.
<hr/>
<h3>introductions</h3>
1. unix or windows system<br/>
2. python 3<br/>
3. libraries :<br/>
- pycryptodome<br/>
- requests<br/>
- urllib3<br/>
- tqdm<br/>
<br/>
<i>note: libraries automatically will be installed when you install rubika library</i>
<hr/>
<h3>install</h3>
enter this command on your command line to install the library
<pre lang="bash">pip install rubika</pre>
<br/>
<i>first introductions will be installed then rubika library</i>
<hr/>
<h3>use</h3>
enter this example code in a file or enter line-to-line in the python3 shell:
<pre lang="py3">
from rubika import Bot

bot = Bot("AUTH-KEY")
target = "CHAT-ID"

bot.sendMessage(target, 'YOUR-MESSAGE')
</pre>
<br/>
as result your message will be sent in the target chat.
<hr/>
<h3>documents</h3>
for reading more about this library, you can visit site:<br/>
🌐 http://rublib.ir
