"""empty message

Revision ID: 13a4650f65a5
Revises: c135a4d3e34b
Create Date: 2021-08-22 11:39:20.848113

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '13a4650f65a5'
down_revision = 'c135a4d3e34b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('hoster_1_repositories_complete')
    op.drop_column('gitea_repositories', 'is_completed')
    op.drop_column('github_repositories', 'is_completed')
    op.drop_column('gitlab_repositories', 'is_completed')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gitlab_repositories', sa.Column('is_completed', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('github_repositories', sa.Column('is_completed', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('gitea_repositories', sa.Column('is_completed', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.create_table('hoster_1_repositories_complete',
    sa.Column('id', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('gitea_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('owner_username', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('empty', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('private', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('fork', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('mirror', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('size', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('website', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('stars_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('forks_count', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('watchers_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('open_issues_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('default_branch', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('pushed_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('hosting_service_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('html_url', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
    sa.Column('is_completed', sa.BOOLEAN(), autoincrement=False, nullable=True)
    )
    # ### end Alembic commands ###
