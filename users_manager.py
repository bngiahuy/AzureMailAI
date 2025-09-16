import logging
from msgraph.graph_service_client import GraphServiceClient
from azure.identity.aio import ClientSecretCredential
from msgraph.generated.users.users_request_builder import UsersRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration

logger = logging.getLogger(__name__)


class Users:
    """Client for interacting with Microsoft Graph API for user operations."""

    def __init__(self, credential: ClientSecretCredential, scopes: list[str]):
        self.client = GraphServiceClient(credentials=credential, scopes=scopes)


    async def get_user_by_email(self, email: str, select: list[str] = None):
        """
        Fetch a user's information from Microsoft Graph API by email (userPrincipalName).
        Optionally, select specific properties to return.
        """
        from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
        try:
            query_params = None
            if select:
                query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
                    select=select
                )
            config = RequestConfiguration(query_parameters=query_params) if query_params else None
            user = await self.client.users.by_user_id(email).get(request_configuration=config)
            return user
        except Exception as e:
            logger.error(f"Error fetching user by email: {e}")
            return None
        
    async def get_user_planner_tasks(self, user_id: str):
        """
        Fetch a user's Planner tasks from Microsoft Graph API.
        """
        try:
            tasks = await self.client.users.by_user_id(user_id).planner.tasks.get()
            return tasks.value if tasks else []
        except Exception as e:
            logger.error(f"Error fetching user's planner tasks: {e}")
            return None

    async def get_users(self):
        """
        Fetch all users from Microsoft Graph API.
        """
        try:
            query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
                filter="startswith(userPrincipalName,'huy')",
                count=True,
                top=10,
            )
            config = RequestConfiguration(query_parameters=query_params)
            # The 'ConsistencyLevel: eventual' header is required for advanced queries (e.g., $count, $filter with certain properties) in Microsoft Graph API.
            # Without this header, requests using $count or advanced filters may fail or return incomplete results.
            config.headers.add("ConsistencyLevel", "eventual")
            users = await self.client.users.get(request_configuration=config)
            return users
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []
