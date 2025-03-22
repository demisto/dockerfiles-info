import os
from slack_sdk import WebClient
from collections.abc import Iterable

def slack_notifier(slack_token, channel_id, removed_images ,added_images, failed_to_inspect_images):

    # removed_images = join_list_by_delimiter_in_chunks(removed_images, delimiter='\n* ')
    # added_images = join_list_by_delimiter_in_chunks(added_images, delimiter='\n* ')

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
            client.chat_postMessage(
                channel=channel_id,
                text='*The following images removed:*',
                thread_ts=message_ts  # Threaded message, using the timestamp of the original message
            )
            
            with open('removed_images.txt', 'w') as f:
                f.write('\n'.join(removed_images))
            
            client.files_upload_v2(
                channel='C04CHML16P8',
                file='removed_images.txt',
                title='Removed images',
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
            client.chat_postMessage(
                channel=channel_id,
                text='*The following images added:*',
                thread_ts=message_ts  # Threaded message, using the timestamp of the original message
            )
            
            with open('added_images.txt', 'w') as f:
                f.write('\n'.join(added_images))
            
            client.files_upload_v2(
                channel='C04CHML16P8',
                file='added_images.txt',
                title='Added images',
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
            client.chat_postMessage(
                channel=channel_id,
                text='*The following images failed to inspect:*',
                thread_ts=message_ts  # Threaded message, using the timestamp of the original message
            )
            
            with open('failed_images.txt', 'w') as f:
                f.write('\n'.join(added_images))
            
            client.files_upload_v2(
                channel='C04CHML16P8',
                file='failed_images.txt',
                title='Failed images',
                thread_ts=message_ts  # Threaded message, using the timestamp of the original message
            )
    



        # if added_images:
        #     added_images_messages = ['*The following images added:*']
        #     added_images_messages.extend(added_images)
        # else:
        #     added_images_messages = ['*No new images has been added*']

        # # replay the new images added message
        # for message in added_images_messages:
        #     client.chat_postMessage(
        #         channel=channel_id,
        #         text=message,
        #         thread_ts=message_ts  # Threaded message, using the timestamp of the original message
        #     )
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")
    finally:
        if os.path.exists('removed_images.txt'):
            os.remove('removed_images.txt')
            
        if os.path.exists('added_images.txt'):
            os.remove('added_images.txt')
            
        if os.path.exists('failed_images.txt'):
            os.remove('failed_images.txt')


def join_list_by_delimiter_in_chunks(list_to_join: Iterable[str], delimiter: str = ", ", max_length: int = 2_000) -> list[str]:
    """
    Join a list of strings into chunks with a given delimiter and maximum length.
    Args:
        list_to_join (list): The list to split.
        delimiter (str): The delimiter to join the chunks.
        max_length (int): The maximum length of each chunk.

    Returns:
        list: The list of chunks.
    """
    chunks = []
    current_chunk = ""
    for item in list_to_join:
        if len(current_chunk) + len(item) + len(delimiter) > max_length:
            chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += f"{delimiter}{item}"
    if current_chunk:
        chunks.append(current_chunk)
    return chunks
