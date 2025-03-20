from slack_sdk import WebClient
from collections.abc import Iterable

def slack_notifier(slack_token, channel_id, removed_images ,added_images):

    removed_images = join_list_by_delimiter_in_chunks(removed_images, delimiter='\n* ')
    added_images = join_list_by_delimiter_in_chunks(added_images, delimiter='\n* ')

    # Initialize the WebClient with the token
    client = WebClient(token=slack_token)

    try:
        # send a message to Slack
        response = client.chat_postMessage(
            channel=channel_id,
            text='Update `dockerfiles-info` - Success'
        )

        message_ts = response['ts']
        print(f"Message sent successfully: {response['ts']}")

        if removed_images:
            removed_images_messages = ['*The following images removed:*']
            removed_images_messages.extend(removed_images)
        else:
            removed_images_messages = ['*No old images has been removed*']

        # replay the old images removed message
        for message in removed_images_messages:
            client.chat_postMessage(
            channel=channel_id,
            text=message,
            thread_ts=message_ts  # Threaded message, using the timestamp of the original message
            )

        if added_images:
            added_images_messages = ['*The following images added:*']
            added_images_messages.extend(added_images)
        else:
            added_images_messages = ['*No new images has been added*']

        # replay the old images removed message
        for message in added_images_messages:
            client.chat_postMessage(
                channel=channel_id,
                text=message,
                thread_ts=message_ts  # Threaded message, using the timestamp of the original message
            )
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")


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
        current_chunk += f"{item}{delimiter}"
    if current_chunk:
        chunks.append(current_chunk)
    return chunks
