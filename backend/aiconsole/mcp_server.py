from flask import Flask, request, jsonify
import sys
import io

app = Flask(__name__)


@app.route("/execute", methods=["POST"])
def execute_code():
    data = request.get_json()

    # Get the Python code to execute
    code = data.get("code")

    if not code:
        return jsonify({"error": "No code provided"}), 400

    try:
        # Redirect stdout to capture print statements
        old_stdout = sys.stdout
        result = io.StringIO()
        sys.stdout = result

        # Execute the code
        exec(code)

        # Reset stdout
        sys.stdout = old_stdout

        # Return the result
        return jsonify({"result": result.getvalue()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
