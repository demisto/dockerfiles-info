import os
from slack_sdk import WebClient

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
            with open('removed_images.txt', 'w') as f:
                f.write('\n'.join(removed_images))
            
            client.files_upload_v2(
                channel=channel_id,
                file='removed_images.txt',
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
            with open('added_images.txt', 'w') as f:
                f.write('\n'.join(added_images))
            
            client.files_upload_v2(
                channel=channel_id,
                file='added_images.txt',
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
            with open('failed_images.txt', 'w') as f:
                f.write('\n'.join(failed_to_inspect_images))
            
            client.files_upload_v2(
                channel=channel_id,
                file='failed_images.txt',
                title='Failed images',
                text='*The following images failed to inspect:*',
                thread_ts=message_ts  # Threaded message, using the timestamp of the original message
            )

    except Exception as e:
        print(f"Error sending message: {str(e)}")
    finally:
        if os.path.exists('removed_images.txt'):
            os.remove('removed_images.txt')
            
        if os.path.exists('added_images.txt'):
            os.remove('added_images.txt')
            
        if os.path.exists('failed_images.txt'):
            os.remove('failed_images.txt')
