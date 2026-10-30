import unittest
from typing import get_origin, Annotated
import src.models as models


class TestModelsStructure(unittest.TestCase):
    """
    Verifica los requisitos pedagógicos de la cátedra para modelos y schemas:
    1. Existencia de al menos 3 clases por modelo (Base, Table, Public, y Nested donde aplique).
    2. Uso de Annotated en las definiciones de campos.
    3. Definición de Relationships de SQLModel.
    """

    def test_categoria_classes(self):
        self.assertTrue(hasattr(models, "CategoriaBase"))
        self.assertTrue(hasattr(models, "Categoria"))
        self.assertTrue(hasattr(models, "CategoriaPublic"))
        self.assertTrue(hasattr(models, "CategoriaPublicNested"))
        self.assertTrue(hasattr(models, "CategoriaCreate"))
        self.assertTrue(hasattr(models, "CategoriaUpdate"))
        # Verifica relación con productos
        self.assertTrue(hasattr(models.Categoria, "productos"))

    def test_rubro_classes(self):
        self.assertTrue(hasattr(models, "RubroBase"))
        self.assertTrue(hasattr(models, "Rubro"))
        self.assertTrue(hasattr(models, "RubroPublic"))
        self.assertTrue(hasattr(models, "RubroPublicNested"))
        self.assertTrue(hasattr(models, "RubroCreate"))
        self.assertTrue(hasattr(models, "RubroUpdate"))
        self.assertTrue(hasattr(models.Rubro, "emprendedores"))

    def test_feria_classes(self):
        self.assertTrue(hasattr(models, "FeriaBase"))
        self.assertTrue(hasattr(models, "Feria"))
        self.assertTrue(hasattr(models, "FeriaPublic"))
        self.assertTrue(hasattr(models, "FeriaPublicNested"))
        self.assertTrue(hasattr(models, "FeriaCreate"))
        self.assertTrue(hasattr(models, "FeriaUpdate"))
        self.assertTrue(hasattr(models.Feria, "emprendedores"))

    def test_contacto_classes(self):
        self.assertTrue(hasattr(models, "ContactoBase"))
        self.assertTrue(hasattr(models, "Contacto"))
        self.assertTrue(hasattr(models, "ContactoPublic"))
        self.assertTrue(hasattr(models, "ContactoCreate"))
        self.assertTrue(hasattr(models, "ContactoUpdate"))

    def test_usuario_classes(self):
        self.assertTrue(hasattr(models, "UsuarioBase"))
        self.assertTrue(hasattr(models, "Usuario"))
        self.assertTrue(hasattr(models, "UsuarioPublic"))
        self.assertTrue(hasattr(models, "UsuarioPublicNested"))
        self.assertTrue(hasattr(models, "UsuarioCreate"))
        self.assertTrue(hasattr(models, "UsuarioUpdate"))
        self.assertTrue(hasattr(models.Usuario, "emprendedor"))

    def test_emprendedor_classes_and_nested(self):
        self.assertTrue(hasattr(models, "EmprendedorBase"))
        self.assertTrue(hasattr(models, "Emprendedor"))
        self.assertTrue(hasattr(models, "EmprendedorPublic"))
        self.assertTrue(hasattr(models, "EmprendedorPublicNested"))
        self.assertTrue(hasattr(models, "EmprendedorCreate"))
        self.assertTrue(hasattr(models, "EmprendedorUpdate"))
        # Verifica relationships
        self.assertTrue(hasattr(models.Emprendedor, "usuario"))
        self.assertTrue(hasattr(models.Emprendedor, "rubro"))
        self.assertTrue(hasattr(models.Emprendedor, "feria"))
        self.assertTrue(hasattr(models.Emprendedor, "productos"))

    def test_producto_classes_and_nested(self):
        self.assertTrue(hasattr(models, "ProductoBase"))
        self.assertTrue(hasattr(models, "Producto"))
        self.assertTrue(hasattr(models, "ProductoPublic"))
        self.assertTrue(hasattr(models, "ProductoPublicNested"))
        self.assertTrue(hasattr(models, "ProductoCreate"))
        self.assertTrue(hasattr(models, "ProductoUpdate"))
        # Verifica relationships
        self.assertTrue(hasattr(models.Producto, "emprendedor"))
        self.assertTrue(hasattr(models.Producto, "categoria"))

    def test_annotated_types_used(self):
        # Verifica que los campos en ProductoBase y CategoriaBase usen Annotated
        categoria_hints = models.CategoriaBase.__annotations__
        self.assertEqual(get_origin(categoria_hints["nombre"]), Annotated)

        producto_hints = models.ProductoBase.__annotations__
        self.assertEqual(get_origin(producto_hints["nombre"]), Annotated)
        self.assertEqual(get_origin(producto_hints["precio"]), Annotated)


if __name__ == "__main__":
    unittest.main()
