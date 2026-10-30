routes: dict[tuple[str, str], object] = {}

def route(method: str, path: str):
    def decorator(func):
        routes[(method, path)] = func
        return func
    return decorator

@route("POST", "/chat")
def chat(question: str) -> dict[str, str]:
    return {"answer": question.upper()}

handler = routes[("POST", "/chat")]
print(handler("hello"))
