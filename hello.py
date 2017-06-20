from flask import Flask
from flask import request

app=Flask(__name__)

@app.route('/')
def index():
	return '<h1>hello world!</h1>'
@app.route('/1')
def index1():
	return '<h1>first page</h1>'
@app.route('/user/<name>')
def user(name):
	return '<h1>hello, %s</h1>'% name

@app.route('/useragent')
def index2():
	user_agent= request.headers.get('User-agent')
	return '<p>your brower is %s</p>'% user_agent


if __name__=='__main__':
	app.run(debug=True)

