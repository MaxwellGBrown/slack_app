"""Slack App deployed on AWS API Gateway & AWS Lambda."""
import os

from .app import App
from .authorizer import SlackAuthenticationCheck


app = App()

SIGNING_SECRET = os.environ.get("SIGNING_SECRET")
app.auth_check = SlackAuthenticationCheck(SIGNING_SECRET)

app.slash_command(
    "slack_app",
    lambda x: {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hello World",
                },
            },
        ]
    }
)
app.slash_command(
    "foo",
    lambda x: {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Foo Bar",
                },
            },
        ]
    }
)
