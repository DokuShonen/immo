"""Application des migrations de base de donnees.

Usage :
    python migrate.py            applique les migrations en attente
    python migrate.py --status   affiche l'etat sans rien modifier

Le suivi des migrations est assure par la table schema_migrations, creee au
premier lancement. Les scripts du dossier migrations/ sont appliques dans
l'ordre lexicographique, chacun dans sa propre transaction.
"""
import os
import sys

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MIGRATIONS_DIR = os.path.join(BASE_DIR, "migrations")

CREATE_TRACKING = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


def connection():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL non définie dans l'environnement ou le fichier .env")
    return psycopg2.connect(url)


def applied_versions(conn):
    with conn.cursor() as cur:
        cur.execute(CREATE_TRACKING)
        conn.commit()
        cur.execute("SELECT version FROM schema_migrations")
        return {row[0] for row in cur.fetchall()}


def migration_files():
    if not os.path.isdir(MIGRATIONS_DIR):
        return []
    return sorted(
        f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".sql")
    )


def main():
    conn = connection()
    try:
        deja_faits = applied_versions(conn)
        fichiers = migration_files()
        en_attente = [f for f in fichiers if f not in deja_faits]

        if "--status" in sys.argv:
            print(f"migrations trouvees : {len(fichiers)}")
            print(f"deja appliquees    : {len(deja_faits)}")
            for f in en_attente:
                print(f"  en attente : {f}")
            return 0

        if not en_attente:
            print("La base est a jour, aucune migration a appliquer.")
            return 0

        for fichier in en_attente:
            chemin = os.path.join(MIGRATIONS_DIR, fichier)
            with open(chemin, encoding="utf-8") as f:
                sql = f.read()
            print(f"Application de {fichier} ...", end=" ")
            with conn.cursor() as cur:
                try:
                    cur.execute(sql)
                    cur.execute(
                        "INSERT INTO schema_migrations (version) VALUES (%s)", (fichier,)
                    )
                    conn.commit()
                    print("ok")
                except Exception as exc:
                    conn.rollback()
                    print("echec")
                    print(f"   {exc}")
                    return 1
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
