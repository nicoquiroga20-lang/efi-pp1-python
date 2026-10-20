import unittest
from src.main import app


class TestOpenAPI404Docs(unittest.TestCase):
    """
    Verifica que todos los endpoints que buscan coincidencias por ID tengan
    documentado el error 404 en el esquema OpenAPI (/docs), tal como lo exige el PDF.
    """

    def setUp(self):
        self.schema = app.openapi()
        self.paths = self.schema["paths"]

    def test_all_id_endpoints_document_404(self):
        id_routes = [
            "/api/v1/categorias/{categoria_id}",
            "/api/v1/productos/{producto_id}",
            "/api/v1/emprendedores/{emprendedor_id}",
            "/api/v1/planes/{plan_id}",
            "/api/v1/rubros/{rubro_id}",
            "/api/v1/ferias/{feria_id}",
            "/api/v1/contactos/{contacto_id}",
            "/api/v1/usuarios/{usuario_id}",
        ]

        for path in id_routes:
            self.assertIn(path, self.paths, f"Ruta {path} no encontrada en OpenAPI")
            methods = self.paths[path]
            for method_name, method_obj in methods.items():
                if method_name in ["get", "put", "delete"]:
                    responses = method_obj.get("responses", {})
                    self.assertIn(
                        "404",
                        responses,
                        f"Error 404 no documentado en {method_name.upper()} {path}",
                    )
                    self.assertTrue(
                        len(responses["404"].get("description", "")) > 0,
                        f"Descripción de 404 vacía en {method_name.upper()} {path}",
                    )


if __name__ == "__main__":
    unittest.main()
