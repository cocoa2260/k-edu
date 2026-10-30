import os
import sys

print("python:", sys.version.split()[0])
print("executable:", sys.executable)
print("virtual_env:", os.environ.get("VIRTUAL_ENV", "not active"))
