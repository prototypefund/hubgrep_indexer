import click
from flask import Blueprint, render_template
from flask import current_app as app, request

cli_bp = Blueprint("cli", __name__)

from crawler_controller.models.platforms import Platform
from crawler_controller import db

@cli_bp.cli.command()
def init_db():
    db.create_all()
    #user_datastore.create_user(email="test@me.com", password=hash_password("password"))
    db.session.commit()


@cli_bp.cli.command()
@click.argument('platform_type')
@click.argument('base_url')
def add_platform(platform_type, base_url):
    if not Platform.query.filter_by(platform_type=platform_type, base_url=base_url).first():
        platform = Platform()
        platform.platform_type = platform_type
        platform.base_url = base_url
        db.session.add(platform)
        db.session.commit()
    else:
        print(f'{base_url} already exists')

@cli_bp.cli.command()
@click.argument('platform_type')
@click.argument('base_url')
def del_platform(platform_type, base_url):
    platform = Platform.query.filter_by(platform_type=platform_type, base_url=base_url).first()
    if platform:
        db.session.delete(platform)
        db.session.commit()
    else:
        print(f'{platform_type} / {base_url} not found')
