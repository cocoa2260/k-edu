user = {"id": 1, "name": "Kim", "active": True}
user["role"] = "student"

print(user["name"])
print(user.get("email", "email 없음"))
for key, value in user.items():
    print(key, value)
