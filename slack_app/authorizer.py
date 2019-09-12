"""Authentication checks for Lambda API gateway requests."""
from hashlib import sha256
import hmac
import json
import time


class ForbiddenException(Exception):
    """Request being processed fails Authorization."""


class SlackAuthenticationCheck(object):
    """Check requests against a Slack Signing Secret.

    For details see:
    https://api.slack.com/docs/verifying-requests-from-slack
    """

    required_headers = ("X-Slack-Request-Timestamp", "X-Slack-Signature")

    def __init__(self, signing_secret, *, version="v0", request_leeway=300):
        """Instantiate with the Signing Secret provided by the Slack App.

        :param signing_secret: The Signing Secret of the Slack App sending the
          request
        :param version: The version of the Slack App authentication method
        :param request_leeway: The number of seconds until a request is
          considered stale (and therefor unauthorized) by it's timestamp header
        """
        self.secret = signing_secret
        self.version = version
        self.request_leeway = request_leeway

    def __call__(self, handler):
        """Return a decorated handler that is wrapped by an auth check."""
        def _handler(event, context):
            try:
                self._check(event)
            except ForbiddenException as auth_error:
                return {
                    "statusCode": 403,
                    "headers": dict(),
                    "body": json.dumps(auth_error.args)
                }

            return handler(event, context)
        return _handler

    def _check(self, event):
        """Raise an exception if request is unauthorized."""
        headers = event.get("headers", dict())

        for required_header in self.required_headers:
            if required_header not in headers:
                message = f'missing required header "{required_header}"'
                raise ForbiddenException(message)

        # Check X-Slack-Request-Timestamp
        timestamp = int(headers["X-Slack-Request-Timestamp"])
        if timestamp < (time.time() - self.request_leeway):
            raise ForbiddenException("X-Slack-Request-Timestamp is too old")

        # Check X-Slack-Signature
        raw_signature = f"{self.version}:{timestamp}:{event['body']}"
        signature_hmac = hmac.new(self.secret.encode(), raw_signature.encode(),
                                  sha256)
        signature = f"{self.version}={signature_hmac.hexdigest()}".encode()

        encoded_header = headers["X-Slack-Signature"].encode()

        if not hmac.compare_digest(signature, encoded_header):
            raise ForbiddenException("X-Slack-Signature was invalid")
