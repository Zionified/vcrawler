"""html source table

Revision ID: 893a7e075a03
Revises: 3667ec7b8326
Create Date: 2023-06-26 00:07:14.157845

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '893a7e075a03'
down_revision = '3667ec7b8326'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('source_html',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='id'),
    sa.Column('source', sa.String(length=1024), nullable=False, comment='source url'),
    sa.Column('source_hash', sa.String(length=32), nullable=False, comment='shorter url'),
    sa.Column('content', sa.Text(), nullable=False, comment='html'),
    sa.Column('create_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='movie length(in seconds)'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('source_hash', name='uniq_idx_source_hash')
    )
    op.add_column('movie', sa.Column('cover', sa.Text(), nullable=False, comment='movie cover'))
    op.add_column('movie', sa.Column('description', sa.Text(), nullable=False, comment='movie description'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('movie', 'description')
    op.drop_column('movie', 'cover')
    op.drop_table('source_html')
    # ### end Alembic commands ###