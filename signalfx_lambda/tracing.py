import functools

def wrapper(func):
    @functools.wraps(func)
    def call(*args, **kwargs):
        print("tracing wrapper")

        # do nothing else for now
        func(*args, **kwargs)

    return call
