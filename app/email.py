from threading import threading
from flask	import current_app, render_tamplate
from flask import Message
from . import mail

#创建异步发送邮件的函数，使处理发送邮件的请求在后台线程中运行
def send_async_email(app, msg): 
	with app.app_context():
		mail.send(msg)

def send_email(to, subject, template, **kwargs):
	msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, \
		sender = app.config['FLASKY_MAIL_SENDER'], recipients=[to])
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	thr = Thread(target=send_async_email, args=[app, msg])
	thr.start()
	return thr