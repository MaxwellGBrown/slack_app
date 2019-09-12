"""Slack App deployed on AWS API Gateway & AWS Lambda."""
import os

from .app import SlashCommands
from .authorizer import SlackAuthenticationCheck


SIGNING_SECRET = os.environ.get("SIGNING_SECRET")
authorizer = SlackAuthenticationCheck(SIGNING_SECRET)

slash_commands = {
    "/slack_app": lambda x: {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hello World",
                },
            },
        ]
    },
    "/foo": lambda x: {
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
}

slash_commands = authorizer(SlashCommands(slash_commands))
