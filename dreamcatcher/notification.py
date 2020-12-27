import attr
import boto3
import ratelimit
import textwrap


_AWS_SNS_CLIENT = boto3.client(
    "sns",
    aws_access_key_id="AWS_ACCESS_KEY_ID",
    aws_secret_access_key="AWS_SECRET_ACCESS_KEY",
    region_name="REGION_NAME",
)
_AWS_SNS_TOPIC = "AWS_SNS_TOPIC"

AWS_SNS_LIMIT = 2
AWS_SNS_COOLDOWN = 900


@ratelimit.limits(calls=2, period=60)
def send_notification(results, category):
    [_AWS_SNS_CLIENT.publish(
        TopicArn=_AWS_SNS_TOPIC,
        Subject="New Listing",
        Message=str(result)
    ) for result in results]
