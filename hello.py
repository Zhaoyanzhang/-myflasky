from flask import Flask,session,redirect,url_for,flash
from flask import request
from flask import render_template
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

app = Flask(__name__)
app.config['SECRET_KEY']='hard to guess string'

manager = Manager(app)
bootstrap=Bootstrap(app)
moment=Moment(app)

class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

@app.route('/',methods=['GET','POST'])
def index():
	form =NameForm()
	if form.validate_on_submit():
		old_name = session.get('name')
		if old_name  is not None and old_name != form.name.data:
			flash('Looks like you have changed your name')
		session['name']=form.name.data
		return redirect(url_for('index'))
	return render_template('index.html',form=form,name=session.get('name'))

@app.route('/1')
def index1():
	return render_template('1.html',current_time=datetime.utcnow())

@app.route('/user/<name>')
def user(name):
	return render_template('user.html',name=name+'a')

@app.route('/useragent')
def index2():
	user_agent= request.headers.get('User-agent')
	return '<p>your brower is %s</p>'% user_agent


if __name__=='__main__':
	manager.run()

