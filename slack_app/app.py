"""Slack App using AWS API Gateway Lambda Integration."""
import json
import urllib.parse


class SlashCommands:
    """Lambda Handler to register, parse, and route slack slash commands."""

    def __init__(self, slash_commands=None):
        """Take in slash commands by their name."""
        self.commands = slash_commands if slash_commands else dict()

    def __call__(self, event, context):
        """Parse request body & call registerd command."""
        command_body = self._parse_command_body(event["body"])
        command = self.commands.get(command_body["command"], self._command_not_configured)  # noqa

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
                        "text": f"Command `{command_body['command']}` is "
                                "registered in the Slack App, but not "
                                "implemented on the API."
                    },
                }
            ]
        }

    @staticmethod
    def _parse_command_body(request_body):
        parsed_body = urllib.parse.parse_qs(request_body)
        # an empty qs will omit the key on parse, but it's valid to put no text
        parsed_body.setdefault("text", [""])

        # query strings can be multiple; just take the first of each found
        return {k: v[0] for k, v in parsed_body.items()}
