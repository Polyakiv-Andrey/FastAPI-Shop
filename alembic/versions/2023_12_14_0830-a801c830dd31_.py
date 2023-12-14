"""empty message

Revision ID: a801c830dd31
Revises: c93cdbfaec65
Create Date: 2023-12-14 08:30:26.823053

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a801c830dd31'
down_revision = 'c93cdbfaec65'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction',
    sa.Column('order_uuid', sa.String(), nullable=False),
    sa.Column('transaction_status', sa.Enum('success', 'pending', 'failed', name='transaction_status', create_constraint=True), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('currency', sa.String(), nullable=False),
    sa.Column('data_created', sa.DateTime(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('order_uuid')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transaction')
    # ### end Alembic commands ###