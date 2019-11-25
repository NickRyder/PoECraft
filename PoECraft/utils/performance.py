from contextlib import contextmanager
import time

@contextmanager
def timer(name=""):
    tic = time.time()
    yield
    print(f"{name}: {time.time() - tic}")