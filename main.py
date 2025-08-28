import asyncio
import logging
from azure.identity.aio import ClientSecretCredential
from config import Config
from mail_client import MailClient
from llm_client import LLMClient
from utils import timer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def main():
    """Main function to fetch user mails, process the latest one, and summarize with LLM."""
    try:
        # Validate configuration
        Config.validate()

        # Initialize clients
        credential = ClientSecretCredential(
            Config.AZURE_TENANT_ID,
            Config.AZURE_CLIENT_ID,
            Config.AZURE_CLIENT_SECRET,
        )
        mail_client = MailClient(credential, Config.GRAPH_SCOPES)
        llm_client = LLMClient(Config.GEMINI_API_KEY)

        user_email_address = "youremail@example.com"

        with timer():
            # Fetch messages
            messages = await mail_client.get_user_messages(user_email_address)
            if not messages:
                logging.info("No messages found.")
                return

            # Process latest message
            mail_info = mail_client.process_latest_message(messages)
            if not mail_info:
                logging.info("No mail info to process.")
                return

            # Invoke LLM for summarization
            summary = llm_client.invoke_llm(mail_info)
            if summary:
                print(summary)
            else:
                logging.error("Failed to generate summary.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
