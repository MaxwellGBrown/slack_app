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
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Hello, Assistant to the Regional Manager"
                                    " Dwight! *Michael Scott* wants to know "
                                    "where you'd like to take the Paper "
                                    "Company investors to dinner tonight.\n\n "
                                    "*Please select a restaurant:*"
                        }
                    },
                    {"type": "divider"},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Farmhouse Thai Cuisine*\n"
                                    ":star::star::star::star: 1528 reviews\n"
                                    "They do have some vegan options, like the"
                                    " roti and curry, plus they have a ton of "
                                    "salad stuff and noodles can be ordered "
                                    "without meat!! They have something for "
                                    "everyone here"
                        },
                        "accessory": {
                            "type": "image",
                            "image_url": "https://s3-media3.fl.yelpcdn.com"
                                         "/bphoto/c7ed05m9lC2EmA3Aruue7A"
                                         "/o.jpg",
                            "alt_text": "alt text for image",
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Kin Khao*\n:star::star::star::star: "
                                    "1638 reviews\n The sticky rice also goes"
                                    " wonderfully with the caramelized pork "
                                    "belly, which is absolutely "
                                    "melt-in-your-mouth and so soft."
                        },
                        "accessory": {
                            "type": "image",
                            "image_url": "https://s3-media2.fl.yelpcdn.com"
                                         "/bphoto/korel-1YjNtFtJlMTaC26A"
                                         "/o.jpg",
                            "alt_text": "alt text for image"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Ler Ros*\n:star::star::star::star: "
                                    "2082 reviews\n I would really recommend "
                                    "the  Yum Koh Moo Yang - Spicy lime "
                                    "dressing and roasted quick marinated pork"
                                    " shoulder, basil leaves, chili "
                                    "& rice powder."
                        },
                        "accessory": {
                            "type": "image",
                            "image_url": "https://s3-media2.fl.yelpcdn.com"
                                         "/bphoto/DawwNigKJ2ckPeDeDM7jAg"
                                         "/o.jpg",
                            "alt_text": "alt text for image"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Farmhouse",
                                    "emoji": True
                                },
                                "value": "click_me_123"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Kin Khao",
                                    "emoji": True
                                },
                                "value": "click_me_123"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Ler Ros",
                                    "emoji": True
                                },
                                "value": "click_me_123"
                            }
                        ]
                    }
                ]
            }),
        }
