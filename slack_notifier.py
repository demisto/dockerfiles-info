from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def slack_notifier(slack_token, channel_id, removed_images ,added_images):
    removed_images_msg = f'The following images removed: \n {"\n".join(removed_images)}' if removed_images else 'No old images has been removed'
    added_images_msg = f'The following images added: \n {"\n".join(added_images)}' if added_images else 'No new images has been added'
    
    # Initialize the WebClient with the token
    client = WebClient(token=slack_token)

    try:
        # Send a message to Slack
        response = client.chat_postMessage(
            channel=channel_id,
            text='Update `dockerfiles-info` - Success'
        )

        message_ts = response['ts']
        print(f"Message sent successfully: {response['ts']}")
        
        # replay the old images removed message
        client.chat_postMessage(
        channel=channel_id,
        text=removed_images_msg,
        thread_ts=message_ts  # Threaded message, using the timestamp of the original message
        )


        # replay the new images removed message
        client.chat_postMessage(
        channel=channel_id,
        text=added_images_msg,
        thread_ts=message_ts  # Threaded message, using the timestamp of the original message
        )
        
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")
