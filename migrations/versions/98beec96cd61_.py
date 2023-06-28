"""empty message

Revision ID: 98beec96cd61
Revises: cd4a02e19cb0
Create Date: 2023-06-25 13:52:32.527088

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98beec96cd61'
down_revision = 'cd4a02e19cb0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('artists', schema=None) as batch_op:
        batch_op.alter_column('facebook_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)
        batch_op.alter_column('image_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)
        batch_op.alter_column('website_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)

    with op.batch_alter_table('shows', schema=None) as batch_op:
        batch_op.add_column(sa.Column('artist_name', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('artist_image_link', sa.String(length=500), nullable=True))

    with op.batch_alter_table('venues', schema=None) as batch_op:
        batch_op.alter_column('facebook_link',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=500),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('venues', schema=None) as batch_op:
        batch_op.alter_column('facebook_link',
               existing_type=sa.String(length=500),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)

    with op.batch_alter_table('shows', schema=None) as batch_op:
        batch_op.drop_column('artist_image_link')
        batch_op.drop_column('artist_name')

    with op.batch_alter_table('artists', schema=None) as batch_op:
        batch_op.alter_column('website_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=False)
        batch_op.alter_column('image_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=False)
        batch_op.alter_column('facebook_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=False)

    # ### end Alembic commands ###