"""auth models

Revision ID: 3f828b95fb61
Revises: 
Create Date: 2023-12-09 20:55:36.593147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f828b95fb61'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('otp',
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('otp_code', sa.String(), nullable=False),
    sa.Column('data_created', sa.DateTime(), nullable=False),
    sa.Column('otp_type', sa.Enum('registration', 'change_password', name='otp_type', create_constraint=True), nullable=False),
    sa.Column('attempt', sa.Integer(), nullable=False),
    sa.Column('used', sa.Boolean(), nullable=False),
    sa.Column('confirmed', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tokenblacklist',
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.LargeBinary(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('data_created', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('tokenblacklist')
    op.drop_table('otp')
    # ### end Alembic commands ###
