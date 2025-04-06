import requests
import json

MCP_SERVER_URL = "http://127.0.0.1:5001/execute"


def execute_python_code(code: str):
    try:
        response = requests.post(MCP_SERVER_URL, json={"code": code})
        response_data = response.json()

        if response.status_code == 200:
            return response_data.get("result")
        else:
            return f"Error: {response_data.get('error')}"
    except Exception as e:
        return f"Error communicating with MCP server: {str(e)}"


# Example of using the function
if __name__ == "__main__":
    python_code = """
result = sum([1, 2, 3, 4])
print(result)
"""
    result = execute_python_code(python_code)
    print(f"Execution result: {result}")
