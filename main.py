import asyncio
import logging
from azure.identity.aio import ClientSecretCredential
from config import Config
from mail_client import MailClient
from llm_client import LLMClient
from utils import timer
from users_manager import Users
from groups_manager import Groups
from planner_manager import Planner
# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
        # mail_client = MailClient(credential, Config.GRAPH_SCOPES)
        # llm_client = LLMClient(Config.GEMINI_API_KEY)

        # user_email_address = "huy.bui47@bngiahuy.onmicrosoft.com"

        # with timer():
        #     # Fetch messages
        #     messages = await mail_client.get_user_messages(user_email_address)
        #     if not messages:
        #         logging.info("No messages found.")
        #         return

        #     # Process latest message
        #     mail_info = mail_client.process_latest_message(messages)
        #     if not mail_info:
        #         logging.info("No mail info to process.")
        #         return

        #     # Invoke LLM for summarization
        #     summary = llm_client.invoke_llm(mail_info)
        #     if summary:
        #         print(summary)
        #     else:
        #         logging.error("Failed to generate summary.")

        # users_manager = Users(credential, Config.GRAPH_SCOPES)

        # # Find a specific user by email
        # user = await users_manager.get_user_by_email("huy.bui47@bngiahuy.onmicrosoft.com")
        # print(f"User Details: {user}")

        # Groups manager
        groups_manager = Groups(credential, Config.GRAPH_SCOPES)

        # List all groups
        groups = await groups_manager.list_groups()
        print(f"Groups: {groups}")
        for group in groups:
            print(f"Group: {group.display_name}, ID: {group.id}")

        # I chose a specific group to work with
        # group_id = "7a37cd5a-29d3-4960...", name = "The Perspective Team"
        group_plans = await groups_manager.list_plans(group_id="7a37cd5a-29d3-4960-89be-bb489ab6ef7b")
        print(f"Plans: {group_plans}")

        # List tasks in a specific plan
        tasks = await groups_manager.list_tasks_by_plan(group_id="7a37cd5a-29d3-4960-89be-bb489ab6ef7b", plan_id=group_plans[0].id)
        print(f"List tasks in Plan: {tasks}")
        
        # Create a new task in a specific plan
        from msgraph.generated.models.planner_assignments import PlannerAssignments
        new_task_assignment = PlannerAssignments(
            odata_type="microsoft.graph.plannerAssignments",
            additional_data={
                "b5337e23-45a1-4cd1-8da2-98725636ca47": { # huy.bui... userId
                    "@odata.type": "microsoft.graph.plannerAssignment",
                    "orderHint": " !"
                }
            }
        )
        new_task = await groups_manager.create_task(
            # group_id="7a37cd5a-29d3-4960-89be-bb489ab6ef7b",
            plan_id=group_plans[0].id,
            title="My New Task from SDK #5",
            assignments=new_task_assignment,
            due_date="2025-10-20T07:00:00Z"
        )
        print(f"New Task: {new_task}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
