from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def slack_notifier(slack_token, channel_id, message):
    # Initialize the WebClient with the token
    client = WebClient(token=slack_token)

    try:
        # Send a message to Slack
        response = client.chat_postMessage(
            channel=channel_id,
            text=message
        )
        print(f"Message sent successfully: {response['ts']}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
