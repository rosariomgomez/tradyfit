"""added latitude and longitude to item

Revision ID: e0673de42c3
Revises: 7d03c5d0603
Create Date: 2015-04-17 17:38:49.409825

"""

# revision identifiers, used by Alembic.
revision = 'e0673de42c3'
down_revision = '7d03c5d0603'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('latitude', sa.Numeric(precision=10, scale=6), nullable=True))
    op.add_column('items', sa.Column('longitude', sa.Numeric(precision=10, scale=6), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('items', 'longitude')
    op.drop_column('items', 'latitude')
    ### end Alembic commands ###
