from core import TotoroBot

import asyncio

bot = TotoroBot()

if __name__ == "__main__":
    try:
        asyncio.run(bot.startup())
    except KeyboardInterrupt:
        asyncio.run(bot.close())
