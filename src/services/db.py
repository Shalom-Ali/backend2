from azure.cosmos import CosmosClient
from dotenv import load_dotenv
import os

load_dotenv()

class CosmosDB:
    def __init__(self):
        self.client = CosmosClient(
            url=os.getenv("COSMOS_ENDPOINT"),
            credential=os.getenv("COSMOS_KEY")
        )
        self.database = self.client.get_database_client(os.getenv("DATABASE_NAME"))
        self.container = self.database.get_container_client(os.getenv("CONTAINER_NAME"))

    def get_user(self, user_id: str):
        query = f"SELECT * FROM c WHERE c.id = '{user_id}'"
        items = list(self.container.query_items(query=query, enable_cross_partition_query=True))
        return items[0] if items else None

    def upsert_user(self, user: dict):
        self.container.upsert_item(user)

    def update_progress(self, user_id: str, module: str, progress: float):
        user = self.get_user(user_id)
        if user:
            user["progress"][module] = progress
            self.upsert_user(user)
