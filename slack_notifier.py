from __future__ import annotations

import os
from dataclasses import dataclass, field

from slack_sdk import WebClient

REMOVED_IMAGES_FILE_NAME = "removed_images.txt"
ADDED_IMAGES_FILE_NAME = "added_images.txt"
FAILED_IMAGE_FILE_NAME = "failed_images.txt"
LIST_ADDED_IMAGES_FILE_NAME = "docker_images_list_added.txt"
LIST_REMOVED_IMAGES_FILE_NAME = "docker_images_list_removed.txt"


@dataclass(frozen=True)
class ImageReport:
    """A single group of images reported as a threaded Slack reply.

    When ``images`` is non-empty the names are written to ``file_name`` and
    uploaded with ``title``/``text``. When it is empty, ``empty_text`` is posted
    instead - or nothing at all if ``empty_text`` is None.
    """

    images: list[str] = field(default_factory=list)
    file_name: str = ""
    title: str = ""
    text: str = ""
    empty_text: str | None = None


def _post_report(client, channel_id, thread_ts, report):
    """Upload the report's images as a threaded file, or post its empty message."""
    if report.images:
        with open(report.file_name, 'w') as f:
            f.write('\n'.join(report.images))

        client.files_upload_v2(
            channel=channel_id,
            file=report.file_name,
            title=report.title,
            text=report.text,
            thread_ts=thread_ts,  # Threaded message, using the timestamp of the original message
        )
    elif report.empty_text:
        client.chat_postMessage(
            channel=channel_id,
            text=report.empty_text,
            thread_ts=thread_ts,  # Threaded message, using the timestamp of the original message
        )


def slack_notifier(
    slack_token,
    channel_id,
    removed_images,
    added_images,
    failed_to_inspect_images,
    list_added_images=None,
    list_removed_images=None,
):
    # Initialize the WebClient with the token
    client = WebClient(token=slack_token)

    list_added_images = list_added_images or []
    list_removed_images = list_removed_images or []

    reports = (
        ImageReport(
            images=removed_images,
            file_name=REMOVED_IMAGES_FILE_NAME,
            title='Removed images',
            text='*The following images removed:*',
            empty_text='*No old images has been removed*',
        ),
        ImageReport(
            images=added_images,
            file_name=ADDED_IMAGES_FILE_NAME,
            title='Added images',
            text='*The following images added:*',
            empty_text='*No new images has been added*',
        ),
        ImageReport(
            images=list_added_images,
            file_name=LIST_ADDED_IMAGES_FILE_NAME,
            title='Added images (docker_images_list.json)',
            text='*The following images were added to `docker_images_list.json`:*',
            empty_text='*No new images has been added to `docker_images_list.json`*',
        ),
        ImageReport(
            images=list_removed_images,
            file_name=LIST_REMOVED_IMAGES_FILE_NAME,
            title='Removed images (docker_images_list.json)',
            text='*The following images were removed from `docker_images_list.json`:*',
            empty_text='*No old images has been removed from `docker_images_list.json`*',
        ),
        # No empty_text: stay silent when nothing failed to inspect.
        ImageReport(
            images=failed_to_inspect_images,
            file_name=FAILED_IMAGE_FILE_NAME,
            title='Failed images',
            text='*The following images failed to inspect:*',
        ),
    )

    try:
        # send a message to Slack
        response = client.chat_postMessage(
            channel=channel_id,
            text=(
                'Update `dockerfiles-info` finished\n'
                f'• `docker_images_metadata.json` - Added images: {len(added_images)}, '
                f'Removed images: {len(removed_images)}\n'
                f'• `docker_images_list.json` - Added images: {len(list_added_images)}, '
                f'Removed images: {len(list_removed_images)}'
            ),
        )

        message_ts = response['ts']
        print(f"Message sent successfully: {message_ts}")

        for report in reports:
            _post_report(client, channel_id, message_ts, report)

    except Exception as e:
        print(f"Error sending message: {str(e)}")
    finally:
        for report in reports:
            if os.path.exists(report.file_name):
                os.remove(report.file_name)
