from contextlib import asynccontextmanager

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


@asynccontextmanager
async def get_checkpointer():
    """
    Provides a properly managed async SQLite checkpoint saver.

    WHY:
    AsyncSqliteSaver.from_conn_string() returns an async
    context manager, not the saver itself.

    This wrapper ensures:
    - proper resource initialization
    - proper teardown
    - correct async lifecycle handling
    """

    async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
        yield checkpointer
