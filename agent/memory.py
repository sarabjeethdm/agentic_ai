import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from openai import AsyncOpenAI
import json

logger = logging.getLogger(__name__)


class MemoryStore:
    """Handles long-term memory storage and retrieval using Azure Cosmos DB with vector search."""

    def __init__(
        self,
        connection_string: Optional[str] = None,
        endpoint: Optional[str] = None,
        key: Optional[str] = None,
        database_name: str = "agent_memory",
        collection_name: str = "conversations",
    ):
        """
        Initialize the memory store.

        Args:
            connection_string: MongoDB connection string (for MongoDB vCore)
            endpoint: Cosmos DB endpoint (for SQL API)
            key: Cosmos DB key (for SQL API)
            database_name: Name of the database
            collection_name: Name of the collection/container
        """
        self.database_name = database_name
        self.collection_name = collection_name

        # Initialize OpenAI client for embeddings
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Determine which Cosmos DB API to use
        self.connection_string = connection_string or os.getenv(
            "AZURE_COSMOS_CONNECTION_STRING"
        )
        self.endpoint = endpoint or os.getenv("COSMOS_ENDPOINT")
        self.key = key or os.getenv("COSMOS_KEY")

        # Initialize the appropriate client
        self._init_cosmos_client()

    def _init_cosmos_client(self):
        """Initialize Cosmos DB client based on available credentials."""
        # Prioritize SQL API if both endpoint and key are provided
        if self.endpoint and self.key:
            # SQL API
            logger.info("Using Cosmos DB SQL API")
            self._init_sql_client()
        elif self.connection_string and self.connection_string.startswith("mongodb"):
            # MongoDB vCore API (only if it's a valid MongoDB connection string)
            logger.info("Using Cosmos DB MongoDB vCore API")
            self._init_mongodb_client()
        else:
            raise ValueError(
                "Missing credentials. Provide either:\n"
                "1. COSMOS_ENDPOINT and COSMOS_KEY (for SQL API), or\n"
                "2. AZURE_COSMOS_CONNECTION_STRING starting with 'mongodb://' or 'mongodb+srv://' (for MongoDB vCore)"
            )

    def _init_mongodb_client(self):
        """Initialize MongoDB vCore client."""
        try:
            from pymongo import MongoClient

            self.client_type = "mongodb"
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]

            # Create vector search index if it doesn't exist
            self._ensure_mongodb_vector_index()

            logger.info(
                f"Connected to Cosmos DB MongoDB vCore: {self.database_name}.{self.collection_name}"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Cosmos DB MongoDB vCore: {e}")
            raise

    def _init_sql_client(self):
        """Initialize SQL API client."""
        try:
            from azure.cosmos import CosmosClient, PartitionKey
            from azure.cosmos.exceptions import CosmosResourceExistsError

            self.client_type = "sql"
            self.client = CosmosClient(self.endpoint, credential=self.key)

            # Get or create database
            try:
                self.db = self.client.create_database(self.database_name)
            except CosmosResourceExistsError:
                self.db = self.client.get_database_client(self.database_name)

            try:
                # Create or get container (works for both serverless and provisioned)
                self.container = self.db.create_container_if_not_exists(
                    id=self.collection_name,
                    partition_key=PartitionKey(path="/session_id"),
                )
                logger.info(f"Created/retrieved container: {self.collection_name}")
            except Exception as e:
                logger.error(f"Failed to create/retrieve container: {e}")
                raise

            logger.info(
                f"Connected to Cosmos DB SQL API: {self.database_name}.{self.collection_name}"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Cosmos DB SQL API: {e}")
            raise

    def _ensure_mongodb_vector_index(self):
        """Create vector search index for MongoDB vCore."""
        try:
            indexes = self.collection.list_indexes()
            index_names = [idx["name"] for idx in indexes]

            if "vector_index" not in index_names:
                self.collection.create_index(
                    [("embedding", "cosmosSearch")],
                    name="vector_index",
                    cosmosSearchOptions={
                        "kind": "vector-ivf",
                        "numLists": 1,
                        "similarity": "COS",
                        "dimensions": 1536,
                    },
                )
                logger.info("MongoDB vector index created successfully")
        except Exception as e:
            logger.warning(f"Could not create MongoDB vector index: {e}")

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI's embedding model.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding
        """
        try:
            response = await self.openai_client.embeddings.create(
                model="text-embedding-3-small", input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    async def store_interaction(
        self,
        session_id: str,
        goal: str,
        plan: List[str],
        observations: List[str],
        result: str,
        metadata: Optional[Dict] = None,
    ):
        """
        Store an interaction in the memory database.

        Args:
            session_id: Unique session identifier
            goal: User's goal/query
            plan: Generated plan steps
            observations: Execution observations
            result: Final result
            metadata: Additional metadata
        """
        try:
            # Create a summary for embedding
            summary = f"Goal: {goal}\nResult: {result}\nPlan: {' -> '.join(plan)}"
            embedding = await self.generate_embedding(summary)

            # Create document
            document = {
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "goal": goal,
                "plan": plan,
                "observations": observations,
                "result": result,
                "embedding": embedding,
                "metadata": metadata or {},
            }

            # Insert based on client type
            if self.client_type == "mongodb":
                self.collection.insert_one(document)
            else:  # sql
                document["id"] = f"{session_id}_{datetime.utcnow().timestamp()}"
                self.container.create_item(body=document)

            logger.info(f"Stored interaction for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to store interaction: {e}")
            raise

    async def retrieve_similar_interactions(
        self, query: str, limit: int = 5, min_score: float = 0.7
    ) -> List[Dict]:
        """
        Retrieve similar past interactions using vector search.

        Args:
            query: Query text to search for
            limit: Maximum number of results to return
            min_score: Minimum similarity score (0-1)

        Returns:
            List of similar interactions
        """
        try:
            # Generate embedding for the query
            query_embedding = await self.generate_embedding(query)

            if self.client_type == "mongodb":
                return self._mongodb_vector_search(query_embedding, limit)
            else:  # sql
                return self._sql_vector_search(query_embedding, limit, min_score)
        except Exception as e:
            logger.error(f"Failed to retrieve similar interactions: {e}")
            return []

    def _mongodb_vector_search(
        self, query_embedding: List[float], limit: int
    ) -> List[Dict]:
        """Perform vector search using MongoDB vCore."""
        try:
            pipeline = [
                {
                    "$search": {
                        "cosmosSearch": {
                            "vector": query_embedding,
                            "path": "embedding",
                            "k": limit,
                        },
                        "returnStoredSource": True,
                    }
                },
                {"$project": {"embedding": 0, "_id": 0}},
            ]

            results = list(self.collection.aggregate(pipeline))
            logger.info(f"Retrieved {len(results)} similar interactions (MongoDB)")
            return results
        except Exception as e:
            logger.error(f"MongoDB vector search failed: {e}")
            return []

    def _sql_vector_search(
        self, query_embedding: List[float], limit: int, min_score: float
    ) -> List[Dict]:
        """Perform vector search using SQL API."""
        try:
            # Convert embedding to string format for SQL query
            embedding_str = str(query_embedding)

            # SQL API vector search using query
            query = f"""
                SELECT TOP {limit} c.session_id, c.timestamp, c.goal, c.plan, 
                       c.observations, c.result, c.metadata,
                       VectorDistance(c.embedding, {embedding_str}) AS SimilarityScore
                FROM c
                WHERE VectorDistance(c.embedding, {embedding_str}) > {min_score}
                ORDER BY VectorDistance(c.embedding, {embedding_str}) DESC
            """

            results = list(
                self.container.query_items(
                    query=query, enable_cross_partition_query=True
                )
            )

            # Remove embedding and internal fields
            for item in results:
                item.pop("embedding", None)
                item.pop("_rid", None)
                item.pop("_self", None)
                item.pop("_etag", None)
                item.pop("_attachments", None)
                item.pop("_ts", None)
                item.pop("id", None)

            logger.info(
                f"Retrieved {len(results)} similar interactions using native vector search"
            )
            return results
        except Exception as e:
            # VectorDistance not available - this is expected for containers without vector indexing
            # Fall back to manual similarity calculation silently
            logger.debug(f"Native vector search not available: {e}")
            return self._sql_manual_similarity_search(query_embedding, limit)

    def _sql_simple_query(self, limit: int) -> List[Dict]:
        """Fallback query without vector search for SQL API."""
        try:
            query = f"SELECT TOP {limit} * FROM c ORDER BY c.timestamp DESC"
            results = list(
                self.container.query_items(
                    query=query, enable_cross_partition_query=True
                )
            )

            for item in results:
                item.pop("embedding", None)
                item.pop("_rid", None)
                item.pop("_self", None)
                item.pop("_etag", None)
                item.pop("_attachments", None)
                item.pop("_ts", None)
                item.pop("id", None)

            return results
        except Exception as e:
            logger.error(f"Simple query failed: {e}")
            return []

    def _sql_manual_similarity_search(
        self, query_embedding: List[float], limit: int
    ) -> List[Dict]:
        """
        Manual similarity search by fetching all items and computing cosine similarity.
        Fallback when VectorDistance is not available.
        """
        try:
            import numpy as np

            # Fetch all items
            query = "SELECT * FROM c"
            all_items = list(
                self.container.query_items(
                    query=query, enable_cross_partition_query=True
                )
            )

            if not all_items:
                return []

            # Calculate cosine similarity for each item
            similarities = []
            query_vec = np.array(query_embedding)

            for item in all_items:
                if "embedding" in item and item["embedding"]:
                    item_vec = np.array(item["embedding"])
                    # Cosine similarity
                    similarity = np.dot(query_vec, item_vec) / (
                        np.linalg.norm(query_vec) * np.linalg.norm(item_vec)
                    )
                    similarities.append((similarity, item))

            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[0], reverse=True)

            # Get top N results
            results = []
            for similarity, item in similarities[:limit]:
                # Remove internal fields
                item.pop("embedding", None)
                item.pop("_rid", None)
                item.pop("_self", None)
                item.pop("_etag", None)
                item.pop("_attachments", None)
                item.pop("_ts", None)
                item.pop("id", None)
                item["SimilarityScore"] = float(similarity)
                results.append(item)

            logger.info(
                f"Retrieved {len(results)} similar interactions (manual similarity)"
            )
            return results
        except Exception as e:
            logger.error(f"Manual similarity search failed: {e}")
            return self._sql_simple_query(limit)

    def get_recent_history(self, session_id: str, limit: int = 5) -> List[Dict]:
        """
        Get recent conversation history for a session.

        Args:
            session_id: Session identifier
            limit: Number of recent interactions to retrieve

        Returns:
            List of recent interactions
        """
        try:
            if self.client_type == "mongodb":
                results = (
                    self.collection.find({"session_id": session_id})
                    .sort("timestamp", -1)
                    .limit(limit)
                )
                history = list(results)

                # Remove internal fields
                for item in history:
                    item.pop("embedding", None)
                    item.pop("_id", None)
            else:  # sql
                query = f"""
                    SELECT TOP {limit} c.session_id, c.timestamp, c.goal, c.plan, 
                           c.observations, c.result, c.metadata
                    FROM c
                    WHERE c.session_id = @session_id
                    ORDER BY c.timestamp DESC
                """
                results = list(
                    self.container.query_items(
                        query=query,
                        parameters=[{"name": "@session_id", "value": session_id}],
                        enable_cross_partition_query=True,
                    )
                )
                history = results

                # Remove internal fields
                for item in history:
                    item.pop("_rid", None)
                    item.pop("_self", None)
                    item.pop("_etag", None)
                    item.pop("_attachments", None)
                    item.pop("_ts", None)

            logger.info(
                f"Retrieved {len(history)} history items for session: {session_id}"
            )
            return history[::-1]  # Return in chronological order
        except Exception as e:
            logger.error(f"Failed to get recent history: {e}")
            return []

    async def get_relevant_context(
        self, goal: str, session_id: str, history_limit: int = 5, similar_limit: int = 3
    ) -> Dict:
        """
        Get relevant context including recent history and similar past interactions.

        Args:
            goal: Current goal/query
            session_id: Current session identifier
            history_limit: Number of recent history items to include
            similar_limit: Number of similar interactions to include

        Returns:
            Dictionary with history and similar_interactions
        """
        # Get recent history
        history = self.get_recent_history(session_id, history_limit)

        # Get similar past interactions
        similar = await self.retrieve_similar_interactions(goal, similar_limit)

        return {"recent_history": history, "similar_interactions": similar}

    def close(self):
        """Close the database connection."""
        if hasattr(self, "client"):
            if self.client_type == "mongodb":
                self.client.close()
            # SQL API client doesn't need explicit close
            logger.info("Closed Cosmos DB connection")
