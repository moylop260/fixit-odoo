import libcst as cst
from fixit import LintRule, InvalidTestCase, ValidTestCase


class NoInstallableTrueRule(LintRule):
    """Replace _('text') calls with self.env._('text') inside Odoo model methods."""

    MESSAGE = "Use self.env._(...) instead of _(…) directly inside Odoo model methods."

    VALID = [
        ValidTestCase(
            code="""
from odoo import models, _


class TestModel(models.Model):
    def my_method(self):
        self.env._("new translated")
"""
        )
    ]

    INVALID = [
        InvalidTestCase(
            code="""
from odoo import models, _


class TestModel(models.Model):
    def my_method(self):
        _("old translated")
        self.env._("new translated")

""",
            expected_replacement="""
from odoo import models, _


class TestModel(models.Model):
    def my_method(self):
        self.env._("old translated")
        self.env._("new translated")

""",
        )
    ]

    def visit_Call(self, node: cst.Call) -> None:
        """
        Visit every function call node.
        If the call is _('...'), report it for replacement.
        """
        if isinstance(node.func, cst.Name) and node.func.value == "_":
            # Register the violation and attach a fix
            self.report(node, replacement=self.fix(node))

    def fix(self, node: cst.Call) -> cst.Call:
        """
        Return the fixed version of _('text') → self.env._('text').
        """
        return node.with_changes(
            func=cst.Attribute(
                value=cst.Attribute(
                    value=cst.Name("self"),
                    attr=cst.Name("env"),
                ),
                attr=cst.Name("_"),
            )
        )
