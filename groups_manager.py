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
        Create a new Planner task in a plan.

        Microsoft Docs:
        - Create task: https://learn.microsoft.com/en-us/graph/api/planner-post-tasks?view=graph-rest-1.0
        - Task resource: https://learn.microsoft.com/en-us/graph/api/resources/plannertask?view=graph-rest-1.0

        Args:
            plan_id (str): ID of the plan to add the task to.
            title (str): Title of the new task.
            assignments (dict): Mapping userId to assignment details.
            due_date (str): Due date/time in ISO 8601 format (optional).
            **kwargs: Additional PlannerTask properties.

        Returns:
            PlannerTask object if successful, else None.
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
            task = await self.client.planner.tasks.post(task_body)
            return task
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None

    async def list_tasks_by_plan(self, group_id: str, plan_id: str):
        """
        List all tasks in a specific Planner plan.

        Microsoft Docs:
        - List tasks: https://learn.microsoft.com/en-us/graph/api/planner-list-tasks?view=graph-rest-1.0

        Args:
            group_id (str): ID of the group that owns the plan.
            plan_id (str): ID of the plan whose tasks to list.

        Returns:
            List of PlannerTask objects, or empty list if none/error.
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

        Microsoft Docs:
        - List groups: https://learn.microsoft.com/en-us/graph/api/group-list?view=graph-rest-1.0

        Args:
            **kwargs: Query parameters (e.g., filter, select, top).

        Returns:
            List of Group objects, or empty list if none/error.
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
        List all Planner plans for a specific Microsoft 365 group.

        Microsoft Docs:
        - List plans: https://learn.microsoft.com/en-us/graph/api/planner-list-plans?view=graph-rest-1.0

        Args:
            group_id (str): ID of the group whose plans to list.

        Returns:
            List of PlannerPlan objects, or empty list if none/error.
        """
        try:
            plans = await self.client.groups.by_group_id(group_id).planner.plans.get()
            
            return plans.value if plans else []
        except Exception as e:
            logger.error(f"Error listing plans: {e}")
            return []