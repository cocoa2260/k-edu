contracts = [
    {"method": "GET", "path": "/documents/{id}", "status": 200},
    {"method": "POST", "path": "/questions", "status": 201},
    {"method": "DELETE", "path": "/documents/{id}", "status": 204},
]

for contract in contracts:
    print(f"{contract['method']:6} {contract['path']} -> {contract['status']}")
