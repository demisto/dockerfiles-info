import os
from slack_sdk import WebClient

REMOVED_IMAGES_FILE_NAME = "removed_images.txt"
ADDED_IMAGES_FILE_NAME = "added_images.txt"
FAILED_IMAGE_FILE_NAME = "failed_images.txt"

def slack_notifier(slack_token, channel_id, removed_images ,added_images, failed_to_inspect_images):
    # Initialize the WebClient with the token
    client = WebClient(token=slack_token)

    try:
        # send a message to Slack
        response = client.chat_postMessage(
            channel=channel_id,
            text='Update `dockerfiles-info` finished'
        )

        message_ts = response['ts']
        print(f"Message sent successfully: {response['ts']}")

        # replay the old images removed message
        if removed_images:
            with open(REMOVED_IMAGES_FILE_NAME, 'w') as f:
                f.write('\n'.join(removed_images))
            
            client.files_upload_v2(
                channel=channel_id,
                file=REMOVED_IMAGES_FILE_NAME,
                title='Removed images',
                text='*The following images removed:*',
                thread_ts=message_ts  # Threaded message, using the timestamp of the original message
            )
    
        else:
            client.chat_postMessage(
                channel=channel_id,
                text='*No old images has been removed*',
                thread_ts=message_ts  # Threaded message, using the timestamp of the original message
            )

        # replay the new images added message
        if added_images:
            with open(ADDED_IMAGES_FILE_NAME, 'w') as f:
                f.write('\n'.join(added_images))
            
            client.files_upload_v2(
                channel=channel_id,
                file=ADDED_IMAGES_FILE_NAME,
                title='Added images',
                text='*The following images added:*',
                thread_ts=message_ts  # Threaded message, using the timestamp of the original message
            )
    
        else:
            client.chat_postMessage(
                channel=channel_id,
                text='*No new images has been added*',
                thread_ts=message_ts  # Threaded message, using the timestamp of the original message
            )

        # replay failed to inspect images
        if failed_to_inspect_images:
            with open(FAILED_IMAGE_FILE_NAME, 'w') as f:
                f.write('\n'.join(failed_to_inspect_images))
            
            client.files_upload_v2(
                channel=channel_id,
                file=FAILED_IMAGE_FILE_NAME,
                title='Failed images',
                text='*The following images failed to inspect:*',
                thread_ts=message_ts  # Threaded message, using the timestamp of the original message
            )

    except Exception as e:
        print(f"Error sending message: {str(e)}")
    finally:
        if os.path.exists(REMOVED_IMAGES_FILE_NAME):
            os.remove(REMOVED_IMAGES_FILE_NAME)
            
        if os.path.exists(ADDED_IMAGES_FILE_NAME):
            os.remove(ADDED_IMAGES_FILE_NAME)
            
        if os.path.exists(FAILED_IMAGE_FILE_NAME):
            os.remove(FAILED_IMAGE_FILE_NAME)
