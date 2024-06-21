import os
import base64


def lambda_handler(event, context):
    authorization_header = event["authorizationToken"]

    if not authorization_header:
        return generate_policy("user", "Deny", event["methodArn"])

    encoded_credentials = authorization_header.split(" ")[1]
    try:
        credentials = base64.b64decode(encoded_credentials).decode("ascii")
    except Exception as e:
        return generate_policy("user", "Deny", event["methodArn"])
    username, password = credentials.split(":")

    valid_username = os.getenv("MY_USERNAME")
    valid_password = os.getenv("MY_PASSWORD")

    if username == valid_username and password == valid_password:
        return generate_policy(username, "Allow", event["methodArn"])
    else:
        return generate_policy("user", "Deny", event["methodArn"])


def generate_policy(principal_id, effect, resource):
    auth_response = {}
    auth_response["principalId"] = principal_id

    if effect and resource:
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource,
                },
            ],
        }
        auth_response["policyDocument"] = policy_document

    return auth_response
