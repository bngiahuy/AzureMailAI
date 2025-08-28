import asyncio
import logging
from typing import List, Optional
from azure.identity.aio import ClientSecretCredential
from msgraph.graph_service_client import GraphServiceClient
from msgraph.generated.models.message import Message
from html_to_markdown import convert_to_markdown
import unicodedata
import re
from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import (
                MessagesRequestBuilder)
logger = logging.getLogger(__name__)


class MailClient:
    """Client for interacting with Microsoft Graph API for mail operations."""

    def __init__(self, credential: ClientSecretCredential, scopes: List[str]):
        self.client = GraphServiceClient(credentials=credential, scopes=scopes)

    @staticmethod
    def clean_markdown(text: str) -> str:
        """
        Clean Markdown string, return plain text.
        """
        if not text:
            return ""

        text = unicodedata.normalize("NFC", text)

        # Remove code blocks ```...```
        text = re.sub(r"```[\s\S]*?```", "", text)

        # Remove inline code `...`
        text = re.sub(r"`([^`]*)`", r"\1", text)

        # Handle links [text](url)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

        # Handle images ![alt](url)
        text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)

        # Remove blockquotes ">"
        text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)

        # Remove bold/italic (**text**, *text*, _text_)
        text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
        text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    async def get_user_messages(
        self, user_id: str, folder_id: Optional[str] = None
    ) -> List[Message]:
        """
        Fetch all mail messages for a given user (optionally within a specific folder).
        Handles pagination.
        """
        if folder_id:
            request = (
                self.client.users.by_user_id(user_id)
                .mail_folders.by_mail_folder_id(folder_id)
                .messages
            )
        else:
            request = self.client.users.by_user_id(user_id).messages

        all_messages: List[Message] = []
        try:
            config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration()
            # Add headers to the configuration, to specify the response format
            config.headers.add("Prefer", "outlook.body-content-type='text'")
            response = await request.get(request_configuration=config)
            if not response or not response.value:
                logger.info("No messages found.")
                return all_messages

            all_messages.extend(response.value)

            # Uncomment the following lines to enable pagination
            # this code below will get all messages in the inbox

            # next_link = getattr(response, "odata_next_link", None)
            # while next_link:
            #     response = await request.with_url(next_link).get()
            #     if not response or not response.value:
            #         logger.info("No more messages found.")
            #         break
            #     all_messages.extend(response.value)
            #     next_link = getattr(response, "odata_next_link", None)

        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            raise

        return all_messages

    def process_latest_message(self, messages: List[Message]) -> Optional[str]:
        """
        Process the latest message and return formatted mail info.
        """
        if not messages:
            logger.info("No messages to process.")
            return None

        latest_msg = messages[0]

        # Check if body and content exist
        if not latest_msg.body or not latest_msg.body.content:
            logger.warning("Message body is empty.")
            return None

        # Because the body content is sometime HTML, we need to convert it to Markdown for easier processing. But if we add the header "Prefer: outlook.body-content-type='text'", the body content will be plain text, which means we can skip the conversion.
        # Uncomment the following lines to enable conversion
        # latest_msg_body_raw = convert_to_markdown(
        #     latest_msg.body.content,
        #     parser="lxml",
        #     extract_metadata=False,
        #     strip_newlines=True,
        # )
        # latest_msg_body_clean = self.clean_markdown(latest_msg_body_raw)

        # Check sender information
        sender_address = "Unknown"
        if (
            latest_msg.sender
            and latest_msg.sender.email_address
            and latest_msg.sender.email_address.address
        ):
            sender_address = latest_msg.sender.email_address.address

        subject = latest_msg.subject or "No Subject"
        date_str = "Unknown Date"
        if latest_msg.received_date_time:
            date_str = str(latest_msg.received_date_time.astimezone())

        mail_info = (
            f"From: {sender_address}.\n"
            f"Subject: {subject}.\n"
            f"Date: {date_str}.\n"
            f"Body: {latest_msg.body.content}.\n"
            # f"Body: {latest_msg_body_clean}.\n"
        )

        logger.info(f"Mail Information:\n{mail_info}\n")
        return mail_info
