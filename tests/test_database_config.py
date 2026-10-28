"""Testes da selecao de banco em ambiente serverless."""
import os
import tempfile
import unittest
from unittest.mock import patch

from backend.database import _usar_postgres, get_connection, get_database_url


class TestDatabaseConfiguration(unittest.TestCase):
    def setUp(self):
        self.no_database_env = {
            "DATABASE_URL": "",
            "POSTGRES_URL": "",
            "POSTGRES_PRISMA_URL": "",
            "POSTGRES_URL_NON_POOLING": "",
            "PGHOST": "",
            "PGDATABASE": "",
        }

    def test_vercel_fails_closed_without_persistent_postgres(self):
        """Vercel nao deve silently usar SQLite temporario quando falta URL."""
        with patch.dict(os.environ, {**self.no_database_env, "VERCEL": "1"}, clear=False):
            self.assertEqual(get_database_url(), "")
            self.assertFalse(_usar_postgres())
            with self.assertRaisesRegex(RuntimeError, "Banco persistente nao configurado na Vercel"):
                get_connection()

    def test_explicit_test_database_path_still_uses_sqlite(self):
        """Testes com caminho explicito continuam isolados em SQLite."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = os.path.join(tmp_dir, "test.db")
            with patch.dict(os.environ, {**self.no_database_env, "VERCEL": "1"}, clear=False):
                conn = get_connection(db_path=db_path)
                try:
                    result = conn.execute("SELECT 1").fetchone()[0]
                    self.assertEqual(result, 1)
                finally:
                    conn.close()

    def test_postgres_url_from_marketplace_is_detected(self):
        """URLs de integracoes Marketplace sao reconhecidas para selecionar PostgreSQL."""
        with patch.dict(os.environ, {"VERCEL": "1", "POSTGRES_URL": "postgresql://user:pass@db.example.test/app"}, clear=False):
            self.assertTrue(_usar_postgres())
            self.assertEqual(get_database_url(), "postgresql://user:pass@db.example.test/app")


if __name__ == "__main__":
    unittest.main()
