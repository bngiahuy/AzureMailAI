import logging
from msgraph.graph_service_client import GraphServiceClient
from kiota_abstractions.base_request_configuration import RequestConfiguration

logger = logging.getLogger(__name__)

class Groups:
    """
    Client for interacting with Microsoft 365 Groups via Microsoft Graph API.
    """
    def __init__(self, credential, scopes):
        self.client = GraphServiceClient(credentials=credential, scopes=scopes)

    async def create_task(self, plan_id: str, title: str, assignments, due_date: str = None, **kwargs):
        """
        Create a new task in Microsoft Planner.

        Docs: https://learn.microsoft.com/en-us/graph/api/planner-post-tasks?view=graph-rest-1.0
        Task resource: https://learn.microsoft.com/en-us/graph/api/resources/plannertask?view=graph-rest-1.0

        Args:
            plan_id (str): The ID of the plan to add the task to (required).
            title (str): The title of the new task (required).
            assignments (dict): A dictionary mapping userId to assignment details (optional).
            due_date (str): Due date/time in ISO 8601 format (e.g., '2025-09-20T17:00:00Z').
            **kwargs: Additional properties for the PlannerTask (see Microsoft Graph docs).

        Returns:
            The created task object, or None if creation failed.

        Example usage:
            task = await groups_manager.create_task(plan_id="<plan_id>", title="My Task", assignments={"<user_id>": {"orderHint": " !"}}, due_date="2025-09-20T17:00:00Z")
        """
        from msgraph.generated.models.planner_task import PlannerTask
        try:
            task_body = PlannerTask(
                plan_id=plan_id,
                title=title,
                assignments=assignments,
                priority=7, # Currently, Planner interprets values 0 and 1 as 'urgent', 2, 3 and 4 as 'important', 5, 6, and 7 as 'medium', and 8, 9, and 10 as 'low'.
                due_date_time=due_date, # ISO 8601 format
                **kwargs
            )
            # POST /planner/tasks as per official docs
            # https://learn.microsoft.com/en-us/graph/api/planner-post-tasks?view=graph-rest-1.0
            task = await self.client.planner.tasks.post(task_body)
            return task
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None

    async def list_tasks_by_plan(self, group_id: str, plan_id: str):
        """
        List all tasks for a specific plan in Microsoft Planner.

        Args:
            plan_id (str): The ID of the plan whose tasks to list (required).

        Returns:
            A list of task objects, or an empty list if none found or on error.

        Example usage:
            tasks = await groups_manager.list_tasks_by_plan(plan_id="<plan_id>")
        """
        try:
            tasks = await self.client.groups.by_group_id(group_id).planner.plans.by_planner_plan_id(plan_id).tasks.get()
            return tasks.value if tasks else []
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return []

    async def list_groups(self, **kwargs):
        """
        List all Microsoft 365 groups available to the authenticated user.

        Args:
            **kwargs: Additional query parameters (e.g., filter, select, top).

        Returns:
            A list of group objects, or an empty list if none found or on error.

        Example usage:
            groups = await groups_manager.list_groups()
        """
        from msgraph.generated.groups.groups_request_builder import GroupsRequestBuilder
        try:
            query_params = None
            if kwargs:
                query_params = GroupsRequestBuilder.GroupsRequestBuilderGetQueryParameters(**kwargs)
            config = RequestConfiguration(query_parameters=query_params) if query_params else None
            groups = await self.client.groups.get(request_configuration=config)
            return getattr(groups, 'value', []) if groups else []
        except Exception as e:
            logger.error(f"Error listing groups: {e}")
            return []
    
    async def list_plans(self, group_id: str):
        """
        List all plans for a specific Microsoft 365 group (owner) in Microsoft Planner.

        Args:
            group_id (str): The ID of the Microsoft 365 group (owner) whose plans to list (required).
            **kwargs: Additional query parameters (e.g., select, top).

        Returns:
            A list of plan objects, or an empty list if none found or on error.

        Example usage:
            plans = await planner.list_plans(group_id="<group_id>")
        """
        try:
            plans = await self.client.groups.by_group_id(group_id).planner.plans.get()
            
            return plans.value if plans else []
        except Exception as e:
            logger.error(f"Error listing plans: {e}")
            return []