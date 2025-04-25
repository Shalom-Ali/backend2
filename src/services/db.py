from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from dotenv import load_dotenv
import os

load_dotenv()

class CosmosDB:
    def __init__(self):
        endpoint = os.getenv("COSMOS_ENDPOINT")
        key = os.getenv("COSMOS_KEY")
        if not endpoint or not key:
            raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY must be set")
        self.client = CosmosClient(url=endpoint, credential=key)
        self.database = self.client.get_database_client(os.getenv("DATABASE_NAME", "LearningDB"))
        self.container = self.database.get_container_client(os.getenv("CONTAINER_NAME", "Users"))

    def get_user(self, user_id: str):
        try:
            query = "SELECT * FROM c WHERE c.id = @user_id"
            items = list(self.container.query_items(
                query=query,
                parameters=[{"name": "@user_id", "value": user_id}],
                enable_cross_partition_query=True
            ))
            return items[0] if items else None
        except CosmosResourceNotFoundError:
            return None

    def upsert_user(self, user: dict):
        self.container.upsert_item(user)

    def update_progress(self, user_id: str, module: str, progress: float):
        user = self.get_user(user_id)
        if user:
            user["progress"][module] = progress
            self.upsert_user(user)
            return user
        return None
