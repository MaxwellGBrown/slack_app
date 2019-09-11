"""Slack App using AWS API Gateway Lambda Integration."""
import json

from .authorizer import ForbiddenException


class App:
    """Configurable application to handle API Gateway lambda events."""

    def __init__(self):
        """Instantiate with configurable options."""
        self.auth_check = lambda x: None

    def __call__(self, event, context):
        """Handle event and return API Gateway response."""
        # As of 2019-10-11, there is no way to access the request body in an
        # API Gateway Custom Lambda Authorizer. Thus, authentication here.
        try:
            self.auth_check(event)
        except ForbiddenException as auth_error:
            return {
                "statusCode": 403,
                "headers": dict(),
                "body": json.dumps(auth_error.args)
            }

        return {
            "statusCode": 200,
            "headers": dict(),
            "body": json.dumps({
                "text": "Hello World",
            }),
        }
