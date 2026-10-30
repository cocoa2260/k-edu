from importlib.metadata import PackageNotFoundError, version

for package in ["fastapi", "uvicorn", "pydantic", "openai"]:
    try:
        print(package, version(package))
    except PackageNotFoundError:
        print(package, "not installed")
