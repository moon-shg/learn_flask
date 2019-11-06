import os
from app import creat_app, db
from app.modle import User, Role
from flask_migrate import Migrate


app = create-app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)
