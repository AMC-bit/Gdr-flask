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

    # Controlla se la tabella user esiste
    tables = inspector.get_table_names()
    if 'user' not in tables:
        # Se la tabella non esiste, creala da zero con la struttura completa
        op.create_table('user',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('nome', sa.String(80), nullable=False),
            sa.Column('email', sa.String(80), unique=True, nullable=False),
            sa.Column('password_hash', sa.String(128), nullable=False),
            sa.Column('crediti', sa.Float, nullable=False),
            sa.Column('character_ids', sa.Text, nullable=False, server_default='[]'),
            sa.Column('ruolo', sa.String(10), nullable=False, server_default='PLAYER'),
        )
        return

    columns = [col['name'] for col in inspector.get_columns('user')]
    columns_info = {col['name']: col for col in inspector.get_columns('user')}
    pk_constraint = inspector.get_pk_constraint('user')
    unique_constraints = inspector.get_unique_constraints('user')

    ruolo_missing = 'ruolo' not in columns

    critical_columns_problems = False
    missing_constraint = False
    id_problems = False

    if 'id' in columns_info:
        id_column = columns_info['id']
        # Controlla PRIMARY KEY
        id_is_pk = 'id' in pk_constraint.get('constrained_columns', [])
        # Controlla se è nullable
        id_nullable = id_column.get('nullable', True)

        if not id_is_pk or id_nullable:
            id_problems = True

    critical_columns = ['nome', 'email', 'password_hash', 'crediti']
    for col_name in critical_columns:
        if col_name in columns_info:
            if columns_info[col_name].get('nullable', True):  # Se nullable=True
                critical_columns_problems = True
                break

    for constraint in unique_constraints:
        if 'email' in constraint.get('column_names', []):
            missing_constraint = True
            break

    if 'character_ids' in columns_info and not missing_constraint:
        char_default= columns_info['character_ids'].get('server_default')
        if char_default != '[]' and char_default != "'[]'":
            missing_constraint = True

    if 'ruolo' in columns_info and not missing_constraint:
        ruolo_default = columns_info['ruolo'].get('server_default')
        if ruolo_default != 'PLAYER' and ruolo_default != "'PLAYER'":
            missing_constraint = True

    needs_rebuild = (
        ruolo_missing
        or missing_constraint
        or critical_columns_problems
        or id_problems
    )

    if needs_rebuild:
        op.execute("PRAGMA foreign_keys=off")

        # 1. Rinomino la tabella attuale
        op.execute("ALTER TABLE user RENAME TO user_old")

        # 2. Creo la nuova tabella con la struttura completa e corretta
        op.execute("""
            CREATE TABLE user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(80) NOT NULL,
                email VARCHAR(80) NOT NULL UNIQUE,
                password_hash VARCHAR(128) NOT NULL,
                crediti FLOAT NOT NULL,
                character_ids TEXT NOT NULL DEFAULT '[]',
                ruolo VARCHAR(10) NOT NULL DEFAULT 'PLAYER'
            )
        """)

        # 3.1 Costruzione della query di inserimento dinamica
        select_columns = []
        for col in ['id', 'nome', 'email', 'password_hash', 'crediti']:
            if col in columns:
                select_columns.append(col)
            else:
                # Gestione delle colonne mancanti con valori di default
                if col == 'crediti':
                    select_columns.append('100 as crediti')
                else:
                    select_columns.append(f"'' as {col}")

        # 3.2 Gestione di character_ids e ruolo
        if 'character_ids' in columns:
            select_columns.append("COALESCE(character_ids, '[]') as character_ids")
        else:
            select_columns.append("'[]' as character_ids")

        if 'ruolo' in columns:
            select_columns.append("COALESCE(ruolo, 'PLAYER') as ruolo")
        else:
            select_columns.append("'PLAYER' as ruolo")

        # 4. Esecuzione dell'inserimento
        op.execute(f"""
            INSERT INTO user (id, nome, email, password_hash, crediti, character_ids, ruolo)
            SELECT {', '.join(select_columns)}
            FROM user_old
        """)

        # 5. Drop della tabella vecchia
        op.execute("DROP TABLE user_old")

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
