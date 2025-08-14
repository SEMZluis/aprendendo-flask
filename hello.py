from flask import Flask, request, url_for, render_template
from markupsafe import escape

app = Flask(__name__)       # cria uma instância da interface, a qual recebe como nome o nome do pacote ou do módulo em que se encontra

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    if request.method == 'GET':
        return render_template('hello.html', person=name)
    else:
        return 'dracarys'

# COM HTML ESCAPING
@app.route("/user/<username>")
def hello_user(name):
    return f"Hello, {escape(name)}!"

@app.get("/login")
def login_get():
    return 'faça login ai carai'

with app.test_request_context():
    print(url_for('login_get'))


