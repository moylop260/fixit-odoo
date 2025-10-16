import libcst as cst
import libcst.matchers as m
from fixit import InvalidTestCase, LintRule, ValidTestCase


class NoInstallableTrueRule(LintRule):
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
        ),
    ]

    VALID = [
        ValidTestCase(
            code="""
from odoo import models, _


class TestModel(models.Model):
    def my_method(self):
        self.env._("new translated")
"""
        )]

    def leave_SimpleStatementLine(
        self,
        original_node: cst.SimpleStatementLine,
        # 👇 The missing argument that caused the error is here
        updated_node: cst.SimpleStatementLine, 
    ) -> cst.SimpleStatementLine:
        """
        Busca expresiones que consisten en una llamada a la función global '_'.
        """
        
        # Matcher para identificar una expresión (cst.Expr) que contenga 
        # una llamada (cst.Call) donde la función sea un Name con valor '_'.
        global_underscore_call_matcher = m.SimpleStatementLine(
            body=[
                m.Expr(
                    value=m.Call(
                        func=m.Name("_"),
                        args=m.ZeroOrMore(),
                    )
                )
            ]
        )

        if m.matches(updated_node, global_underscore_call_matcher):
            # Encontramos la llamada a '_()'
            
            expression = updated_node.body[0]
            call_node = cst.ensure_type(expression.value, cst.Call)

            # Construir el nuevo nodo de función: self.env._
            new_func_node = cst.Attribute(
                value=cst.Attribute(
                    value=cst.Name("self"),
                    attr=cst.Name("env"),
                    dot=cst.Dot(
                        whitespace_before=cst.SimpleWhitespace(""),
                        whitespace_after=cst.SimpleWhitespace("")
                    )
                ),
                attr=cst.Name("_"),
                dot=cst.Dot(
                    whitespace_before=cst.SimpleWhitespace(""),
                    whitespace_after=cst.SimpleWhitespace("")
                )
            )

            # Crear el nuevo nodo de llamada (cst.Call) con la función modificada.
            new_call_node = call_node.with_changes(
                func=new_func_node,
                whitespace_after_func=call_node.whitespace_after_func,
                whitespace_before_args=call_node.whitespace_before_args,
                lpar=call_node.lpar,
                rpar=call_node.rpar,
            )

            # Crear la nueva expresión (cst.Expr)
            new_expression = expression.with_changes(value=new_call_node)

            # Devolver el nodo SimpleStatementLine con la expresión corregida
            return updated_node.with_changes(body=(new_expression,))

        return updated_node