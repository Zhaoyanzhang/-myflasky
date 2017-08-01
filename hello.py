from flask import Flask,session,redirect,url_for,flash
from flask import request
from flask import render_template
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
import os
from flask_script import Shell
from flask_migrate import Migrate, MigrateCommand

basedir=os.path.abspath(os.path.dirname(__name__))

app = Flask(__name__)
app.config['SECRET_KEY']='hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

manager = Manager(app)
bootstrap=Bootstrap(app)
moment=Moment(app)
db=SQLAlchemy(app)
migrate=Migrate(app,db)
manager.add_command('db',MigrateCommand)

class Role(db.Model):
	__tablename__='roles'
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(64),unique=True)
	users=db.relationship('User',backref='role')
	def __repr__(self):
		return '<Role %r>'% self.name
class User(db.Model):
	__tablename__='users'
	id=db.Column(db.Integer,primary_key=True)
	username=db.Column(db.String(64),unique=True,index=True)
	role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
	def __repr__(self):
		return '<User %r>'% self.username

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

def make_shell_context():
	return dict(app=app,db=db,User=User,Role=Role)
manager.add_command("shell",Shell(make_context=make_shell_context))


@app.route('/',methods=['GET','POST'])
def index():
	form =NameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.name.data).first()
		if user is None:
			user=User(username=form.name.data)
			db.session.add(user)
			session['known']=False
		else:
			session['known']=True
		session['name']=form.name.data
		form.name.data = ''
		return redirect(url_for('index'))
	return render_template('index.html',form=form,name=session.get('name'),known=session.get('known',False))

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

