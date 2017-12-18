"""
A flask server that gets a ping when the google form is filled up.
Link to google form : https://goo.gl/forms/0QQBq8OkwX5vuJVj1
"""
from flask import Flask, request

app = Flask(__name__)


@app.route("/",methods=["POST"])
def getUpdate():
    print(request.data.decode('utf8'))
    return "200"


# if __name__ == '__main__':
#     app.run(port=3113)

msg = "okau"
print(type(msg))