from fastmcp import FastMCP
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_NAME")]

mcp = FastMCP("Database Tools")


class QueryResult(BaseModel):
    rows: list[dict]
    count: int
    execution_time: float


@mcp.tool()
async def query_database(aggrigate: str, limit: int = 10) -> QueryResult:
    """
    Execute a MongoDB aggregation pipeline against the database

    Args:
        aggrigate: MongoDB aggregation pipeline to execute
        limit: Maximum number of rows to return
    """
    import time

    start = time.time()

    # Execute your query (with proper security!)
    collection_name = os.getenv("MEMBER_MASTER_COLLECTION")
    results = await db[collection_name].aggregate(aggrigate, limit=limit)

    return QueryResult(
        rows=results, count=len(results), execution_time=time.time() - start
    )
