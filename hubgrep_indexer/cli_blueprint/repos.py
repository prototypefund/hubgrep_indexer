import os
import click
from flask import current_app
from pathlib import Path
import logging

from hubgrep_indexer.models.hosting_service import HostingService, Export

from hubgrep_indexer.cli_blueprint import cli_bp
from hubgrep_indexer import db

logger = logging.getLogger(__name__)


@cli_bp.cli.command()
@click.argument("hosting_service")
def export_repos(hosting_service):
    hosting_service: HostingService = HostingService.query.filter_by(
        api_url=hosting_service
    ).first()

    print(f"exporting raw repositories for {hosting_service}")
    export = hosting_service.export_repositories(unified=False)
    print(f"exported to {export.file_path}")
    db.session.add(export)
    db.session.commit()

    print(f"exporting unified repositories for {hosting_service}")
    export = hosting_service.export_repositories(unified=True)
    print(f"exported to {export.file_path}")
    db.session.add(export)
    db.session.commit()




@cli_bp.cli.command(help="remove old exports, keep the newest ones")
@click.option("--keep", type=int, default=3)
@click.option(
    "--hosting-service",
    type=str,
    help="api_url of the hosting service (eg. https://api.github.com/)",
)
def cleanup_exports(keep, hosting_service=None):
    """
    remove old exports from the hdd and their references from the db.
    only keep the last <keep> exports.
    """
    if hosting_service:
        q = HostingService.query.filter_by(api_url=hosting_service)
    else:
        q = HostingService.query
    for hosting_service in q.all():
        old_exports_raw = (
            Export.query.filter_by(hosting_service_id=hosting_service.id, is_raw=True)
            .order_by(Export.created_at.desc())
            .offset(keep)
        )
        old_exports_unified = (
            Export.query.filter_by(hosting_service_id=hosting_service.id, is_raw=False)
            .order_by(Export.created_at.desc())
            .offset(keep)
        )

        for export in old_exports_raw:
            print(f"deleting export {export}")
            export.delete_file()
            db.session.delete(export)
        for export in old_exports_unified:
            print(f"deleting export {export}")
            export.delete_file()
            db.session.delete(export)
        db.session.commit()
