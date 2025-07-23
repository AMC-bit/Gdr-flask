"""Aggiunto campo ruolo alla tabella user

Revision ID: ec2e022a5e18
Revises: 
Create Date: 2025-07-23 11:32:13.212375

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec2e022a5e18'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Verifica se la colonna ruolo esiste già
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('user')]

    if 'ruolo' not in columns:
        # 1. Aggiungi la colonna ruolo come nullable con default 'PLAYER'
        with op.batch_alter_table('user', schema=None) as batch_op:
            batch_op.add_column(sa.Column('ruolo', sa.String(10), nullable=True, server_default='PLAYER'))

        # 2. Aggiorna tutti i record esistenti con 'PLAYER'
        op.execute("UPDATE user SET ruolo = 'PLAYER' WHERE ruolo IS NULL OR ruolo = ''")

        # 3. Ora rendi la colonna NOT NULL (senza batch_alter per evitare problemi)
        # SQLite accetterà questo perché tutti i valori sono già impostati
        op.execute("PRAGMA foreign_keys=off")
        op.execute("""
            CREATE TABLE user_new AS SELECT
                id, nome, email, password_hash, crediti, character_ids,
                CASE WHEN ruolo IS NULL OR ruolo = '' THEN 'PLAYER' ELSE ruolo END as ruolo
            FROM user
        """)
        op.execute("DROP TABLE user")
        op.execute("ALTER TABLE user_new RENAME TO user")
        op.execute("PRAGMA foreign_keys=on")

    # ### end Alembic commands ###


def downgrade():
    # 1. Crea tabella temporanea senza la colonna 'ruolo'
    op.create_table(
        'user_tmp',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('nome', sa.String(80), nullable=False),
        sa.Column('email', sa.String(80), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(128), nullable=False),
        sa.Column('crediti', sa.Float, nullable=False),
        sa.Column('character_ids', sa.Text, nullable=False, server_default='[]'),
    )
    # 2. Copia i dati dalla tabella attuale
    op.execute("""
        INSERT INTO user_tmp (id, nome, email, password_hash, crediti, character_ids)
        SELECT id, nome, email, password_hash, crediti, character_ids FROM user
    """)
    # 3. Elimina la tabella attuale
    op.drop_table('user')
    # 4. Rinomina la tabella temporanea
    op.rename_table('user_tmp', 'user')
