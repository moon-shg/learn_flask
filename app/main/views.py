from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app, flash, request, make_response
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..models import User, Permission, Post, Role
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required

# 设置路由表
@main.route('/', methods=['GET','POST'])
def index():
	form = PostForm()
	# 提交博客
	if current_user.can(Permission.WRITE) and form.validate_on_submit():
		post = Post(body=form.body.data, author=current_user._get_current_object())
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('.index'))
	
	# 显示所有博客文章或只显示关注用户的文章
	show_followed = False
	if current_user.is_authenticated:
		show_followed = bool(request.cookies.get('show_followed', ''))
	if show_followed:
		query = current_user.followed_posts
	else:
		query = Post.query
		# 分页显示博客内容
	page = request.args.get('page', 1, type=int)
	pagination = query.order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], 
		error_out=False)
	posts = pagination.items
	return render_template('index.html', form = form, posts=posts, 
		show_followed=show_followed, pagination=pagination)

# 查询所有博客文章posts
@main.route('/all')
@login_required
def show_all():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed', '', max_age=30*24*60*60) #cookie 有效期为30天
	return resp
# 查询所关注用户的文章
@main.route('/followed')
@login_required
def show_followed():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
	return resp

# 个人主页路由
@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	if user is None:
		abort(404)
	page = request.args.get('page', 1, type=int)
	pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], 
		error_out=False)
	posts = pagination.items
	return render_template('user.html', user=user, posts=posts, pagination=pagination)

# 编辑个人资料页面路由
@main.route('/edit-profile', methods=['GET','POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user._get_current_object())
		db.session.commit()
		flash("个人资料已更新！")
		return redirect(url_for('.user', username=current_user.username))
	# 设置表单的初始值
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('/edit_profile.html', form=form)


# 管理员的资料编辑路由
@main.route('/edit-profile/<int:id>', methods=['GET','POST'])
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		db.session.commit()
		flash('用户资料已更新！')
		return redirect(url_for('.user', username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me
	return render_template('edit_profile.html', form=form, user=user)

# 为博客提供固定链接
@main.route('/post/<int:id>')
def post(id):
	post = Post.query.get_or_404(id)
	#虽然posts只有一个元素，但这里还是传递一个列表，这样就能够复用_posts.html来渲染post.html了
	return render_template('post.html', posts=[post]) 

# 编辑博客路由
@main.route('/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_post(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author and not current_user.can(Permission.ADMIN):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.body = form.body.data
		db.session.add(post)
		db.session.commit()
		flash('博客已更新！')
		return redirect(url_for('.post', id=post.id))
	form.body.data = post.body
	return render_template('/edit_post.html', form=form) 


# 关注和粉丝相关路由
# 关注用户
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户不存在！')
		return redirect(url_for('.index'))
	if current_user.is_following(user):
		flash('您已经关注ta了！')
		return redirect(url_for('.user', username=username))
	current_user.follow(user)
	db.session.commit()
	flash(f'关注{ username }成功')
	return redirect(url_for('.user', username=username))

# 取消关注
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户不存在！')
		return redirect(url_for('.index'))
	if not current_user.is_following(user):
		flash('您还未关注ta哦~')
		return redirect(url_for('.user', username=username))
	current_user.unfollow(user)
	db.session.commit()
	flash(f'您已取消关注{ username }。')
	return redirect(url_for('.user', username=username))

# 粉丝列表路由
@main.route('/followers/<username>')
@login_required
def followers(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户不存在！')
	page = request.args.get('page', 1, type=int)
	pagination = user.followers.paginate(page, 
		per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'], error_out=False)
	follows = [{ 'user': item.followers, 'timestamp':item.timestamp} \
		for item in pagination.items]
	return render_template('followers.html', user=user, title="的粉丝", 
		endpoint='.followers', pagination=pagination, follows=follows)

#他的关注列表路由
@main.route('/followed_by/<username>')
@login_required
def followed_by(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户不存在！')
	page = request.args.get('page', 1, type=int)
	pagination = user.followed.paginate(page, 
		per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'], error_out=False)
	follows = [{ 'user': item.followed, 'timestamp':item.timestamp} \
		for item in pagination.items]
	return render_template('followers.html', user=user, title="的关注", 
		endpoint='.followed_by', pagination=pagination, follows=follows)
