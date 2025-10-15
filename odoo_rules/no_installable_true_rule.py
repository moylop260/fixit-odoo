import libcst as cst
import libcst.matchers as m
from fixit import LintRule, InvalidTestCase, ValidTestCase


class NoInstallableTrueRule(LintRule):
    """Identifies and removes 'installable': True from Odoo manifest files (__manifest__.py).
    'installable': True is the default and should be omitted for simplicity.
    """
    INVALID = [
        InvalidTestCase(
            code="""
{
    'installable': True,
    'depends': [],
    'author': '',
    'name': 'Mi Módulo',
}
""",
            expected_replacement='''
{
    'name': 'Mi Módulo',
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
    "active": True,
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
    'active': False,
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
        if not isinstance(node.key, cst.SimpleString):
            return
        if (isinstance(node.value, cst.List) and not node.value.elements) or (
            isinstance(node.value, cst.SimpleString) and not node.value.evaluated_value):
            self.report(
                node,
                "Delete empty values.",
                replacement=cst.RemoveFromParent(),
            )
        if node.key.evaluated_value in ("active", "installable"):
            if isinstance(node.value, cst.Name) and node.value.value == "True":
                self.report(
                    node,
                    "Delete default values",
                    replacement=cst.RemoveFromParent(),
                )
