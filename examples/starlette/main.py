"""
    examples/starlette/main
    ~~~~~~~~~~~~~~~~~~~~~~~

    Contains simple example using probot + starlette.
"""
from typing import Optional

from starlette import applications
import uvicorn

from probot.api import starlette as probot

app = applications.Starlette()
bot = probot.Probot(app)


@bot.on('repository.created')
async def on_repo_created(ctx: probot.Context) -> Optional[probot.Response]:
    print('repository.created!')
    print(ctx)
    return None


if __name__ == '__main__':
    uvicorn.run('main:app', port=8000)
