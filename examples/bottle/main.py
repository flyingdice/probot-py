"""
    examples/bottle/main
    ~~~~~~~~~~~~~~~~~~~~

    Contains simple example using probot + bottle.
"""
from typing import Optional

import bottle

from probot.api import bottle as probot


app = bottle.Bottle()
bot = probot.Probot(app)


@bot.on('repository.created')
def on_repo_created(ctx: probot.Context) -> Optional[probot.Response]:
    print('repository.created called!')
    print(ctx)
    return None


if __name__ == '__main__':
    app.run(debug=True, port=8000)
