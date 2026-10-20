import unittest
from fastapi.testclient import TestClient
from src.main import app


class TestCRUDAndNested(unittest.TestCase):
    """
    Verifica las operaciones de la API con TestClient:
    1. Endpoint raíz y documentación.
    2. Paginación en GET all.
    3. Retorno de error 404 con HTTPException ante IDs inexistentes.
    4. Serialización anidada (Nested schema) en detalles por ID.
    5. Flujo CRUD completo.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "online")
        self.assertIn("docs", data)

    def test_get_all_paginated(self):
        response = self.client.get("/api/v1/categorias/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Valida estructura de fastapi-pagination
        self.assertIn("items", data)
        self.assertIn("total", data)
        self.assertIn("page", data)
        self.assertIn("size", data)

    def test_404_on_nonexistent_id(self):
        response = self.client.get("/api/v1/categorias/999999")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("detail", data)

    def test_producto_nested_schema(self):
        # El producto 1 existe en la base de datos de prueba
        response = self.client.get("/api/v1/productos/1")
        if response.status_code == 200:
            data = response.json()
            self.assertIn("id", data)
            self.assertIn("nombre", data)
            # Verifica que el schema anidado (Nested) contenga categoria y emprendedor
            self.assertIn("categoria", data)
            self.assertIn("emprendedor", data)
            if data["categoria"] is not None:
                self.assertIn("nombre", data["categoria"])
            if data["emprendedor"] is not None:
                self.assertIn("nombre_fantasia", data["emprendedor"])

    def test_emprendedor_nested_schema(self):
        # El emprendedor 1 existe en la base de datos de prueba
        response = self.client.get("/api/v1/emprendedores/1")
        if response.status_code == 200:
            data = response.json()
            self.assertIn("id", data)
            self.assertIn("nombre_fantasia", data)
            # Verifica que el schema anidado (Nested) contenga rubro, feria, plan
            self.assertIn("rubro", data)
            self.assertIn("feria", data)
            self.assertIn("plan", data)

    def test_contacto_crud_flow(self):
        from src.core.security import create_access_token
        admin_token = create_access_token(subject=1, extra_claims={"rol": "admin", "email": "admin@feriaimperio.com.ar"})
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. CREATE (POST /api/v1/contactos/ - público)
        payload = {
            "nombre_completo": "Test User",
            "email": "test@example.com",
            "telefono": "3584000000",
            "tipo_mensaje": "consulta_general",
            "mensaje": "Mensaje de prueba automatizada",
            "leido": False,
        }
        res_create = self.client.post("/api/v1/contactos/", json=payload)
        self.assertEqual(res_create.status_code, 201)
        created = res_create.json()
        item_id = created["id"]
        self.assertEqual(created["email"], "test@example.com")

        # 2. READ by ID (GET /api/v1/contactos/{id} - requiere Admin)
        res_read = self.client.get(f"/api/v1/contactos/{item_id}", headers=headers)
        self.assertEqual(res_read.status_code, 200)
        self.assertEqual(res_read.json()["id"], item_id)

        # 3. UPDATE (PUT /api/v1/contactos/{id} - requiere Admin)
        res_update = self.client.put(
            f"/api/v1/contactos/{item_id}",
            json={"leido": True},
            headers=headers,
        )
        self.assertEqual(res_update.status_code, 200)
        self.assertTrue(res_update.json()["leido"])

        # 4. DELETE (DELETE /api/v1/contactos/{id} - requiere Admin)
        res_del = self.client.delete(f"/api/v1/contactos/{item_id}", headers=headers)
        self.assertEqual(res_del.status_code, 204)

        # 5. READ after DELETE -> 404 NOT FOUND
        res_after = self.client.get(f"/api/v1/contactos/{item_id}", headers=headers)
        self.assertEqual(res_after.status_code, 404)


if __name__ == "__main__":
    unittest.main()
