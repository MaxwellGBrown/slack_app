"""Slack App using AWS API Gateway Lambda Integration."""
import json
import urllib.parse


def lambda_handler(event, context):
    """Lambda API Gateway endpoint for slack app."""
    parsed_body = urllib.parse.parse_qs(event["body"])
    # query strings can be multiple; just take the first of each found
    request_body = {k: v[0] for k, v in parsed_body.items()}

    return {
        "statusCode": 200,
        "headers": dict(),
        "body": json.dumps(request_body),
    }
