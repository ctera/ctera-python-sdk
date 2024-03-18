from .. import errors


async def accept(response):
    error_message = await response.text() if response.status > 399 else None
    return errors.accept(response, error_message)
