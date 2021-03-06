"""empty message

Revision ID: 5d848561ada8
Revises: acc24b8d35a2
Create Date: 2021-12-28 17:59:48.928696

"""
from alembic import op
import sqlalchemy as sa

from models import Artist


# revision identifiers, used by Alembic.
revision = "5d848561ada8"
down_revision = "acc24b8d35a2"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("artists", sa.Column("joined_at", sa.DateTime(), nullable=True))
    op.add_column("venues", sa.Column("joined_at", sa.DateTime(), nullable=True))
    op.execute(
        "UPDATE artists SET joined_at = '1970-01-01 00:00:00' WHERE joined_at IS NULL"
    )
    op.execute(
        "UPDATE venues SET joined_at = '1970-01-01 00:00:00' WHERE joined_at IS NULL"
    )
    op.alter_column("artists", "joined_at", nullable=False)
    op.alter_column("venues", "joined_at", nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("venues", "joined_at")
    op.drop_column("artists", "joined_at")
    # ### end Alembic commands ###
