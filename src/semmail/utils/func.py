from time import sleep


def retry(exception_type, attempts: int = 5, wait: float = 1):
    """
    Decorator to retry a function if it raises a specific exception.

    Parameters
    ----------
    exception_type
        The exception type to catch
    attempts
        The number of attempts to make before giving up
    wait
        The number of seconds to sleep between attempts
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(attempts):
                try:
                    return func(*args, **kwargs)
                except exception_type:
                    sleep(wait)
            else:
                raise

        return wrapper

    return decorator
