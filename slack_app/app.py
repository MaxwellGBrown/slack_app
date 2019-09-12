"""Slack App using AWS API Gateway Lambda Integration."""
import json
import urllib.parse

from .authorizer import ForbiddenException


class App:
    """Configurable application to handle API Gateway lambda events."""

    def __init__(self):
        """Instantiate with configurable options."""
        self.auth_check = lambda x: None
        self._commands = dict()

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

        command_name = event["pathParameters"]["command_name"]
        command_body = self._parse_command_body(event["body"])
        command = self._commands.get(command_name, self._command_not_configured)  # noqa
        response_body = command(command_body)

        return {
            "statusCode": 200,
            "headers": dict(),
            "body": json.dumps(response_body),
        }

    @staticmethod
    def _command_not_configured(command_body):
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Command `/{command_body['command']}` is "
                                "not implemented."
                    },
                }
            ]
        }

    @staticmethod
    def _parse_command_body(request_body):
        parsed_body = urllib.parse.parse_qs(request_body)
        # query strings can be multiple; just take the first of each found
        return {k: v[0] for k, v in parsed_body.items()}

    def slash_command(self, command_name, command):
        """Register a command to be called."""
        self._commands[command_name] = command
