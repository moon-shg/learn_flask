from . import api
from ..models import Comment
from flask import jsonify, request, current_app, url_for


# 请求所有评论
@api.route('/comments/')
def get_comments():
	page = request.args.get('page', 1, type=int)
	pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
		error_out=False)
	prev = None
	if pagination.has_prev:
		prev = url_for('api.get_comments', prev=prev-1)
	next = None
	if pagination.has_prev:
		next = url_for('api.get_comments', next=next+1)
	comments = pagination.items
	return jsonify({ 'comment' : [ comment.to_json() for comment in comments ],
		'prev_url': prev,
		'next_url': next,
		'count':pagination.total
		 })


#请求一条评论
@api.route('/comments/<int:id>')
def get_comment(id):
	comment = Comment.query.get_or_404(id)
	return jsonify(comment.to_json())