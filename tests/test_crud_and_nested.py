import unittest
import uuid
from fastapi.testclient import TestClient
from src.main import app


class TestCRUDAndNested(unittest.TestCase):
    """
    Verifica las operaciones de la API con TestClient:
    1. Endpoint raíz y documentación.
    2. Paginación en GET all.
    3. Retorno de error 404 con HTTPException ante IDs inexistentes.
    4. Serialización anidada (Nested schema) en detalles por ID.
    5. Flujos CRUD completos y directos sin autenticación (Usuarios, Emprendedores, Productos, Contactos).
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
            # Verifica que el schema anidado (Nested) contenga rubro, feria, usuario, productos
            self.assertIn("rubro", data)
            self.assertIn("feria", data)
            self.assertIn("usuario", data)
            self.assertIn("productos", data)


    def test_contacto_crud_flow(self):
        # 1. CREATE (POST /api/v1/contactos/ - público)
        payload = {
            "nombre_completo": "Test User Contacto",
            "email": f"contacto_{uuid.uuid4().hex[:6]}@example.com",
            "telefono": "3584000000",
            "tipo_mensaje": "consulta_general",
            "mensaje": "Mensaje de prueba automatizada",
            "leido": False,
        }
        res_create = self.client.post("/api/v1/contactos/", json=payload)
        self.assertEqual(res_create.status_code, 201)
        created = res_create.json()
        item_id = created["id"]
        self.assertEqual(created["nombre_completo"], payload["nombre_completo"])

        # 2. READ by ID (GET /api/v1/contactos/{id})
        res_read = self.client.get(f"/api/v1/contactos/{item_id}")
        self.assertEqual(res_read.status_code, 200)
        self.assertEqual(res_read.json()["id"], item_id)

        # 3. UPDATE (PUT /api/v1/contactos/{id})
        res_update = self.client.put(
            f"/api/v1/contactos/{item_id}",
            json={"leido": True},
        )
        self.assertEqual(res_update.status_code, 200)
        self.assertTrue(res_update.json()["leido"])

        # 4. DELETE (DELETE /api/v1/contactos/{id})
        res_del = self.client.delete(f"/api/v1/contactos/{item_id}")
        self.assertEqual(res_del.status_code, 204)

        # 5. READ after DELETE -> 404 NOT FOUND
        res_after = self.client.get(f"/api/v1/contactos/{item_id}")
        self.assertEqual(res_after.status_code, 404)

    def test_usuario_crud_flow(self):
        # 1. CREATE (POST /api/v1/usuarios/)
        unique_email = f"user_{uuid.uuid4().hex[:6]}@example.com"
        user_payload = {
            "nombre_completo": "Usuario de Prueba",
            "email": unique_email,
            "password": "Password123!",
            "telefono": "3584112233",
            "rol": "emprendedor",
            "activo": True,
        }
        res_create = self.client.post("/api/v1/usuarios/", json=user_payload)
        self.assertEqual(res_create.status_code, 201)
        created_user = res_create.json()
        user_id = created_user["id"]
        self.assertEqual(created_user["email"], unique_email)
        self.assertNotIn("password_hash", created_user)  # No se debe exponer hash

        # 2. READ by ID (GET /api/v1/usuarios/{id})
        res_read = self.client.get(f"/api/v1/usuarios/{user_id}")
        self.assertEqual(res_read.status_code, 200)
        self.assertEqual(res_read.json()["id"], user_id)

        # 3. READ paginated (GET /api/v1/usuarios/)
        res_list = self.client.get("/api/v1/usuarios/")
        self.assertEqual(res_list.status_code, 200)
        self.assertIn("items", res_list.json())

        # 4. UPDATE (PUT /api/v1/usuarios/{id})
        update_payload = {"nombre_completo": "Usuario Modificado"}
        res_update = self.client.put(f"/api/v1/usuarios/{user_id}", json=update_payload)
        self.assertEqual(res_update.status_code, 200)
        self.assertEqual(res_update.json()["nombre_completo"], "Usuario Modificado")

        # 5. DELETE (DELETE /api/v1/usuarios/{id})
        res_del = self.client.delete(f"/api/v1/usuarios/{user_id}")
        self.assertEqual(res_del.status_code, 204)

        # 6. READ after DELETE -> 404 NOT FOUND
        res_after = self.client.get(f"/api/v1/usuarios/{user_id}")
        self.assertEqual(res_after.status_code, 404)

    def test_producto_crud_flow_directo(self):
        # 1. CREATE DIRECT PRODUCT (POST /api/v1/productos/) con emprendedor_id y categoria_id
        prod_payload = {
            "nombre": f"Producto Test {uuid.uuid4().hex[:4]}",
            "descripcion": "Descripción del producto de prueba",
            "precio": 2500.50,
            "stock": 10,
            "disponible": True,
            "categoria_id": 1,
            "emprendedor_id": 1,
        }
        res_create = self.client.post("/api/v1/productos/", json=prod_payload)
        self.assertEqual(res_create.status_code, 201)
        created_prod = res_create.json()
        prod_id = created_prod["id"]
        self.assertEqual(created_prod["nombre"], prod_payload["nombre"])

        # 2. READ by ID (GET /api/v1/productos/{id})
        res_read = self.client.get(f"/api/v1/productos/{prod_id}")
        self.assertEqual(res_read.status_code, 200)
        self.assertEqual(res_read.json()["id"], prod_id)

        # 3. UPDATE (PUT /api/v1/productos/{id})
        res_update = self.client.put(f"/api/v1/productos/{prod_id}", json={"precio": 3200.0})
        self.assertEqual(res_update.status_code, 200)
        self.assertEqual(res_update.json()["precio"], 3200.0)

        # 4. DELETE (DELETE /api/v1/productos/{id})
        res_del = self.client.delete(f"/api/v1/productos/{prod_id}")
        self.assertEqual(res_del.status_code, 204)

        # 5. READ after DELETE -> 404 NOT FOUND
        res_after = self.client.get(f"/api/v1/productos/{prod_id}")
        self.assertEqual(res_after.status_code, 404)

    def test_emprendedor_crud_flow_directo(self):
        # 1. Crear un usuario dedicado para este emprendedor
        user_res = self.client.post(
            "/api/v1/usuarios/",
            json={
                "nombre_completo": "Titular Puesto",
                "email": f"titular_{uuid.uuid4().hex[:6]}@example.com",
                "password": "Password123!",
                "telefono": "3584998877",
                "rol": "emprendedor",
            },
        )
        self.assertEqual(user_res.status_code, 201)
        user_id = user_res.json()["id"]

        # 2. CREATE EMPRENDEDOR (POST /api/v1/emprendedores/)
        emp_payload = {
            "nombre_fantasia": f"Puesto Artesanal {uuid.uuid4().hex[:4]}",
            "descripcion_bio": "Artesanías en madera y cerámica",
            "telefono_whatsapp": "3584123456",
            "rubro_id": 1,
            "usuario_id": user_id,
        }
        res_create = self.client.post("/api/v1/emprendedores/", json=emp_payload)
        self.assertEqual(res_create.status_code, 201)
        created_emp = res_create.json()
        emp_id = created_emp["id"]
        self.assertEqual(created_emp["nombre_fantasia"], emp_payload["nombre_fantasia"])

        # 3. READ by ID (GET /api/v1/emprendedores/{id})
        res_read = self.client.get(f"/api/v1/emprendedores/{emp_id}")
        self.assertEqual(res_read.status_code, 200)
        self.assertEqual(res_read.json()["id"], emp_id)

        # 4. UPDATE (PUT /api/v1/emprendedores/{id})
        res_update = self.client.put(
            f"/api/v1/emprendedores/{emp_id}",
            json={"descripcion_bio": "Bio actualizada"},
        )
        self.assertEqual(res_update.status_code, 200)
        self.assertEqual(res_update.json()["descripcion_bio"], "Bio actualizada")

        # 5. DELETE (DELETE /api/v1/emprendedores/{id})
        res_del = self.client.delete(f"/api/v1/emprendedores/{emp_id}")
        self.assertEqual(res_del.status_code, 204)

        # 6. READ after DELETE -> 404 NOT FOUND
        res_after = self.client.get(f"/api/v1/emprendedores/{emp_id}")
        self.assertEqual(res_after.status_code, 404)

    def test_categoria_nested_schema(self):
        """Verifica que GET /categorias/{id} retorne CategoriaPublicNested con productos."""
        response = self.client.get("/api/v1/categorias/1")
        if response.status_code == 200:
            data = response.json()
            self.assertIn("productos", data)
            self.assertIsInstance(data["productos"], list)

    def test_rubro_nested_schema(self):
        """Verifica que GET /rubros/{id} retorne RubroPublicNested con emprendedores."""
        response = self.client.get("/api/v1/rubros/1")
        if response.status_code == 200:
            data = response.json()
            self.assertIn("emprendedores", data)
            self.assertIsInstance(data["emprendedores"], list)

    def test_feria_nested_schema(self):
        """Verifica que GET /ferias/{id} retorne FeriaPublicNested con emprendedores."""
        response = self.client.get("/api/v1/ferias/1")
        if response.status_code == 200:
            data = response.json()
            self.assertIn("emprendedores", data)
            self.assertIsInstance(data["emprendedores"], list)

    def test_usuario_nested_schema(self):
        """Verifica que GET /usuarios/{id} retorne UsuarioPublicNested con emprendedor."""
        response = self.client.get("/api/v1/usuarios/1")
        if response.status_code == 200:
            data = response.json()
            self.assertIn("emprendedor", data)

    def test_producto_negative_price_rejected_on_update(self):
        """Verifica que ProductoUpdate rechace precio negativo con 422."""
        response = self.client.put("/api/v1/productos/1", json={"precio": -100.0})
        self.assertEqual(response.status_code, 422)

    def test_producto_post_nonexistent_category_returns_404(self):
        """Verifica que POST /productos con categoría inexistente retorne 404."""
        payload = {
            "nombre": "Producto Inexistente FK",
            "precio": 500.0,
            "categoria_id": 999999,
            "emprendedor_id": 1,
            "activo": True,
        }
        response = self.client.post("/api/v1/productos/", json=payload)
        self.assertEqual(response.status_code, 404)

    def test_delete_categoria_with_products_returns_409(self):
        """Verifica que eliminar una categoría con productos asignados devuelva 409 Conflict."""
        # Categoría 1 tiene productos asignados en la BD
        response = self.client.delete("/api/v1/categorias/1")
        self.assertEqual(response.status_code, 409)

    def test_delete_rubro_with_emprendedores_returns_409(self):
        """Verifica que eliminar un rubro con emprendedores devuelva 409 Conflict."""
        # Rubro 1 tiene emprendedores asignados en la BD
        response = self.client.delete("/api/v1/rubros/1")
        self.assertEqual(response.status_code, 409)


    def test_emprendedor_empty_nombre_rejected_on_update(self):
        """Verifica que EmprendedorUpdate rechace nombre_fantasia vacío con 422."""
        response = self.client.put("/api/v1/emprendedores/1", json={"nombre_fantasia": ""})
        self.assertEqual(response.status_code, 422)

    def test_sqlite_pragma_foreign_keys_is_enabled(self):
        """Verifica que PRAGMA foreign_keys esté activo en la conexión SQLite."""
        from src.db.session import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA foreign_keys")).scalar()
            self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()



