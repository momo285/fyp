"""empty message

Revision ID: c5d62877720e
Revises: 
Create Date: 2024-03-06 00:54:47.263154

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5d62877720e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('job',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description_filename', sa.String(length=100), nullable=False),
    sa.Column('logo_filename', sa.String(length=100), nullable=False),
    sa.Column('job_url', sa.String(length=200), nullable=True),
    sa.Column('values_category', sa.String(length=50), nullable=True),
    sa.Column('vision_category', sa.String(length=50), nullable=True),
    sa.Column('culture_category', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('startup',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password_hash', sa.String(length=200), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('companyName', sa.String(length=120), nullable=False),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.Column('industry', sa.String(length=120), nullable=True),
    sa.Column('url', sa.String(length=120), nullable=True),
    sa.Column('vision', sa.String(length=500), nullable=True),
    sa.Column('values', sa.String(length=500), nullable=True),
    sa.Column('culture', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password_hash', sa.String(length=200), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=True),
    sa.Column('university', sa.String(length=100), nullable=True),
    sa.Column('degree_program', sa.String(length=100), nullable=True),
    sa.Column('year_of_graduation', sa.String(length=4), nullable=True),
    sa.Column('values_type', sa.String(length=50), nullable=True),
    sa.Column('vision_type', sa.String(length=50), nullable=True),
    sa.Column('culture_type', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('student_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('university', sa.String(length=100), nullable=False),
    sa.Column('degree_program', sa.String(length=100), nullable=False),
    sa.Column('year_of_graduation', sa.String(length=4), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('student_info')
    op.drop_table('user')
    op.drop_table('startup')
    op.drop_table('job')
    # ### end Alembic commands ###
