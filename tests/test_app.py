"""Tests for complaint_counter.py."""
from hashlib import sha256
import hmac
import json
import time
from unittest.mock import Mock
from urllib.parse import urlencode

from slack_app.app import SlashCommands


def slash_command_event(body=None, headers=None, *, secret=None, timestamp=None):  # noqa
    """Construct an event that resembles a slack slash command.

    To specify the lack of a default header, specify None as it's value.
    """
    body = body if body else dict()
    headers = headers if headers else dict()
    timestamp = timestamp if timestamp else int(time.time())
    secret = secret if secret else "8f742231b10e8888abcd99yyyzzz85a5"

    body.setdefault("token", "ftMJyTJlA4qo8QNY3PVhuYf6")
    body.setdefault("team_id", "T18UTUL93")
    body.setdefault("team_domain", "test_domain")
    body.setdefault("channel_id", "D81P2TLNM")
    body.setdefault("channel_name", "directmessage")
    body.setdefault("user_id", "U81JYT64Q")
    body.setdefault("user_name", "test_user")
    body.setdefault("command", "/test")
    body.setdefault("text", "")
    body.setdefault(
        "response_url",
        "https://hooks.slack.com/commands/T18UTUL93/440741347573"
        "/RSYHp7T18s0uP4eU7hGFdSm6",
    )

    # remove None values
    body = {k: v for k, v in body.items() if v is not None}

    urlencoded_body = urlencode(body)

    headers.setdefault("X-Slack-Request-Timestamp", timestamp)
    headers.setdefault("Content-Type", "application/x-www-form-urlencoded")

    raw_signature = f"v0:{timestamp}:{urlencoded_body}"
    signature_hmac = hmac.new(secret.encode(), raw_signature.encode(), sha256)
    signature = b"v0=" + signature_hmac.hexdigest().encode()

    headers.setdefault("X-Slack-Signature", signature.decode())

    # remove None values
    headers = {k: v for k, v in headers.items() if v is not None}

    _leading_slash, command_name = body["command"].split("/")
    event = {
        "body": urlencoded_body,
        "headers": headers,
        "requestContext": {"resourcePath": f"/slash_command"},
        "path": f"/slash_command",
        "resource": f"/slash_command",
        "httpMethod": "POST",
    }
    return event, body


def test_SlashCommands_calls_registered_command():
    """Assert registered command gets called.

    Outgoing Command: Assert command sent
    """
    slash_commands = SlashCommands()
    command = Mock(return_value=dict())
    slash_commands.commands["/foo"] = command

    event, raw_body = slash_command_event({"command": "/foo"})
    slash_commands(event, None)

    command.assert_called_once_with(raw_body)


def test_SlashCommands_use_command_response_as_json_body():
    """Assert response from registered commands is json dumped as body.

    Incoming Query: Assert response.
    """
    slash_commands = SlashCommands()
    command = Mock(return_value={"hello": "world"})
    slash_commands.commands["/foo"] = command

    event, raw_body = slash_command_event({"command": "/foo"})
    response = slash_commands(event, None)

    assert response["statusCode"] == 200
    assert response["body"] == json.dumps({"hello": "world"})


def test_SlashCommands_returns_misconfiguration_message():
    """Assert commands that aren't registered return a 200 message.

    Incoming Query: Assert response.
    """
    slash_commands = SlashCommands()
    event, raw_body = slash_command_event({"command": "/broken"})
    response = slash_commands(event, None)

    assert response["statusCode"] == 200
    assert response["body"] == json.dumps({
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Command `/broken` is registered in the Slack App,"
                            " but not implemented on the API."
                },
            }
        ]
    })
