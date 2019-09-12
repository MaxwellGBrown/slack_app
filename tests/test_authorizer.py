"""Tests for slack_app.authorizer.

Tests in here are built using the example from the slack API documentation:

    https://api.slack.com/docs/verifying-requests-from-slack#step-by-step_walk-through_for_validating_a_request
"""
from hashlib import sha256
import hmac
import time
from unittest.mock import MagicMock

import pytest

from slack_app.authorizer import SlackAuthenticationCheck


TIMESTAMP = 1531420618


@pytest.fixture
def signing_secret():
    """Slack signing secret for the request."""
    return "8f742231b10e8888abcd99yyyzzz85a5"


@pytest.fixture()
def timestamp(monkeypatch):
    """Timestamp associated with the request & adds latency to time.time()."""
    monkeypatch.setattr(time, 'time', lambda: TIMESTAMP)
    return TIMESTAMP


@pytest.fixture()
def event(signing_secret, timestamp):
    """Return request associated with slack authentication example."""
    headers = {
        "X-Slack-Signature": "v0=a2114d57b48eac39b9ad189dd8316235a7b4a8d21a10b"
                             "d27519666489c69b503",
        "X-Slack-Request-Timestamp": str(timestamp),
        "Content-Type": "x-www-form-urlencoded",
    }

    body = "token=xyzz0WbapA4vBCDEFasx0q6G&team_id=T1DC2JH3J&team_domain=tes" \
           "tteamnow&channel_id=G8PSS9T3V&channel_name=foobar&user_id=U2CERL" \
           "KJA&user_name=roadrunner&command=%2Fwebhook-collect&text=&respon" \
           "se_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT1DC2JH3J%2F39" \
           "7700885554%2F96rGlfmibIGlgcZRskXaIFfN&trigger_id=398738663015.47" \
           "445629121.803a0bc887a14d10d2c447fce8b6703c"

    return {"body": body, "headers": headers}


@pytest.fixture()
def context():
    """Lambda event context."""
    return MagicMock(name="context")


def test_SlackAuthenticationCheck_calls_wrapped_fxn(signing_secret,
                                                    event,
                                                    context):
    """Assert SlackAuthenticationCheck() calls the wrapped callable.

    Incoming Command: Assert public side effects.
    """
    lambda_handler = MagicMock()
    authorizer = SlackAuthenticationCheck(signing_secret)
    wrapped_handler = authorizer(lambda_handler)
    wrapped_handler(event, context)

    lambda_handler.assert_called_once_with(event, context)


def test_failed_auth_does_not_call_wrapped(signing_secret, event, context):
    """Assert SlackAuthenticationCheck() calls the wrapped callable.

    Incoming Command: Assert public side effects.
    """
    event["body"] = "hello world"

    lambda_handler = MagicMock()
    authorizer = SlackAuthenticationCheck(signing_secret)
    wrapped_handler = authorizer(lambda_handler)
    wrapped_handler(event, context)

    lambda_handler.assert_not_called()


@pytest.mark.parametrize("headers", [
    # Missing required headers
    {"X-Slack-Signature": None},
    {"X-Slack-Request-Timestamp": None},
    # Mismatching X-Slack-Signature
    {"X-Slack-Signature": "v0=ac86bcd8b786a8b0871323abcbade312f13ad"},
    # Request-Timestamp doesn't match the signed header
    {"X-Slack-Request-Timestamp": f"{TIMESTAMP + 600}"},
])
def test_wrapped_fxn_returns_403_with_missing_or_invalid_headers(
    signing_secret,
    event,
    headers,
    context,
):
    """Tests that the exact slack example returns a 200."""
    event["headers"].update(headers)
    event["headers"] = {
        k: v for k, v in event["headers"].items() if v is not None
    }

    lambda_handler = MagicMock()
    authorizer = SlackAuthenticationCheck(signing_secret)
    wrapped_handler = authorizer(lambda_handler)
    response = wrapped_handler(event, context)

    assert response["statusCode"] == 403


@pytest.mark.parametrize("age_in_seconds", [
    (60 * 5) + 1,
    60 * 10,
    60 * 1000000,
])
def test_SlackAuthenticationCheck_old_request_timestamp(
    age_in_seconds,
    signing_secret,
    timestamp,
    context,
):
    """Assert wrapped function returns 403 if the timestamp is too lod.

    Incoming Query: Assert Response
    """
    body = "hello world"
    request_timestamp = timestamp - age_in_seconds

    raw_signature = f"v0:{request_timestamp}:{body}"
    signature_hmac = hmac.new(signing_secret.encode(), raw_signature.encode(),
                              sha256)
    signature = b"v0=" + signature_hmac.hexdigest().encode()

    event = {
        "body": body,
        "headers": {
            "X-Slack-Signature": signature.decode(),
            "X-Slack-Request-Timestamp": str(request_timestamp),
        },
    }

    lambda_handler = MagicMock()
    authorizer = SlackAuthenticationCheck(signing_secret)
    wrapped_handler = authorizer(lambda_handler)
    response = wrapped_handler(event, context)

    assert response["statusCode"] == 403
