import json

data = json.loads("""{ "Markdown ": [2, 3],
    "Grocery": [3, 4],
    "Reduced for Quick Sale": [4, 5],
    "Grocery": [5, 6],
"Grocery": [5, 6]}""")

print(data)

processed_data = {}
for key, value in data.items():
    if key not in processed_data:
        processed_data[key] = [value]
    else:
        processed_data[key].append(value)

print(json.dumps(processed_data, indent=4))