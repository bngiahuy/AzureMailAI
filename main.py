import asyncio
import logging
from azure.identity.aio import ClientSecretCredential
from config import Config
from mail_client import MailClient
from llm_client import LLMClient
from utils import timer
from users_manager import Users
from groups_manager import Groups
from msgraph.generated.models.planner_assignments import PlannerAssignments


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# async def test_llm():
# with timer():
#     mail_client = MailClient(credential, Config.GRAPH_SCOPES)
#     llm_client = LLMClient(Config.GEMINI_API_KEY)
#     user_email_address = "huy.bui47@bngiahuy.onmicrosoft.com"
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


async def test_users(credential):
    users_manager = Users(credential, Config.GRAPH_SCOPES)

    # List all users
    user = await users_manager.get_users()
    logger.info(f"User Details: {user}")

    # Get user planner tasks
    user_id = "b5337e23-45a1-4cd1-8da2-98725636ca47"  # huy.bui... userId
    tasks = await users_manager.get_user_planner_tasks(user_id=user_id)
    for task in tasks:
        logger.info(
            f"\nID: {task.id}\nTask: {task.title}\nStart Date: {task.start_date_time}\nDue Date: {task.due_date_time}\n"
            f"Status: {task.percent_complete}\nPriority: {task.priority}\nAssignee Priority: {task.assignee_priority}\n"
            f"Completed: {task.completed_date_time}\nCreated: {task.created_date_time}\n"
        )


async def test_create_task(credential):
    groups_manager = Groups(credential, Config.GRAPH_SCOPES)

    # 1. List all groups and pick the target group
    groups = await groups_manager.list_groups()
    logger.info(f"Groups: {groups}")
    for group in groups:
        logger.info(f"Group: {group.display_name}, ID: {group.id}")

    # Use the specific group ID for the workflow
    group_id = "7a37cd5a-29d3-4960-89be-bb489ab6ef7b"  # The Perspective Team

    # 2. List all plans in the group
    group_plans = await groups_manager.list_plans(group_id=group_id)
    logger.info(f"Plans: {group_plans}")
    if not group_plans:
        logger.info("No plans found for the group.")
        return
    plan_id = group_plans[0].id

    # 3. Create a new task in the plan and assign to user
    user_id = "b5337e23-45a1-4cd1-8da2-98725636ca47"  # huy.bui... userId
    assignments = PlannerAssignments(
        additional_data={
            user_id: {
                "@odata.type": "microsoft.graph.plannerAssignment",
                "orderHint": " !",
            }
        }
    )
    new_task = await groups_manager.create_task(
        plan_id=plan_id,
        title="My New Task from SDK Huy",
        assignments=assignments,
        due_date="2025-10-21T07:00:00Z",
    )
    logger.info(f"New Task: {new_task}")

    # 4. List all tasks in the plan to verify
    tasks = await groups_manager.list_tasks_by_plan(group_id=group_id, plan_id=plan_id)
    logger.info(f"List tasks in Plan after creation: {tasks}")


async def test_bucket_list(groups_manager: Groups):
    # List all buckets in a specific plan
    group_id = "7a37cd5a-29d3-4960-89be-bb489ab6ef7b"  # The Perspective Team

    # 2. List all plans in the group
    group_plans = await groups_manager.list_plans(group_id=group_id)
    logger.info(f"Plans: {group_plans}")
    if not group_plans:
        logger.info("No plans found for the group.")
        return

    # Get the first plan ID
    plan_id = group_plans[0].id
    buckets = await groups_manager.list_buckets_by_plan(plan_id=plan_id)
    logger.info(f"Buckets in Plan {plan_id}: {buckets}")


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
        groups_manager = Groups(credential, Config.GRAPH_SCOPES)

        # Test user-related operations
        await test_users(credential)

        # Test create task in Planner
        # await test_create_task(credential)

        # Test bucket list
        # await test_bucket_list(groups_manager)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
