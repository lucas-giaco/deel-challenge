import os
# from mysql.connector import connect, Error
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def healthz():
    """Health endpoint"""
    return "ok"

@app.route("/reverse")
def reverse_ip():
    """
    Reverse request IP address
    If the XFF header is present we'll use that IP (means the app is behind a proxy)
    Otherwise, it will use the remote address
    """
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    ip_list = ip.split(".")
    ip_list.reverse()
    return ".".join(ip_list)
    # try:
    #     with connect(
    #       host=os.getenv('DB_HOST', 'localhost'),
    #       port=int(os.getenv('DB_PORT', '3306')),
    #       user=os.getenv('DB_USER'),
    #       password=os.getenv('DB_PASSWORD')
    #     ) as connection:
    #         if connection.is_connected():
    #             db_Info = connection.get_server_info()
    #             return f"Connected to MySQL Server version {db_Info}"
    # except Error as e:
    #     print(e)
    #     return 'Unable to connect to DB'

if __name__ == '__main__':
    host = os.getenv('HOST_IP', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    app.run(host=host, port=port, debug=True)
