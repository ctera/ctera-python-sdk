from .. import errors


def accept(response):
    error_message = response.text() if response.status > 399 else None
    return errors.accept(response, error_message)
