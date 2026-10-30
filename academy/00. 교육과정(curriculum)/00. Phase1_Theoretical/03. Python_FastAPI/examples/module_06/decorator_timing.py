from functools import wraps
from time import perf_counter, sleep

def measure(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        started = perf_counter()
        result = func(*args, **kwargs)
        print(f"elapsed={perf_counter() - started:.3f}s")
        return result
    return wrapper

@measure
def generate_answer(question: str) -> str:
    sleep(0.05)
    return f"answer: {question}"

print(generate_answer("Decorator란?"))
