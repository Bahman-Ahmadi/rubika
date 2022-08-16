<p align="center">
    <a href="https://github.com/bahman-ahmadi/rubika">
        <img src="https://rubikalib.github.io/assets/logo.png" alt="RUBIKA" width="128">
    </a>
    <br>
    <b>Rubika Bot Self Library for Python</b>
    <br>
    <a href="https://rubikalib.github.io">
        Homepage
    </a>
    •
    <a href="https://rubikalib.github.io/docs.html">
        Documentation
    </a>
    •
    <a href="https://t.me/rubikalibGP">
        Community
    </a>
    •
    <a href="https://t.me/rubikalib">
        News
    </a>
</p>

## Rubika

> easy, fast and elegant library for making rubika self bots

``` python
from rubika import Bot, Socket
from rubika.filters import filters

bot = Bot("MyApp")
app = Socket(bot.auth)

@app.handler(filters.PV)
def hello(message):
    message.reply("Hello from Rubikalib!")
```

**Rubika** is an easy, fast and unofficial [rubika](https://rubika.ir) self bot library.
It enables you to easily interact with the main Telegram API through a user account (custom client) using Python.

### Key Features

- **Ready**: Install rubika with pip and start building your applications right away.
- **Easy**: Makes the rubika API simple and intuitive, while still allowing advanced usages.
- **Elegant**: Low-level details are abstracted and re-presented in a more convenient way.
- **Fast**: Boosted up by aiohttp instead of requests.
- **Powerful**: Full access to Rubika's API to execute any official client action and more.

### Installing

``` bash
pip3 install rubika
```

### Thanks For (A-Z)
- Dark Code
- Mr.binder
- Sajjad Dehghani
- Sajjad Soleymani
- Saleh (maven)
- Shayan Ghosi
- And you :)

### Resources

- Check out the docs at https://rubikalib.github.io/docs.html to learn more about rubika library, get started right
away and discover more in-depth material for building your client applications.
- Join the official channel at https://t.me/rubikalib and stay tuned for news, updates and announcements.

### License
rubika library is licensed under [GPLv3 license](https://github.com/bahman-ahmadi/rubika/blob/main/LICENSE)

This is not an official rubika product. It is not affiliated with nor endorsed by rubika Inc.

© 2022 Bahman Ahmadi