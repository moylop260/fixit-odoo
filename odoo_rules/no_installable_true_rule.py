import libcst as cst
import libcst.matchers as m
from fixit import LintRule, InvalidTestCase, ValidTestCase


class NoInstallableTrueRule(LintRule):
    """
    Identifies and removes 'installable': True from Odoo manifest files (__manifest__.py).
    'installable': True is the default and should be omitted for simplicity.
    """
    
    # 📚 Casos de Prueba (Opcional pero muy recomendado)
    # Define código que DEBE fallar (INVALID) y cómo DEBE quedar (expected_replacement)
    INVALID = [
        InvalidTestCase(
            code="""
{
    'name': 'Mi Módulo',
    'installable': True,
    'depends': ['base'],
}
""",
            # El reemplazo solo incluye el nodo inmediatamente anterior (la coma)
            expected_replacement='''
{
    'name': 'Mi Módulo',
    'depends': ['base'],
}
'''
        ),
        InvalidTestCase(
            code="""
{
    'installable': True,
    'name': 'Otro Módulo',
}
""",
            # Si es el primer elemento, se debe eliminar la clave-valor y el whitespace
            expected_replacement='''
{
    'name': 'Otro Módulo',
}
'''
        ),
        InvalidTestCase(
            code="""
{
    "installable": (
        True),
    "name": "hola",
}
""",
            expected_replacement="""
{
    "name": "hola",
}
"""
        ),
    ]
    
    # Define código que DEBE ser válido (VALID)
    VALID = [
        ValidTestCase(
            code="""
{
    'name': 'Mi Módulo',
    'depends': ['base'],
    'installable': False,
}
"""
        ),
        ValidTestCase(
            code="""
{
    'name': 'Mi Módulo',
    'depends': ['base'],
}
"""
        )
    ]

    def visit_DictElement(self, node: cst.DictElement) -> None:
        if (
            isinstance(node.key, cst.SimpleString)
            and node.key.value in ("'installable'", '"installable"')
        ):
            if (
                isinstance(node.value, cst.Name)
                and node.value.value == "True"
            ):
                # 3. Reportar el error con un autofix
                # import pdb;pdb.set_trace()
                # m.matches(node.value.value, m.Name("True"))
                # La clave para el autofix es usar cst.RemoveFromParent()
                # para indicarle a LibCST que elimine el nodo DictElement completo.
                self.report(
                    node,
                    "Eliminar 'installable': True, ya que es el valor por defecto.",
                    replacement=cst.RemoveFromParent(),
                )
