import os
import unittest
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic import command


class TestAlembicMigrations(unittest.TestCase):
    """
    Verifica los requisitos de migraciones con Alembic:
    1. Archivo alembic.ini en la raíz.
    2. Directorio alembic/versions con al menos una migración inicial.
    3. Que la migración inicial contenga revision id válido.
    """

    def test_alembic_ini_exists(self):
        self.assertTrue(os.path.exists("alembic.ini"), "alembic.ini no existe en la raíz")

    def test_alembic_versions_exist(self):
        self.assertTrue(os.path.exists("alembic/versions"), "alembic/versions no existe")
        version_files = [f for f in os.listdir("alembic/versions") if f.endswith(".py")]
        self.assertGreaterEqual(len(version_files), 1, "Debe existir al menos una migración inicial")

    def test_alembic_script_directory_loads(self):
        cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(cfg)
        head = script.get_current_head()
        self.assertIsNotNone(head, "Alembic debe contar con un revision head válido")


if __name__ == "__main__":
    unittest.main()
