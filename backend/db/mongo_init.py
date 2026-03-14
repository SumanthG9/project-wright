# backend/db/mongo_init.py
"""
MongoDB initialisation script.

Creates the story_base collection and its project_id index.
Safe to run multiple times — idempotent.

Usage (from project root, venv activated):
    python -m backend.db.mongo_init
"""

import asyncio
from http import client
from typing import Collection

import structlog
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, IndexModel

from backend.core.config import MONGO_DB, MONGO_URI

log = structlog.get_logger()


async def init_mongo():
    """Connect to MongoDB, create story_base collection and project_id index."""
    host = MONGO_URI.split("@")[-1]
    log.info("connecting to database, mongo.connecting", host=host, database=MONGO_DB)
    client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]

    # existing collection name
    existing_collecitons = await db.list_collection_names()
    if "story_base" not in existing_collecitons:
        await db.create_collection("story_base")
        log.info("mongo.colleciton_created", collection="story_base")
    else:
        log.info("mongo.collection_already_exists", collection="story_base")

    # Index of project, project_id indexes
    collection = db["story_base"]
    index = IndexModel([("project_id", ASCENDING)], name="project_id_1")
    result = await collection.create_indexes([index])
    log.info("mongo.indexes_created", indexes=result)

    log.info("mongo.init_complete", database=MONGO_DB)


if __name__ == "__main__":
    asyncio.run(init_mongo())
