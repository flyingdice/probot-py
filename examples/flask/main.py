"""
    examples/flask/main
    ~~~~~~~~~~~~~~~~~~~

    Contains simple example using probot + flask.
"""
from typing import Optional

import flask

from probot.api import flask as probot


app = flask.Flask(__name__)
bot = probot.Probot(app)


@bot.on('repository.created')
def on_repo_created(ctx: probot.Context) -> Optional[probot.Response]:
    print('repository.created!')
    print(ctx)
    return None


if __name__ == '__main__':
    app.run(debug=True, port=8000)
