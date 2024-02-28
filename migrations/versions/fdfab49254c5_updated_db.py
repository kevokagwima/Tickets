"""Updated db

Revision ID: fdfab49254c5
Revises: 
Create Date: 2024-02-27 15:13:52.761742

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fdfab49254c5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Bookings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ticket', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'Pricing', ['ticket'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Bookings', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('ticket')

    # ### end Alembic commands ###