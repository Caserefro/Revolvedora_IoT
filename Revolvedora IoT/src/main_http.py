from flask import Flask, render_template, request, redirect, session
from handlers import *
app = Flask(__name__)


@app.route('/', methods=['POST'])
def ReceiveSensorData():
    if request.method == "POST":
        Package = request.data
        JsonDataReceived = json.loads(Package)
        operation_code = JsonDataReceived["Operation"]
        PackagetoSend = Response(operation_code, JsonDataReceived)
        return PackagetoSend


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
