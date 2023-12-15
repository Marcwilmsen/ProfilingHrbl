import os
import requests

# Endpoint URL for a Django server running on localhost:8000
url = "http://127.0.0.1:8000/upload/solution_generations/"  # Adjust the endpoint path if it's different

absolute_path = os.path.abspath("solution_generations.json")
# Prepare the file for sending
with open(absolute_path, "rb") as f:
    files = {'file': f}

    # Send the request
    response = requests.post(url, files=files, data={"name": "solution_generations"})

# Print the server's response
print(response.text)
