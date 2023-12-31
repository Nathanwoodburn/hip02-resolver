from flask import Flask, make_response, redirect, request
import os
import dotenv
import requests
import hip02
import re


app = Flask(__name__)
dotenv.load_dotenv()

HSD_IP = '10.2.1.15'
HSD_PORT = 5350

if os.getenv('HSD_IP'):
    HSD_IP = os.getenv('HSD_IP')
if os.getenv('HSD_PORT'):
    HSD_PORT = os.getenv('HSD_PORT')

def valid_domain(domain):
    regex = "^((xn--)?[a-z0-9]+\.)*((xn--)?[a-z0-9]+)$"
    return re.match(regex, domain)


@app.route('/')
def index():
    return redirect("https://nathan.woodburn.au")


# Special routes
@app.route('/.well-known/wallets/<token>')
def send_wallet(token):
    address = requests.get('https://nathan.woodburn.au/.well-known/wallets/'+token).text
    return make_response(address, 200, {'Content-Type': 'text/plain'})

@app.route('/favicon.ico')
def favicon():
    return redirect('https://nathan.woodburn.au/favicon.ico')

@app.route('/<path>.json')
def jsonlookup(path):
    if not valid_domain(path):
        return make_response({"success":False,"error":"Invalid domain"}, 200, {'Content-Type': 'application/json'})

    TLSA = hip02.TLSA_check(HSD_IP,HSD_PORT,path)
    if TLSA != True:
        return make_response({"success":False,"error":TLSA}, 200, {'Content-Type': 'application/json'})
    token = "HNS"
    if 'token' in request.args:
        token = request.args['token'].upper()

    hip2 = hip02.resolve(HSD_IP, HSD_PORT, path,token)
    if not hip2:
        return make_response({"success":False,"error":hip2}, 200, {'Content-Type': 'application/json'})

    return make_response({"success":True,"address":hip2}, 200, {'Content-Type': 'application/json'})


@app.route('/<path>')
def lookup(path):
    if not valid_domain(path):
        return make_response("Invalid domain", 200, {'Content-Type': 'text/plain'})

    TLSA = hip02.TLSA_check(HSD_IP,HSD_PORT,path)
    if TLSA != True:
        return make_response(TLSA, 200, {'Content-Type': 'text/plain'})
    token = "HNS"
    if 'token' in request.args:
        token = request.args['token'].upper()

    hip2 = hip02.resolve(HSD_IP, HSD_PORT, path,token)
    if not hip2:
        return make_response("", 200, {'Content-Type': 'text/plain'})
    return make_response(hip2, 200, {'Content-Type': 'text/plain'})

# 404 catch all
@app.errorhandler(404)
def not_found(e):
    return redirect('/')




if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')