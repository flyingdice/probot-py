"""
    examples/fastapi/main
    ~~~~~~~~~~~~~~~~~~~~~

    Contains simple example using probot + fastapi.
"""
from typing import Optional

import fastapi
import uvicorn

from probot.api import fastapi as probot

app = fastapi.FastAPI()
bot = probot.Probot(app)


@bot.on('repository.created')
async def on_repo_created(ctx: probot.Context) -> Optional[probot.Response]:
    print('repository.created!')
    print(ctx)
    return None


if __name__ == '__main__':
    uvicorn.run('main:app', port=8000)
