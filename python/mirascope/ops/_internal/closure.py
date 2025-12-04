from __future__ import annotations

import ast
import gc
import hashlib
import importlib.metadata
import importlib.util
import inspect
import logging
import os
import site
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from functools import cached_property, lru_cache
from pathlib import Path
from textwrap import dedent
from types import ModuleType
from typing import Annotated, Any, TypedDict, TypeVar, cast, get_args, get_origin

import libcst as cst
import libcst.matchers as m
from libcst import MaybeSentinel
from packaging.markers import default_environment
from packaging.requirements import Requirement

from ..exceptions import ClosureComputationError

logger = logging.getLogger(__name__)

_BaseCompoundStatementT = TypeVar(
    "_BaseCompoundStatementT", bound=cst.BaseCompoundStatement
)


def _is_third_party(module: ModuleType, site_packages: set[str]) -> bool:
    """Returns True if the module is a third-party or standard library module."""
    module_file = getattr(module, "__file__", None)
    return (
        module.__name__ == "mirascope"
        or module.__name__.startswith("mirascope.")
        or module.__name__ in sys.stdlib_module_names
        or module_file is None
        or any(
            str(Path(module_file).resolve()).startswith(site_pkg)
            for site_pkg in site_packages
        )
    )


class _RemoveDocstringTransformer(cst.CSTTransformer):
    """CST transformer to remove docstrings from functions and classes."""

    def __init__(self, exclude_fn_body: bool) -> None:
        super().__init__()
        self.exclude_fn_body = exclude_fn_body

    @staticmethod
    def _remove_first_docstring(
        node: _BaseCompoundStatementT,
    ) -> _BaseCompoundStatementT:
        """Returns the node with the first docstring removed from its body."""
        body = node.body
        stmts = list(body.body)
        if stmts:
            first_stmt = stmts[0]
            if m.matches(
                first_stmt, m.SimpleStatementLine(body=[m.Expr(value=m.SimpleString())])
            ):
                stmts.pop(0)

        if not stmts:
            stmts = [
                cst.Expr(
                    value=cst.Ellipsis(
                        lpar=[],
                        rpar=[],
                    ),
                    semicolon=MaybeSentinel.DEFAULT,
                )
            ]
            if m.matches(node.body, m.IndentedBlock()):
                return node.with_changes(body=stmts[0])
        new_body = body.with_changes(body=stmts)
        return node.with_changes(body=new_body)

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        """Returns the function definition with docstring removed or body replaced with ellipsis."""
        if self.exclude_fn_body:
            stmts = cst.Expr(
                value=cst.Ellipsis(
                    lpar=[],
                    rpar=[],
                ),
                semicolon=MaybeSentinel.DEFAULT,
            )
            return updated_node.with_changes(body=stmts)

        return self._remove_first_docstring(updated_node)

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        """Returns the class definition with docstring removed or body replaced with pass."""
        if self.exclude_fn_body:
            pass_stmt = cst.SimpleStatementLine([cst.Pass()])
            new_body = updated_node.body.with_changes(body=[pass_stmt])
            return updated_node.with_changes(body=new_body)

        return self._remove_first_docstring(updated_node)


def _clean_source_code(
    fn: Callable[..., Any] | type,
    *,
    exclude_fn_body: bool = False,
) -> str:
    """Returns the source code of a function or class with docstrings optionally removed."""
    source = dedent(inspect.getsource(fn))
    docstr_flag = os.getenv("MIRASCOPE_VERSIONING_INCLUDE_DOCSTRINGS", "false").lower()
    if docstr_flag in ("1", "true", "yes"):
        return source.rstrip()
    module = cst.parse_module(source)

    transformer = _RemoveDocstringTransformer(exclude_fn_body=exclude_fn_body)
    new_module = module.visit(transformer)

    code = new_module.code
    code = code.rstrip()

    return code


@dataclass(frozen=True)
class _AttributePath:
    """Represents a parsed attribute access path like 'module.class.method'."""

    components: list[str]
    """Ordered list from base to final attribute (e.g., ['module', 'class', 'method'])."""

    @property
    def base_name(self) -> str:
        """Returns the base module or object name."""
        return self.components[0] if self.components else ""

    @property
    def last_attribute(self) -> str:
        """Returns the last attribute in the chain."""
        return self.components[-1] if self.components else ""

    @property
    def full_path(self) -> str:
        """Returns the complete dotted path."""
        return ".".join(self.components)

    @classmethod
    def from_ast_node(cls, node: ast.AST) -> _AttributePath | None:
        """Creates an `_AttributePath` from an AST node.

        Args:
            node: An AST node (typically ast.Name, ast.Attribute, or ast.Call).

        Returns:
            `_AttributePath` with parsed components, or None if parsing fails.
        """
        components = []
        current = node

        while True:
            if isinstance(current, ast.Attribute):
                components.append(current.attr)
                current = current.value
            elif isinstance(current, ast.Call):
                current = current.func
            elif isinstance(current, ast.Name):
                components.append(current.id)
                break
            else:
                break

        components.reverse()
        return cls(components=components)

    def __bool__(self) -> bool:
        """Returns True if components exist."""
        return bool(self.components)


class _NameCollector(ast.NodeVisitor):
    """AST visitor that collects all names used in a piece of code."""

    def __init__(self) -> None:
        self.used_names: list[str] = []

    def visit_Name(self, node: ast.Name) -> None:
        """Collects name nodes."""
        self.used_names.append(node.id)

    def visit_Call(self, node: ast.Call) -> None:
        """Collects function names from call nodes."""
        if isinstance(node.func, ast.Name):
            self.used_names.append(node.func.id)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Collects attribute access chains."""
        attr_path = _AttributePath.from_ast_node(node)
        if attr_path:
            self.used_names.append(attr_path.full_path)
            self.used_names.append(attr_path.base_name)


class _ImportCollector(ast.NodeVisitor):
    """AST visitor that collects import statements based on used names."""

    def __init__(self, used_names: list[str], site_packages: set[str]) -> None:
        self.imports: set[str] = set()
        self.user_defined_imports: set[str] = set()
        self.used_names = used_names
        self.site_packages = site_packages
        self.alias_map: dict[str, str] = {}

    def _is_used_import(self, import_name: str) -> bool:
        """Returns whether an import with the given name is used in the code."""
        return import_name in self.used_names or any(
            u.startswith(f"{import_name}.") for u in self.used_names
        )

    def _add_import(
        self, import_statement: str, is_third_party: bool, alias: str | None = None
    ) -> None:
        """Adds import statement to appropriate collection."""
        if alias:
            self.alias_map[alias] = import_statement

        if is_third_party:
            self.imports.add(import_statement)
        else:
            self.user_defined_imports.add(import_statement)

    def visit_Import(self, node: ast.Import) -> None:
        """Collects import statements."""
        for name in node.names:
            full_module_name = name.name
            base_module_name = name.name.split(".")[0]
            try:
                module = __import__(base_module_name)
            except ImportError:
                module = None
            import_name = name.asname or base_module_name

            if not self._is_used_import(import_name):
                continue

            is_third_party = (
                _is_third_party(module, self.site_packages) if module else False
            )

            if alias := name.asname:
                import_statement = f"import {full_module_name} as {alias}"
            else:
                import_statement = f"import {full_module_name}"

            self._add_import(import_statement, is_third_party, name.asname)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Collects from-import statements."""
        if not (module := node.module):
            return

        try:
            is_third_party = _is_third_party(
                __import__(module.split(".")[0]), self.site_packages
            )
        except ImportError:
            module = "." * node.level + module
            is_third_party = False

        for name in node.names:
            import_name = name.asname or name.name

            if not self._is_used_import(import_name):
                continue

            if alias := name.asname:
                import_statement = f"from {module} import {name.name} as {alias}"
            else:
                import_statement = f"from {module} import {name.name}"

            self._add_import(import_statement, is_third_party, name.asname)


class _LocalAssignmentCollector(ast.NodeVisitor):
    """AST visitor that collects local variable assignments."""

    def __init__(self) -> None:
        self.assignments: set[str] = set()

    def visit_Assign(self, node: ast.Assign) -> None:
        """Collects variable names from assignment statements."""
        if isinstance(node.targets[0], ast.Name):
            self.assignments.add(node.targets[0].id)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Collects variable names from annotated assignment statements."""
        if isinstance(node.target, ast.Name):
            self.assignments.add(node.target.id)
        self.generic_visit(node)


class _GlobalAssignmentCollector(ast.NodeVisitor):
    """AST visitor that collects global assignments used in function."""

    def __init__(self, used_names: list[str], source: str) -> None:
        self.used_names = used_names
        self.source = source
        self.assignments: list[str] = []
        self.current_function = None
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Tracks function scope while visiting."""
        old_function = self.current_function
        self.current_function = node
        self.generic_visit(node)
        self.current_function = old_function

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Tracks class scope while visiting."""
        old_class = self.current_class
        self.current_class = node
        self.generic_visit(node)
        self.current_class = old_class

    def visit_Assign(self, node: ast.Assign) -> None:
        """Collects global assignment statements."""
        if self.current_function is not None or self.current_class is not None:
            return
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in self.used_names:
                code = ast.get_source_segment(self.source, node)
                if code is not None:
                    self.assignments.append(code)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Collects global annotated assignment statements."""
        if self.current_function is not None or self.current_class is not None:
            return
        if isinstance(node.target, ast.Name) and node.target.id in self.used_names:
            code = ast.get_source_segment(self.source, node)
            if code is not None:
                self.assignments.append(code)


def _collect_parameter_names(tree: ast.Module) -> set[str]:
    """Returns set of all parameter names from functions in the AST."""
    params = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                params.add(arg.arg)
            for arg in node.args.kwonlyargs:
                params.add(arg.arg)
            if node.args.vararg:
                params.add(node.args.vararg.arg)
            if node.args.kwarg:
                params.add(node.args.kwarg.arg)
    return params


def _extract_types(annotation: Any) -> set[type]:  # noqa: ANN401
    """Returns set of types found in a type annotation."""
    types_found: set[type] = set()
    origin = get_origin(annotation)

    if origin is not None:
        if origin is Annotated:
            base_annotation, *_ = get_args(annotation)
            types_found |= _extract_types(base_annotation)
        else:
            for arg in get_args(annotation):
                types_found |= _extract_types(arg)
    elif isinstance(annotation, type) and not _is_stdlib_or_builtin(annotation):
        types_found.add(annotation)
    return types_found


def _is_stdlib_or_builtin(obj: Any) -> bool:  # noqa: ANN401
    """Returns True if object is from standard library or builtins."""
    if not hasattr(obj, "__module__"):
        return False

    module_name = obj.__module__
    if not module_name:
        return False

    return (
        module_name in sys.stdlib_module_names
        or module_name.startswith("collections.")
        or module_name.startswith("typing.")
        or module_name in {"abc", "typing", "builtins", "_collections_abc"}
    )


class _DefinitionCollector(ast.NodeVisitor):
    """AST visitor that collects function and class definitions referenced in code."""

    def __init__(
        self, module: ModuleType, used_names: list[str], site_packages: set[str]
    ) -> None:
        self.module = module
        self.used_names = used_names
        self.site_packages = site_packages
        self.definitions_to_include: list[Callable[..., Any] | type] = []
        self.definitions_to_analyze: list[Callable[..., Any] | type] = []
        self.imports: set[str] = set()

    def visit_Name(self, node: ast.Name) -> None:
        """Collects named references to callable definitions."""
        if node.id in self.used_names:
            candidate = getattr(self.module, node.id, None)
            if callable(candidate) and not _is_stdlib_or_builtin(candidate):
                self.definitions_to_include.append(candidate)
        self.generic_visit(node)

    def _process_decorator(self, decorator_node: ast.AST) -> None:
        """Processes a decorator node to extract its definition."""
        if isinstance(decorator_node, ast.Name):
            if decorator_func := getattr(self.module, decorator_node.id, None):
                self.definitions_to_include.append(decorator_func)
        elif isinstance(decorator_node, ast.Attribute):
            attr_path = _AttributePath.from_ast_node(decorator_node)
            if attr_path:
                base_module = getattr(self.module, attr_path.base_name, None)
                if (
                    attr_path.full_path in self.used_names
                    and base_module
                    and (
                        definition := getattr(
                            base_module, attr_path.last_attribute, None
                        )
                    )
                ):
                    self.definitions_to_include.append(definition)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Collects function definitions and their decorators."""
        for decorator_node in node.decorator_list:
            self._process_decorator(decorator_node)

        nested_func = getattr(self.module, node.name, None)
        if nested_func:
            self.definitions_to_analyze.append(nested_func)

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Collects class definitions and their type annotations."""
        if class_def := getattr(self.module, node.name, None):
            self.definitions_to_analyze.append(class_def)
            if hasattr(class_def, "__annotations__"):
                for ann in class_def.__annotations__.values():
                    for candidate in _extract_types(ann):
                        if (
                            isinstance(candidate, type)
                            and candidate.__module__ == class_def.__module__
                            and candidate.__module__ != "builtins"
                        ) and candidate not in self.definitions_to_include:
                            self.definitions_to_include.append(candidate)
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and (
                    definition := getattr(class_def, item.name, None)
                ):
                    self.definitions_to_analyze.append(definition)
        self.generic_visit(node)

    def _process_name_or_attribute(self, node: ast.AST) -> None:
        """Processes name or attribute nodes to find definitions."""
        if isinstance(node, ast.Name):
            if (
                (obj := getattr(self.module, node.id, None))
                and hasattr(obj, "__name__")
                and not _is_stdlib_or_builtin(obj)
            ):
                self.definitions_to_include.append(obj)
        elif isinstance(node, ast.Attribute):
            attr_path = _AttributePath.from_ast_node(node)
            if not attr_path or attr_path.full_path not in self.used_names:
                return

            base_module = getattr(self.module, attr_path.base_name, None)
            if (
                base_module
                and isinstance(base_module, ModuleType)
                and _is_third_party(base_module, self.site_packages)
            ):
                return

            obj = self.module
            for component in attr_path.components:
                obj = getattr(obj, component, None)
                if obj is None:
                    break

            if (
                obj
                and hasattr(obj, "__name__")
                and not _is_stdlib_or_builtin(obj)
                and not isinstance(obj, ModuleType)
            ):
                self.definitions_to_include.append(obj)

    def visit_Call(self, node: ast.Call) -> None:
        """Collects definitions referenced in function calls."""
        self._process_name_or_attribute(node.func)
        for arg in node.args:
            self._process_name_or_attribute(arg)
        for keyword in node.keywords:
            self._process_name_or_attribute(keyword.value)
        self.generic_visit(node)


class _QualifiedNameRewriter(cst.CSTTransformer):
    """CST transformer that rewrites qualified names to simple names for local definitions."""

    def __init__(self, local_names: set[str], user_defined_imports: set[str]) -> None:
        super().__init__()
        self.local_names: set[str] = local_names
        self.alias_mapping = {}
        for import_stmt in user_defined_imports:
            if not import_stmt.startswith("from "):
                continue
            parts = import_stmt.split(" ")
            if len(parts) >= 4 and "as" in parts:
                original_name = parts[parts.index("import") + 1]
                alias = parts[parts.index("as") + 1]
                self.alias_mapping[alias] = original_name

    def _gather_attribute_chain(self, node: cst.Attribute | cst.Name) -> list[str]:
        """Returns the chain of attribute names from an attribute node."""
        names = []
        current = node

        while isinstance(current, cst.Attribute):
            names.append(current.attr.value)
            current = current.value

        if isinstance(current, cst.Name):
            names.append(current.value)

        return list(reversed(names))

    def leave_Attribute(
        self, original_node: cst.Attribute, updated_node: cst.Attribute
    ) -> cst.Name | cst.Attribute:
        """Returns simplified name if attribute refers to local definition."""
        names = self._gather_attribute_chain(updated_node)
        if names and names[-1] in self.local_names:
            return cst.Name(value=names[-1])

        return updated_node

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:
        """Returns de-aliased name if it was imported with an alias."""
        if updated_node.value in self.alias_mapping:
            return cst.Name(
                value=self.alias_mapping[updated_node.value],
                lpar=updated_node.lpar,
                rpar=updated_node.rpar,
            )
        return updated_node


def _get_class_from_unbound_method(method: Callable[..., Any]) -> type | None:
    """Returns the class that contains the given unbound method."""
    qualname = method.__qualname__
    parts = qualname.split(".")
    class_qualname = ".".join(parts[:-1])

    for obj in gc.get_objects():
        try:
            object_is_type = isinstance(obj, type)
        except Exception:
            continue
        if object_is_type and getattr(obj, "__qualname__", None) == class_qualname:
            return obj
    return None


def _clean_source_from_string(source: str, exclude_fn_body: bool = False) -> str:
    """Returns cleaned source code string with optional docstring removal."""
    source = dedent(source)
    module = cst.parse_module(source)
    transformer = _RemoveDocstringTransformer(exclude_fn_body=exclude_fn_body)
    new_module = module.visit(transformer)
    return new_module.code.rstrip()


def _get_class_source_from_method(method: Callable[..., Any]) -> str:
    """Get the source code of the class containing the given method.

    Args:
        method: The method to get the containing class source from.

    Returns:
        The cleaned source code of the containing class.

    Raises:
        ValueError: If the class cannot be determined from the method.
    """
    cls = _get_class_from_unbound_method(method)
    if cls is None:
        raise ValueError("Cannot determine class from method via gc")
    source = inspect.getsource(cls)
    return _clean_source_from_string(source)


class _DependencyCollector:
    """Collects dependencies, imports, and source code for function closure."""

    def __init__(self) -> None:
        self.imports: set[str] = set()
        self.fn_internal_imports: set[str] = set()
        self.user_defined_imports: set[str] = set()
        self.assignments: list[str] = []
        self.source_code: list[str] = []
        self.visited_functions: set[str] = set()
        self.site_packages: set[str] = {
            str(Path(p).resolve()) for p in site.getsitepackages()
        }
        self._last_import_collector: _ImportCollector | None = None

    def _collect_assignments_and_imports(
        self,
        fn_tree: ast.Module,
        module_tree: ast.Module,
        used_names: list[str],
        module_source: str,
    ) -> None:
        """Collects global assignments and their required imports."""
        local_assignment_collector = _LocalAssignmentCollector()
        local_assignment_collector.visit(fn_tree)
        local_assignments = local_assignment_collector.assignments

        parameter_names = _collect_parameter_names(fn_tree)

        global_assignment_collector = _GlobalAssignmentCollector(
            used_names, module_source
        )
        global_assignment_collector.visit(module_tree)

        for global_assignment in global_assignment_collector.assignments:
            tree = ast.parse(global_assignment)
            stmt = cast(ast.Assign | ast.AnnAssign, tree.body[0])
            if isinstance(stmt, ast.Assign):
                var_name = cast(ast.Name, stmt.targets[0]).id
            else:
                var_name = cast(ast.Name, stmt.target).id

            if var_name in parameter_names:
                continue

            if var_name not in used_names or var_name in local_assignments:
                continue

            self.assignments.append(global_assignment)

            name_collector = _NameCollector()
            name_collector.visit(tree)
            import_collector = _ImportCollector(
                name_collector.used_names, self.site_packages
            )
            import_collector.visit(module_tree)
            self.imports.update(import_collector.imports)
            self.user_defined_imports.update(import_collector.user_defined_imports)

    @staticmethod
    def _extract_definition(
        definition: Callable[..., Any] | type | property,
    ) -> Callable[..., Any] | type | None:
        """Returns the actual definition from decorators and properties."""
        if isinstance(definition, property):
            return definition.fget

        if isinstance(definition, cached_property) or (
            hasattr(definition, "func")
            and getattr(definition, "__name__", None) is None
        ):
            # For Python 3.13+
            return definition.func  # pyright: ignore[reportFunctionMemberAccess] # pragma: no cover

        return definition

    def _get_source_code(self, definition: Callable[..., Any] | type) -> str | None:
        """Returns the source code for a definition."""
        if definition.__qualname__ in self.visited_functions:
            return None
        self.visited_functions.add(definition.__qualname__)

        if "." in definition.__qualname__ and inspect.getmodule(definition) is not None:
            try:
                return _get_class_source_from_method(definition)
            except ValueError:
                return _clean_source_code(definition)

        return _clean_source_code(definition)

    def _process_imports(
        self,
        module_tree: ast.Module,
        used_names: list[str],
        source: str,
    ) -> None:
        """Process and categorize imports."""
        import_collector = _ImportCollector(used_names, self.site_packages)
        import_collector.visit(module_tree)

        new_imports = {
            import_stmt
            for import_stmt in import_collector.imports
            if import_stmt not in source
        }

        self.imports.update(new_imports)
        self.fn_internal_imports.update(import_collector.imports - new_imports)
        self.user_defined_imports.update(import_collector.user_defined_imports)

    def _process_definitions(
        self, fn_tree: ast.Module, module: ModuleType, used_names: list[str]
    ) -> None:
        """Process nested definitions and dependencies."""
        definition_collector = _DefinitionCollector(
            module, used_names, self.site_packages
        )
        definition_collector.visit(fn_tree)

        for definition in definition_collector.definitions_to_include:
            self._collect_imports_and_source_code(definition, True)

        for definition in definition_collector.definitions_to_analyze:
            self._collect_imports_and_source_code(definition, False)

    def _collect_imports_and_source_code(
        self,
        definition: Callable[..., Any] | type | property,
        include_source: bool,
    ) -> None:
        """Collects imports and optionally source code for a definition."""
        try:
            if _is_stdlib_or_builtin(definition) or isinstance(definition, ModuleType):
                return

            # property(fget=None) is not reachable via current code paths but kept as guard
            if (
                isinstance(definition, property) and definition.fget is None
            ):  # pragma: no cover
                return

            extracted_definition = _DependencyCollector._extract_definition(definition)
            # Same guard as above; kept for defensive coding
            if extracted_definition is None:  # pragma: no cover
                return

            source = self._get_source_code(extracted_definition)
            if source is None:
                return

            module = inspect.getmodule(extracted_definition)
            if not module or _is_third_party(module, self.site_packages):
                return

            module_source = inspect.getsource(module)
            module_tree = ast.parse(module_source)
            fn_tree = ast.parse(source)

            name_collector = _NameCollector()
            name_collector.visit(fn_tree)
            used_names = list(dict.fromkeys(name_collector.used_names))

            self._process_imports(module_tree, used_names, source)

            if include_source:
                for import_stmt in self.user_defined_imports:
                    source = source.replace(import_stmt, "")
                self.source_code.insert(0, source)

            self._collect_assignments_and_imports(
                fn_tree, module_tree, used_names, module_source
            )

            self._process_definitions(fn_tree, module, used_names)

        except (OSError, TypeError) as e:
            logger.debug(f"Failed to collect imports for {definition}: {e}")

    @staticmethod
    def _collect_required_dependencies(imports: set[str]) -> dict[str, dict[str, Any]]:
        """Returns package dependencies required by the import statements."""
        stdlib_modules = set(sys.stdlib_module_names)
        installed_packages = {
            dist.name: dist for dist in importlib.metadata.distributions()
        }
        import_to_dist = importlib.metadata.packages_distributions()

        dependencies = {}
        imported_dists = {}
        imported_roots = set()

        for import_stmt in imports:
            parts = import_stmt.strip().split()
            root_module = parts[1].split(".")[0]
            if root_module in stdlib_modules:
                continue

            imported_roots.add(root_module)

            dist_names = import_to_dist.get(root_module, [root_module])
            for dist_name in dist_names:
                if dist_name not in installed_packages:
                    continue

                dist = installed_packages[dist_name]
                imported_dists.setdefault(dist_name, dist)
                if dist_name not in dependencies:
                    dependencies[dist_name] = {
                        "version": dist.version,
                        "extras": None,
                    }
                break

        if not imported_dists:
            return {}

        dist_to_modules = {}
        for module_name, dist_names in import_to_dist.items():
            for dist_name in dist_names:
                dist_to_modules.setdefault(dist_name, set()).add(module_name)

        base_env = cast(dict[str, str], default_environment().copy())
        base_env["extra"] = ""
        extra_env_cache = {}

        def _env_for_extra(extra: str) -> dict[str, str]:
            if extra not in extra_env_cache:
                env = cast(dict[str, str], default_environment().copy())
                env["extra"] = extra
                extra_env_cache[extra] = env
            return extra_env_cache[extra]

        base_requirements = {}
        extra_requirements = {}

        for dist_name, dist in imported_dists.items():
            base_reqs = set()
            extras_map = {
                extra: set() for extra in dist.metadata.get_all("Provides-Extra", [])
            }
            requirements = dist.requires or []
            for requirement_str in requirements:
                req = Requirement(requirement_str)
                marker = req.marker
                if marker is None or marker.evaluate(base_env):
                    base_reqs.add(req.name)
                    continue

                for extra in extras_map:
                    if marker.evaluate(_env_for_extra(extra)):
                        extras_map[extra].add(req.name)

            base_requirements[dist_name] = base_reqs
            extra_requirements[dist_name] = extras_map

        provided_requirements = set()
        for reqs in base_requirements.values():
            provided_requirements.update(reqs)
        provided_requirements.update(imported_dists.keys())

        for dist_name in sorted(imported_dists):
            extras_to_keep = []
            apply_usage_gate = not dist_name.startswith("mirascope")
            for extra, deps in extra_requirements[dist_name].items():
                if not deps:
                    continue

                if apply_usage_gate and not any(
                    dist_to_modules.get(dep, set()) & imported_roots for dep in deps
                ):
                    continue

                missing = [dep for dep in deps if dep not in provided_requirements]
                if missing:
                    extras_to_keep.append(extra)
                    provided_requirements.update(deps)

            dependencies[dist_name]["extras"] = extras_to_keep or None

        return dependencies

    @classmethod
    def _map_child_to_parent(
        cls,
        child_to_parent: dict[ast.AST, ast.AST | None],
        node: ast.AST,
        parent: ast.AST | None = None,
    ) -> None:
        """Maps each AST node to its parent node."""
        child_to_parent[node] = parent
        for _, value in ast.iter_fields(node):
            if isinstance(value, list):
                for child in value:
                    if isinstance(child, ast.AST):
                        cls._map_child_to_parent(child_to_parent, child, node)
            elif isinstance(value, ast.AST):
                cls._map_child_to_parent(child_to_parent, value, node)

    def _extract_local_names(self, code_blocks: list[str]) -> set[str]:
        """Extracts names of locally defined functions and classes."""
        local_names = set()

        for code in code_blocks:
            tree = ast.parse(code)
            child_to_parent = {}
            self._map_child_to_parent(child_to_parent, tree)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef | ast.ClassDef):
                    parent = child_to_parent.get(node)
                    if isinstance(parent, ast.Module):
                        local_names.add(node.name)

        return local_names

    @staticmethod
    def _rewrite_code_blocks(
        code_blocks: list[str], rewriter: _QualifiedNameRewriter
    ) -> list[str]:
        """Rewrites code blocks with simplified names."""
        rewritten = []
        for code in code_blocks:
            tree = cst.parse_module(code)
            new_tree = tree.visit(rewriter)
            rewritten.append(new_tree.code)
        return rewritten

    def collect(
        self, fn: Callable[..., Any]
    ) -> tuple[list[str], list[str], list[str], dict[str, dict[str, Any]]]:
        """Collects all components needed for function closure.

        Args:
            fn: The function to collect closure information for.

        Returns:
            A tuple containing:
                - List of import statements
                - List of assignment statements
                - List of source code blocks
                - Dictionary of required dependencies
        """
        self._collect_imports_and_source_code(fn, True)

        local_names = self._extract_local_names(self.source_code + self.assignments)
        rewriter = _QualifiedNameRewriter(local_names, self.user_defined_imports)

        assignments = self._rewrite_code_blocks(self.assignments, rewriter)
        source_code = self._rewrite_code_blocks(self.source_code, rewriter)

        required_dependencies = _DependencyCollector._collect_required_dependencies(
            self.imports | self.fn_internal_imports
        )

        return (
            list(self.imports),
            list(dict.fromkeys(assignments)),
            source_code,
            required_dependencies,
        )


def _run_ruff(code: str) -> str:
    """Returns formatted code using ruff formatter."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp_file:
        tmp_file.write(code)
        tmp_path = Path(tmp_file.name)

    try:
        proc = subprocess.run(
            ["ruff", "check", "--isolated", "--select=I001", "--fix", str(tmp_path)],
            capture_output=True,
            text=True,
        )

        if proc.returncode not in (0, 1):
            raise subprocess.CalledProcessError(
                proc.returncode, proc.args, output=proc.stdout, stderr=proc.stderr
            )

        subprocess.run(
            ["ruff", "format", "--isolated", "--line-length=88", str(tmp_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        processed_code = tmp_path.read_text()
        return processed_code
    finally:
        tmp_path.unlink()


def get_qualified_name(fn: Callable[..., Any]) -> str:
    """Return the simplified qualified name of a function.

    If the function is defined locally, return the name after '<locals>.';
    otherwise, return the last non-empty part after splitting by '.'.

    Args:
        fn: The function to get the qualified name from.

    Returns:
        The simplified qualified name of the function.
    """
    qualified_name = fn.__qualname__
    if "<locals>." in qualified_name:
        return qualified_name.split("<locals>.")[-1]
    else:
        parts = [part for part in qualified_name.split(".") if part]
        return parts[-1] if parts else qualified_name


class DependencyInfo(TypedDict):
    """Represents the dependency information for a closure."""

    version: str
    """The version of the dependency."""

    extras: list[str] | None
    """The extras required for the dependency."""


@dataclass(frozen=True, kw_only=True)
class Closure:
    """Represents the closure of a function."""

    name: str
    """The name of the function."""

    signature: str
    """The signature of the function."""

    docstring: str | None
    """The docstring of the function."""

    code: str
    """The code of the function."""

    hash: str
    """The hash of the closure."""

    signature_hash: str
    """The hash of the function signature (determines major version X)."""

    dependencies: dict[str, DependencyInfo]
    """The dependencies of the closure."""

    @classmethod
    @lru_cache(maxsize=128)
    def from_fn(cls, fn: Callable[..., Any]) -> Closure:
        """Create a closure from a function.

        Args:
            fn: The function to analyze

        Returns:
            Closure: The closure of the function.

        Raises:
            ClosureComputationError: if the closure cannot be computed properly.
        """
        collector = _DependencyCollector()
        imports, assignments, source_code, dependencies = collector.collect(fn)
        code = "{imports}\n\n{assignments}\n\n{source_code}".format(
            imports="\n".join(imports),
            assignments="\n".join(assignments),
            source_code="\n\n".join(source_code),
        )
        qualified_name = get_qualified_name(fn)
        try:
            formatted_code = _run_ruff(code)
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            raise ClosureComputationError(qualified_name=qualified_name)
        hash_value = hashlib.sha256(formatted_code.encode("utf-8")).hexdigest()

        signature = _run_ruff(_clean_source_code(fn, exclude_fn_body=True)).strip()
        signature_hash = hashlib.sha256(signature.encode("utf-8")).hexdigest()

        return cls(
            name=qualified_name,
            docstring=inspect.getdoc(fn),
            signature=signature,
            code=formatted_code,
            hash=hash_value,
            signature_hash=signature_hash,
            dependencies={
                name: DependencyInfo(
                    version=dep_info["version"],
                    extras=dep_info.get("extras"),
                )
                for name, dep_info in dependencies.items()
            },
        )


__all__ = ["Closure", "DependencyInfo"]
