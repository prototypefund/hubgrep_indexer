import logging
import os
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from crawler_controller.lib.init_logging import init_logging
from flask_security import Security, SQLAlchemyUserDatastore, auth_required, hash_password

db = SQLAlchemy()

migrate = Migrate()
logger = logging.getLogger(__name__)


# fix keep-alive in dev server (dropped connections from client sessions)
from werkzeug.serving import WSGIRequestHandler
WSGIRequestHandler.protocol_version = "HTTP/1.1"

def create_app():
    app = Flask(__name__)

    app_env = os.environ.get('APP_ENV', 'development')
    config_mapping = {
        'development': 'crawler_controller.lib.config.DevelopmentConfig',
        'production': 'crawler_controller.lib.config.ProductionConfig',
        'testing': 'crawler_controller.lib.config.testingConfig',
    }

    app.config.from_object(config_mapping[app_env])

    init_logging(loglevel=app.config['LOGLEVEL'])

    db.init_app(app)
    migrate.init_app(app, db=db)


    from crawler_controller.models.github import GitHubUser, GithubRepo
    from crawler_controller.models.user import Role, User

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    from crawler_controller.api_blueprint import api
    from crawler_controller.frontend_blueprint import frontend
    from crawler_controller.cli_blueprint import cli_bp
    app.register_blueprint(api)
    app.register_blueprint(frontend)
    app.register_blueprint(cli_bp)


    return app




