import asyncio
import logging
from azure.identity.aio import ClientSecretCredential
from config import Config
from mail_client import MailClient
from llm_client import LLMClient
from utils import timer
from users_manager import Users
from groups_manager import Groups
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

        # 1. List all groups and pick the target group
        groups = await groups_manager.list_groups()
        print(f"Groups: {groups}")
        for group in groups:
            print(f"Group: {group.display_name}, ID: {group.id}")

        # Use the specific group ID for the workflow
        group_id = "7a37cd5a-29d3-4960-89be-bb489ab6ef7b" # The Perspective Team

        # 2. List all plans in the group
        group_plans = await groups_manager.list_plans(group_id=group_id)
        print(f"Plans: {group_plans}")
        if not group_plans:
            print("No plans found for the group.")
            return
        plan_id = group_plans[0].id

        # 3. Create a new task in the plan and assign to user
        user_id = "b5337e23-45a1-4cd1-8da2-98725636ca47" # huy.bui... userId
        from msgraph.generated.models.planner_assignments import PlannerAssignments
        assignments = PlannerAssignments(
            additional_data={
                user_id: {
                    "@odata.type": "microsoft.graph.plannerAssignment",
                    "orderHint": " !"
                }
            }
        )
        new_task = await groups_manager.create_task(
            plan_id=plan_id,
            title="My New Task from SDK Huy",
            assignments=assignments,
            due_date="2025-10-21T07:00:00Z"
        )
        print(f"New Task: {new_task}")

        # 4. List all tasks in the plan to verify
        tasks = await groups_manager.list_tasks_by_plan(group_id=group_id, plan_id=plan_id)
        print(f"List tasks in Plan after creation: {tasks}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
