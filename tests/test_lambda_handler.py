"""Tests for complaint_counter.py."""
from hashlib import sha256
import hmac
import os
import time
from unittest.mock import Mock
from urllib.parse import urlencode

import pytest

from slack_app.app import lambda_handler


def make_request(body=None, headers=None, *, secret=None, timestamp=None):
    """Create a request that resembles a slack-API request.

    By default, this function returns a valid request that should result in a
    200 OK.

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

    raw_signature = f"v0:{timestamp}:{urlencoded_body}"
    signature_hmac = hmac.new(secret.encode(), raw_signature.encode(), sha256)
    signature = b"v0=" + signature_hmac.hexdigest().encode()

    headers.setdefault("X-Slack-Signature", signature.decode())

    # remove None values
    headers = {k: v for k, v in headers.items() if v is not None}

    return {
        "body": urlencoded_body,
        "headers": headers,
    }


@pytest.fixture(autouse=True)
def environment_variables(monkeypatch):
    """Set environment variables to be expected by the AWS Lambda handler."""
    environment = {"SIGNING_SECRET": "8f742231b10e8888abcd99yyyzzz85a5"}
    monkeypatch.setattr(os, 'environ', environment)


@pytest.fixture
def auth_check():
    """Mock out and return an auth check to be injected into lambda_handler."""
    auth_check = Mock()
    auth_check.return_value = None  # by default, do nothing
    return auth_check


def test_lambda_handler_returns_200(auth_check):
    """Test that lambda_handler returns a 200 status code."""
    request = make_request()
    response = lambda_handler(request, None, auth_check=auth_check)
    assert response['statusCode'] == 200
