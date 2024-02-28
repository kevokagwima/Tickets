"""Updated db

Revision ID: e9a53c892630
Revises: 40e98fbe0776
Create Date: 2024-02-27 16:25:20.124409

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9a53c892630'
down_revision = '40e98fbe0776'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Bookings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ticket', sa.Integer(), nullable=True))
        batch_op.drop_constraint('FK__Bookings__total__19DFD96B', type_='foreignkey')
        batch_op.create_foreign_key(None, 'Pricing', ['ticket'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Bookings', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('FK__Bookings__total__19DFD96B', 'Pricing', ['total'], ['id'])
        batch_op.drop_column('ticket')

    # ### end Alembic commands ###