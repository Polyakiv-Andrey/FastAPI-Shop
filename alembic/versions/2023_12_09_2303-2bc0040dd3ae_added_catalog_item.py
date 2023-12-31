"""added catalog item

Revision ID: 2bc0040dd3ae
Revises: 3f828b95fb61
Create Date: 2023-12-09 23:03:54.590780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2bc0040dd3ae'
down_revision = '3f828b95fb61'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('catalogitem',
    sa.Column('item_name', sa.String(), nullable=False),
    sa.Column('item_image_url', sa.String(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('catalogitem')
    # ### end Alembic commands ###
