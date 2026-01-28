#!/usr/bin/env python3
"""
Test script for the Memory Store functionality.
Tests connection, storage, and retrieval without running the full agent.
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def test_memory_store():
    """Test the memory store functionality."""
    print("=" * 60)
    print("Memory Store Test")
    print("=" * 60)

    try:
        from agent.memory import MemoryStore

        print("\n1. Initializing Memory Store...")
        memory = MemoryStore()
        print("✅ Memory store initialized")

        print("\n2. Testing embedding generation...")
        test_text = "What is the weather like today?"
        embedding = await memory.generate_embedding(test_text)
        print(f"✅ Generated embedding with {len(embedding)} dimensions")

        print("\n3. Testing interaction storage...")
        test_session = "test-session-123"
        await memory.store_interaction(
            session_id=test_session,
            goal="Test weather query",
            plan=["Get weather", "Format response"],
            observations=["Weather is sunny", "Formatted successfully"],
            result="The weather is sunny today",
            metadata={"test": True},
        )
        print("✅ Interaction stored successfully")

        print("\n4. Testing history retrieval...")
        history = memory.get_recent_history(test_session, limit=5)
        print(f"✅ Retrieved {len(history)} history items")
        if history:
            print(f"   Latest goal: {history[-1]['goal']}")

        print("\n5. Testing similarity search...")
        similar = await memory.retrieve_similar_interactions(
            "What's the weather forecast?", limit=3
        )
        print(f"✅ Found {len(similar)} similar interactions")
        if similar:
            print(f"   Most similar: {similar[0]['goal']}")

        print("\n6. Testing full context retrieval...")
        context = await memory.get_relevant_context(
            goal="Current temperature",
            session_id=test_session,
            history_limit=5,
            similar_limit=3,
        )
        print(
            f"✅ Retrieved context with {len(context['recent_history'])} history items"
        )
        print(f"   and {len(context['similar_interactions'])} similar interactions")

        print("\n7. Cleaning up...")
        memory.close()
        print("✅ Connection closed")

        print("\n" + "=" * 60)
        print("✅ All memory store tests passed!")
        print("=" * 60)

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("   Make sure dependencies are installed: uv pip install -e .")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has AZURE_COSMOS_CONNECTION_STRING")
        print("2. Verify your Cosmos DB cluster is running")
        print("3. Check firewall rules allow your IP")
        print("4. Ensure you have an OpenAI API key set")


async def test_connection_only():
    """Test just the database connection."""
    print("\n" + "=" * 60)
    print("Quick Connection Test")
    print("=" * 60)

    try:
        from pymongo import MongoClient

        connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
        if not connection_string or "your_cosmos" in connection_string:
            print("❌ AZURE_COSMOS_CONNECTION_STRING not configured in .env")
            return

        print("\nConnecting to Cosmos DB...")
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)

        # Test connection
        client.admin.command("ping")
        print("✅ Successfully connected to Cosmos DB!")

        # List databases
        dbs = client.list_database_names()
        print(f"✅ Found {len(dbs)} databases")

        client.close()

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nCheck:")
        print("1. Connection string is correct")
        print("2. Cluster is running in Azure")
        print("3. Firewall allows your IP")


if __name__ == "__main__":
    print("\nWhich test would you like to run?")
    print("1. Full memory store test (requires OpenAI API)")
    print("2. Connection test only")
    print("3. Both")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        asyncio.run(test_memory_store())
    elif choice == "2":
        asyncio.run(test_connection_only())
    elif choice == "3":
        asyncio.run(test_connection_only())
        print("\n")
        asyncio.run(test_memory_store())
    else:
        print("Invalid choice. Running full test...")
        asyncio.run(test_memory_store())
