"""Slack App deployed on AWS API Gateway & AWS Lambda."""
import os

from .app import App
from .authorizer import SlackAuthenticationCheck


app = App()

SIGNING_SECRET = os.environ.get("SIGNING_SECRET")
app.auth_check = SlackAuthenticationCheck(SIGNING_SECRET)
