import asyncio
import logging
import functools


logger = logging.getLogger('cterasdk.common')


def execute_with_retries(retries=None, backoff=None, max_backoff=None):
    """
    A decorator that retries a function or coroutine upon exception, using exponential backoff.

    This decorator supports both synchronous and asynchronous functions.

    :param int retries: The maximum number of attempts before giving up.
    :param int backoff: The initial backoff delay in seconds.
    """
    def decorator(func):
        @functools.wraps(func)
        async def a_wrapper(*args, **kwargs):
            delay = backoff
            for try_num in range(retries):
                try:
                    logger.debug("Try %s out of %s of function: '%s'", try_num + 1, retries, func.__name__)
                    return await func(*args, **kwargs)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    logger.debug("Try %s of %s of function '%s' failed. Backing off for %s second(s).", try_num + 1, retries,
                                 func.__name__, delay)
                    if try_num == retries - 1:
                        raise e
                    await asyncio.sleep(delay)
                    delay = min(max_backoff, delay * 2)
        return a_wrapper
    return decorator
