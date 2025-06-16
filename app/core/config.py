import os

for key, value in os.environ.items():
    print(f"{key} = {value}")
api_key = os.environ.get('OPENAI_API_KEY')

print(api_key)