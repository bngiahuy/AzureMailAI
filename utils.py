import asyncio
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def timer():
    """Context manager to calculate and log the time of a process."""
    start_time = asyncio.get_event_loop().time()
    try:
        yield
    finally:
        end_time = asyncio.get_event_loop().time()
        elapsed_time = end_time - start_time
        logger.info(f"Elapsed time: {elapsed_time:.2f} seconds")
