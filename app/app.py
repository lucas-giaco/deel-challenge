import os
from mysql.connector import connect, Error
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def healthz():
    """Health endpoint"""
    return "ok"

@app.route("/db")
def get_ips():
    """Get all IPs stored in the DB"""
    ips = []
    try:
        if bool(os.getenv('STORAGE_ENABLED', 'False')):
            with connect(
                host=os.getenv('STORAGE_HOST', 'localhost'),
                port=int(os.getenv('STORAGE_PORT', '3306')),
                database=os.getenv('STORAGE_DATABASE'),
                user=os.getenv('STORAGE_USER'),
                password=os.getenv('STORAGE_PASSWORD')
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM ips")
                    ips = cursor.fetchall()
    except Error as e:
        return e.msg, 500
    return ips

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
    reversed_ip = ".".join(ip_list)

    try:
        store_ip(ip, reversed_ip)
    except Error as e:
        return e.msg, 500

    return f'{ip} => {reversed_ip}'

def store_ip(ip, reversed_ip):
    """Store an IP and its reversed IP into a DB"""
    if bool(os.getenv('STORAGE_ENABLED', 'False')):
        with connect(
            host=os.getenv('STORAGE_HOST', 'localhost'),
            port=int(os.getenv('STORAGE_PORT', '3306')),
            database=os.getenv('STORAGE_DATABASE'),
            user=os.getenv('STORAGE_USER'),
            password=os.getenv('STORAGE_PASSWORD')
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO ips(ip, reverse_ip) VALUES(%s, %s)",
                    (ip, reversed_ip)
                )
                connection.commit()

if __name__ == '__main__':
    host = os.getenv('HOST_IP', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    debug = bool(os.getenv('DEBUG', 'False'))
    app.run(host=host, port=port, debug=debug)
