from flask import render_template, session, redirect, url_for, current_app,flash,request
from .. import db
from ..models import User,Role,Post
from ..email import send_email
from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm,PostForm
from flask_login import current_user

@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and\
            form.validate_on_submit():
        post=Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
#   posts=Post.query.order_by(Post.timestamp.desc()).all()
    page=request.args.get('page',1,type=int)
    pagination=Post.query.order_by(Post.timestamp.desc()).paginate(\
            page,per_page=15,error_out=False)
    posts=pagination.items
    return render_template('index.html',form=form,posts=posts,pagination=pagination)



# For Page 101 , try my own decorators
from ..decorators import admin_required,permission_required
from flask_login import login_required
from ..models import Permission

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
	return "For Admins page 101"

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
	return 'For comment moderators'

# chapter 10, prepare a webpage for each user to show their own info.
@main.route('/user/<username>')
def user(username):
    user= User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page',1,type=int)
    pagination= user.posts.order_by(Post.timestamp.desc()).paginate\
            (page,per_page=15,error_out=False)
    posts=pagination.items
    return render_template('user.html',user=user,posts=posts,pagination=pagination)



# chapter 10, prepare a webpage for user to edit their profile
@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name=form.name.data
        current_user.location=form.location.data
        current_user.about_me=form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated')
        return redirect(url_for('.user',username=current_user.username))
    form.name.data=current_user.name
    form.location.data=current_user.location
    form.about_me.data=current_user.about_me
    return render_template('edit_profile.html',form=form)

@main.route('/edit-profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user=User.query.get_or_404(id)
    form=EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email=form.email.data
        user.username=form.username.data
        user.confirmed=form.confirmed.data
        user.role=Role.query.get(form.role.data)
        user.name=form.name.data
        user.location=form.location.data
        user.about_me=form.about_me.data
        db.session.add(user)
        flash('The profile has been updated')
        return redirect(url_for('.user',username=user.username))
    form.email.data=user.email
    form.username.data=user.username
    form.confirmed.data=user.confirmed
    form.role.data=user.role_id
    form.name.data=user.name
    form.location.data=user.location
    form.about_me.data=user.about_me
    return render_template('edit_profile.html',form=form,user=user)


#chapter11 create a page for each post
@main.route('/post/<int:id>')
def post(id):
    post= Post.query.get_or_404(id)
    return render_template('post.html',posts=[post])

#chapter11 page for update/edit current post
@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post=Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body=form.body.data
        db.session.add(post)
        flash('The post has been updated')
        return redirect(url_for('.post',id=post.id))
    form.body.data=post.body
    return render_template('edit_post.html',form=form)












