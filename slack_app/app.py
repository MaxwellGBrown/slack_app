"""Slack App using AWS API Gateway Lambda Integration."""
import json
import os
# import urllib.parse

from .authorizer import SlackAuthenticationCheck, ForbiddenException


SIGNING_SECRET = os.environ.get("SIGNING_SECRET")
auth_check = SlackAuthenticationCheck(SIGNING_SECRET)


def lambda_handler(event, context, *, auth_check=auth_check):
    """Lambda API Gateway endpoint for slack app."""
    # As of 2019-10-11, there is no way to access the request body in an
    # API Gateway Custom Lambda Authorizer. Thus, authentication here.
    try:
        auth_check(event)
    except ForbiddenException as auth_error:
        return {
            "statusCode": 403,
            "headers": dict(),
            "body": json.dumps(auth_error.args)
        }

    # parsed_body = urllib.parse.parse_qs(event["body"])
    # # query strings can be multiple; just take the first of each found
    # request_body = {k: v[0] for k, v in parsed_body.items()}

    return {
        "statusCode": 200,
        "headers": dict(),
        "body": json.dumps({
            "text": "Hello World",
        }),
    }
