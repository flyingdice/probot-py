"""
    examples/aiohttp/main
    ~~~~~~~~~~~~~~~~~~~~~

    Contains simple example using probot + aiohttp.
"""
from typing import Optional

from aiohttp import web

from probot.api import aiohttp as probot

app = web.Application()
bot = probot.Probot(app)


@bot.on('repository.created')
async def on_repo_created(ctx: probot.Context) -> Optional[probot.Response]:
    print('repository.created!')
    print(ctx)
    return None


if __name__ == '__main__':
    web.run_app(app, port=8000)
