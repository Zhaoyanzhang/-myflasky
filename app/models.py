from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

#lastest edit at page 97, chapter 9. add permission
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    def __repr__(self):
        return '<Role %r>' % self.name

    #permission var
    default=db.Column(db.Boolean,default=False,index=True)
    permissions=db.Column(db.Integer)
    
    #permission functions
    @staticmethod
    def insert_roles():
        roles=\
            {
            'User':(Permission.FOLLOW|\
                    Permission.COMMENT|\
                    Permission.WRITE_ARTICLES,True),
            'Moderator':(   Permission.FOLLOW|\
                            Permission.COMMENT|\
                            Permission.WRITE_ARTICLES|\
                            Permission.MODERATE_COMMENTS,False),
            'Administrator':(0xff,False)
            }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions=roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

# page97, chapter 9, add permission
class Permission:
    FOLLOW  =           0b00000001
    COMMENT=            0b00000010
    WRITE_ARTICLES=     0b00000100
    MODERATE_COMMENTS=  0b00001000
    ADMINISTER=         0b10000000




# page 99,chapter 9. Add Role with permissions to User
class User(UserMixin,db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash=db.Column(db.String(128))
    confirmed =db.Column(db.Boolean,default=False)

    @property
    def password(self):
        raise AttributeError ('password is not a readable attribute')
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    #callback for Users via Flask_login, to support flask-login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    #confirm User 8.6
    def generate_confirmation_token(self,expiration=3600):
        s=Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})
    def confirm(self,token):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return False
        if data.get('confirm')!=self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username


    # chapter 9. Add role's permission to User once User is init
    #   One account is set to ADMIN, others is ordinary User
    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
    #   chapter 9, Method to detect whether the user has the specified permission. 
    def can(self,permissions):
        return self.role is not None and\
            (self.role.permissions & permissions) == permissions
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

#chapter 9, in order to keep consistant in permission detect method, Anonymous Class is created.
class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False
    def is_administrator(self):
        return False

login_manager.anonyous_user = AnonymousUser



















