"""The `Closure` class."""

from __future__ import annotations

import ast
import hashlib
import importlib.metadata
import importlib.util
import inspect
import site
import subprocess
import sys
import tempfile
from collections.abc import Callable
from functools import cached_property, lru_cache
from pathlib import Path
from textwrap import dedent
from types import ModuleType
from typing import Any, TypeVar, cast

import libcst as cst
import libcst.matchers as m
from libcst import MaybeSentinel
from packaging.requirements import Requirement
from pydantic import BaseModel
from typing_extensions import TypedDict

_BaseCompoundStatementT = TypeVar(
    "_BaseCompoundStatementT", bound=cst.BaseCompoundStatement
)


class DependencyInfo(TypedDict):
    version: str
    extras: list[str] | None


def get_qualified_name(fn: Callable) -> str:
    """Return the simplified qualified name of a function.

    If the function is defined locally, return the name after '<locals>.'; otherwise,
    return the last non-empty part after splitting by '.'.
    """
    qualified_name = fn.__qualname__
    if "<locals>." in qualified_name:
        # For local functions, return the part after "<locals>."
        return qualified_name.split("<locals>.")[-1]
    else:
        parts = [part for part in qualified_name.split(".") if part]
        return parts[-1] if parts else qualified_name


def _is_third_party(module: ModuleType, site_packages: set[str]) -> bool:
    module_file = getattr(module, "__file__", None)
    return (
        module.__name__ == "lilypad"  # always consider lilypad as third-party
        or module.__name__ in sys.stdlib_module_names
        or module_file is None
        or any(
            str(Path(module_file).resolve()).startswith(site_pkg)
            for site_pkg in site_packages
        )
    )


class _RemoveDocstringTransformer(cst.CSTTransformer):
    """A LibCST transformer for removing docstrings from functions and classes.

    This transformer unconditionally removes the first statement (docstring) in each
    FunctionDef/ClassDef if it is a single string literal. If removing the docstring
    leaves the body empty, we insert a single 'pass' statement.

    If exclude_fn_body=True, we replace the entire body with a single 'pass' statement.
    """

    def __init__(self, exclude_fn_body: bool) -> None:
        super().__init__()
        self.exclude_fn_body = exclude_fn_body

    @staticmethod
    def _remove_first_docstring(
        node: _BaseCompoundStatementT,
    ) -> _BaseCompoundStatementT:
        """Return the body without a docstring, inserting 'pass' if no docstring."""
        body = node.body
        stmts = list(body.body)
        if stmts:
            first_stmt = stmts[0]
            # Check if the first statement is a single string-literal line
            if m.matches(
                first_stmt, m.SimpleStatementLine(body=[m.Expr(value=m.SimpleString())])
            ):
                # Remove the docstring
                stmts.pop(0)

        # If removing docstring leaves no statements, insert a single 'pass'
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
        if self.exclude_fn_body:
            # Replace entire body with a single 'pass'
            pass_stmt = cst.SimpleStatementLine([cst.Pass()])
            new_body = updated_node.body.with_changes(body=[pass_stmt])
            return updated_node.with_changes(body=new_body)

        return self._remove_first_docstring(updated_node)


def _clean_source_code(
    fn: Callable[..., Any] | type,
    *,
    exclude_fn_body: bool = False,
) -> str:
    """Returns a function's source code cleaned of elements that have no impact on behavior.
    Uses LibCST to:
      1. Remove the first docstring from any function/class in the code.
      2. Insert 'pass' if removal leaves the body empty.
      3. Optionally replace the body with 'pass' if exclude_fn_body is True.
      4. Convert multi-line strings to triple-quoted strings.
    """
    source = dedent(inspect.getsource(fn))
    module = cst.parse_module(source)

    transformer = _RemoveDocstringTransformer(exclude_fn_body=exclude_fn_body)
    new_module = module.visit(transformer)

    code = new_module.code
    # Trim trailing whitespace
    code = code.rstrip()

    return code


class _NameCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.used_names: list[str] = []

    def visit_Name(self, node: ast.Name) -> None:
        self.used_names.append(node.id)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            self.used_names.append(node.func.id)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        names = []
        current = node
        while True:
            if isinstance(current, ast.Attribute):
                names.append(current.attr)
                current = current.value
            elif isinstance(current, ast.Call):
                current = current.func
            else:
                break
        if isinstance(current, ast.Name):
            names.append(current.id)
            full_path = ".".join(reversed(names))
            self.used_names.append(full_path)
            self.used_names.append(names[-1])


class _ImportCollector(ast.NodeVisitor):
    def __init__(self, used_names: list[str], site_packages: set[str]) -> None:
        self.imports: set[str] = set()
        self.user_defined_imports: set[str] = set()
        self.used_names = used_names
        self.site_packages = site_packages
        self.alias_map: dict[str, str] = {}

    def visit_Import(self, node: ast.Import) -> None:
        for name in node.names:
            module_name = name.name.split(".")[0]
            module = __import__(module_name)
            import_name = name.asname or module_name
            is_used = import_name in self.used_names or any(
                u.startswith(f"{import_name}.") for u in self.used_names
            )
            if is_used:
                import_stmt = (
                    f"import {name.name} as {name.asname}"
                    if name.asname
                    else f"import {name.name}"
                )
                if name.asname:
                    self.alias_map[name.asname] = import_stmt

                if _is_third_party(module, self.site_packages):
                    self.imports.add(import_stmt)
                else:
                    self.user_defined_imports.add(import_stmt)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
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
            is_used = import_name in self.used_names or any(
                u.startswith(f"{import_name}.") for u in self.used_names
            )
            if is_used:
                if name.asname:
                    import_stmt = f"from {module} import {name.name} as {name.asname}"
                    self.alias_map[name.asname] = import_stmt
                else:
                    import_stmt = f"from {module} import {name.name}"

                if is_third_party:
                    self.imports.add(import_stmt)
                else:
                    self.user_defined_imports.add(import_stmt)


class _LocalAssignmentCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.assignments: set[str] = set()

    def visit_Assign(self, node: ast.Assign) -> None:
        if isinstance(node.targets[0], ast.Name):
            self.assignments.add(node.targets[0].id)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.target, ast.Name):
            self.assignments.add(node.target.id)
        self.generic_visit(node)


class _GlobalAssignmentCollector(ast.NodeVisitor):
    def __init__(self, used_names: list[str], source: str) -> None:
        self.used_names = used_names
        self.source = (
            source  # Original module source code for preserving literal formatting
        )
        self.assignments: list[str] = []
        self.current_function = None
        self.current_class = None  # Track class context

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        old_function = self.current_function
        self.current_function = node
        self.generic_visit(node)
        self.current_function = old_function

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_class = self.current_class
        self.current_class = node  # Entering a class context
        self.generic_visit(node)
        self.current_class = old_class  # Exiting the class context

    def visit_Assign(self, node: ast.Assign) -> None:
        # Skip assignments inside functions or classes
        if self.current_function is not None or self.current_class is not None:
            return
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in self.used_names:
                code = ast.get_source_segment(self.source, node)
                if code is not None:
                    self.assignments.append(code)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        # Skip annotated assignments inside functions or classes
        if self.current_function is not None or self.current_class is not None:
            return
        if isinstance(node.target, ast.Name) and node.target.id in self.used_names:
            code = ast.get_source_segment(self.source, node)
            if code is not None:
                self.assignments.append(code)


def _collect_parameter_names(tree: ast.Module) -> set[str]:
    """Collect all parameter names from function definitions in the AST."""
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
    """Recursively extract all type objects from a type annotation."""
    types_found: set[type] = set()
    origin = getattr(annotation, "__origin__", None)
    if origin is not None:
        if origin.__name__ == "Annotated":
            # For Annotated, take the first argument as the actual type.
            types_found |= _extract_types(annotation.__args__[0])
        else:
            for arg in annotation.__args__:
                types_found |= _extract_types(arg)
    elif isinstance(annotation, type):
        types_found.add(annotation)
    return types_found


class _DefinitionCollector(ast.NodeVisitor):
    def __init__(
        self, module: ModuleType, used_names: list[str], site_packages: set[str]
    ) -> None:
        self.module = module
        self.used_names = used_names
        self.site_packages = site_packages
        self.definitions_to_include: list[Callable[..., Any] | type] = []
        self.definitions_to_analyze: list[Callable[..., Any] | type] = []
        self.imports: set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for decorator_node in node.decorator_list:
            if isinstance(decorator_node, ast.Name):
                if decorator_func := getattr(self.module, decorator_node.id, None):
                    self.definitions_to_include.append(decorator_func)
            elif isinstance(decorator_node, ast.Attribute):
                names = []
                current = decorator_node
                while isinstance(current, ast.Attribute):
                    names.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    names.append(current.id)
                    full_path = ".".join(reversed(names))
                    if (
                        full_path in self.used_names
                        and (decorator_module := getattr(self.module, names[-1], None))
                        and (definition := getattr(decorator_module, names[0], None))
                    ):
                        self.definitions_to_include.append(definition)
        if nested_func := getattr(self.module, node.name, None):
            self.definitions_to_analyze.append(nested_func)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if class_def := getattr(self.module, node.name, None):
            self.definitions_to_analyze.append(class_def)
            # Extract types from the class's __annotations__.
            if hasattr(class_def, "__annotations__"):
                for ann in class_def.__annotations__.values():
                    for candidate in _extract_types(ann):
                        if (
                            isinstance(candidate, type)
                            and candidate.__module__ == class_def.__module__
                            and candidate.__module__ != "builtins"
                        ) and candidate not in self.definitions_to_include:
                            self.definitions_to_include.append(candidate)
            # Process methods within the class.
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and (
                    definition := getattr(class_def, item.name, None)
                ):
                    self.definitions_to_analyze.append(definition)
        self.generic_visit(node)

    def _process_name_or_attribute(self, node: ast.AST) -> None:
        if isinstance(node, ast.Name):
            if (obj := getattr(self.module, node.id, None)) and hasattr(
                obj, "__name__"
            ):
                self.definitions_to_include.append(obj)
        elif isinstance(node, ast.Attribute):
            names = []
            current = node
            while isinstance(current, ast.Attribute):
                names.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                names.append(current.id)
                full_path = ".".join(reversed(names))
                if (
                    full_path in self.used_names
                    and (definition := getattr(self.module, names[0], None))
                    and hasattr(definition, "__name__")
                ):
                    self.definitions_to_include.append(definition)

    def visit_Call(self, node: ast.Call) -> None:
        self._process_name_or_attribute(node.func)
        for arg in node.args:
            self._process_name_or_attribute(arg)
        for keyword in node.keywords:
            self._process_name_or_attribute(keyword.value)
        self.generic_visit(node)


class _QualifiedNameRewriter(cst.CSTTransformer):
    """A transformer that rewrites qualified names and resolves import aliases."""

    def __init__(self, local_names: set[str], user_defined_imports: set[str]) -> None:
        """Initialize alias mapping from import statements."""
        super().__init__()
        self.local_names: set[str] = local_names
        self.alias_mapping = {}
        for import_stmt in user_defined_imports:
            if import_stmt.startswith("from "):
                parts = import_stmt.split(" ")
                if len(parts) >= 4 and "as" in parts:
                    original_name = parts[parts.index("import") + 1]
                    alias = parts[parts.index("as") + 1]
                    self.alias_mapping[alias] = original_name

    def _gather_attribute_chain(self, node: cst.Attribute | cst.Name) -> list[str]:
        """Recursively gather the full attribute chain into a list of names.

        Args:
            node: The current node to process

        Returns:
            List of attribute names in order from left to right
        """
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
        """Process attribute access expressions and potentially simplify them.

        Args:
            original_node: Original Attribute node
            updated_node: Updated Attribute node after visiting children

        Returns:
            Transformed node (either simplified Name or original Attribute)
        """
        names = self._gather_attribute_chain(updated_node)

        node_name = names[-1]

        if node_name in self.local_names:
            return cst.Name(value=node_name)

        return updated_node

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:
        """Process name nodes and resolve aliases.

        Args:
            original_node: Original Name node
            updated_node: Updated Name node after visiting children

        Returns:
            Transformed name node with alias resolved if applicable
        """
        if updated_node.value in self.alias_mapping:
            # Replace alias with original name
            return cst.Name(
                value=self.alias_mapping[updated_node.value],
                lpar=updated_node.lpar,
                rpar=updated_node.rpar,
            )
        return updated_node


def _get_class_from_unbound_method(method: Callable[..., Any]) -> type | None:
    qualname = method.__qualname__
    parts = qualname.split(".")
    if len(parts) < 2:
        return None
    class_qualname = ".".join(parts[:-1])
    import gc

    for obj in gc.get_objects():
        try:
            object_is_type = isinstance(obj, type)
        except:  # noqa: E722
            # Skip objects that don't support isinstance() check (e.g. OpenAI's pandas proxy)
            continue
        if object_is_type and getattr(obj, "__qualname__", None) == class_qualname:
            return obj
    return None


def _clean_source_from_string(source: str, exclude_fn_body: bool = False) -> str:
    source = dedent(source)
    module = cst.parse_module(source)
    transformer = _RemoveDocstringTransformer(exclude_fn_body=exclude_fn_body)
    new_module = module.visit(transformer)
    return new_module.code.rstrip()


def get_class_source_from_method(method: Callable[..., Any]) -> str:
    cls = _get_class_from_unbound_method(method)
    if cls is None:
        raise ValueError("Cannot determine class from method via gc")
    source = inspect.getsource(cls)
    return _clean_source_from_string(source)


class _DependencyCollector:
    """Collects all dependencies for a function."""

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
        local_assignment_collector = _LocalAssignmentCollector()
        local_assignment_collector.visit(fn_tree)
        local_assignments = local_assignment_collector.assignments

        # Collect parameter names from dependency functions.
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

            # Skip global assignments that are used as function parameters.
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

    def _collect_imports_and_source_code(
        self, definition: Callable[..., Any] | type, include_source: bool
    ) -> None:
        try:
            if isinstance(definition, property):
                if definition.fget is None:
                    return
                definition = definition.fget

            elif isinstance(definition, cached_property):
                definition = definition.func
            elif (
                hasattr(definition, "func")
                and getattr(definition, "__name__", None) is None
            ):
                definition = definition.func  # pyright: ignore [reportFunctionMemberAccess]

            # For methods, if __qualname__ contains a dot, does not include "<locals>" (global)
            # or if it is local (contains "<locals>"), capture the entire class.
            if (
                "." in definition.__qualname__
                and inspect.getmodule(definition) is not None
            ):
                try:
                    source = get_class_source_from_method(definition)
                except ValueError:
                    # Fallback: clean only the function source.
                    source = _clean_source_code(definition)
                if definition.__qualname__ in self.visited_functions:
                    return
                self.visited_functions.add(definition.__qualname__)
            else:
                if definition.__qualname__ in self.visited_functions:
                    return
                self.visited_functions.add(definition.__qualname__)
                source = _clean_source_code(definition)

            module = inspect.getmodule(definition)
            if not module or _is_third_party(module, self.site_packages):
                return

            module_source = inspect.getsource(module)
            module_tree = ast.parse(module_source)
            fn_tree = ast.parse(source)

            name_collector = _NameCollector()
            name_collector.visit(fn_tree)
            used_names = list(dict.fromkeys(name_collector.used_names))

            import_collector = _ImportCollector(used_names, self.site_packages)
            import_collector.visit(module_tree)
            new_imports: set[str] = {
                import_stmt
                for import_stmt in import_collector.imports
                if import_stmt not in source
            }
            self.imports.update(new_imports)
            self.fn_internal_imports.update(import_collector.imports - new_imports)
            self.user_defined_imports.update(import_collector.user_defined_imports)

            if include_source:
                for user_defined_import in self.user_defined_imports:
                    source = source.replace(user_defined_import, "")
                self.source_code.insert(0, source)

            self._collect_assignments_and_imports(
                fn_tree, module_tree, used_names, module_source
            )
            definition_collector = _DefinitionCollector(
                module, used_names, self.site_packages
            )
            definition_collector.visit(fn_tree)
            for collected_definition in definition_collector.definitions_to_include:
                self._collect_imports_and_source_code(collected_definition, True)
            for collected_definition in definition_collector.definitions_to_analyze:
                self._collect_imports_and_source_code(collected_definition, False)

        except (OSError, TypeError):  # pragma: no cover
            pass

    def _collect_required_dependencies(
        self, imports: set[str]
    ) -> dict[str, DependencyInfo]:
        stdlib_modules = set(sys.stdlib_module_names)
        installed_packages = {
            dist.name: dist for dist in importlib.metadata.distributions()
        }
        import_to_dist = importlib.metadata.packages_distributions()

        dependencies = {}
        for import_stmt in imports:
            parts = import_stmt.strip().split()
            root_module = parts[1].split(".")[0]
            if root_module in stdlib_modules:
                continue

            dist_names = import_to_dist.get(root_module, [root_module])
            for dist_name in dist_names:
                # only >= 3.12 properly discovers this in testing due to structure
                if dist_name == "lilypad":  # pragma: no cover
                    dist_name = "python-lilypad"
                if dist_name not in installed_packages:  # pragma: no cover
                    continue
                dist = installed_packages[dist_name]
                extras = []
                for extra in dist.metadata.get_all("Provides-Extra", []):
                    extra_reqs = dist.requires or []
                    extra_deps = [
                        Requirement(r).name
                        for r in extra_reqs
                        if f"extra == '{extra}'" in r
                    ]
                    if extra_deps and all(
                        dep in installed_packages for dep in extra_deps
                    ):
                        extras.append(extra)

                dependencies[dist.name] = {
                    "version": dist.version,
                    "extras": extras if extras else None,
                }

        return dependencies

    @classmethod
    def _map_child_to_parent(
        cls,
        child_to_parent: dict[ast.AST, ast.AST | None],
        node: ast.AST,
        parent: ast.AST | None = None,
    ) -> None:
        child_to_parent[node] = parent
        for _field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for child in value:
                    if isinstance(child, ast.AST):
                        cls._map_child_to_parent(child_to_parent, child, node)
            elif isinstance(value, ast.AST):
                cls._map_child_to_parent(child_to_parent, value, node)

    def collect(
        self, fn: Callable[..., Any]
    ) -> tuple[list[str], list[str], list[str], dict[str, DependencyInfo]]:
        """Returns the imports and source code for a function and its dependencies."""
        self._collect_imports_and_source_code(fn, True)

        local_names = set()
        for code in self.source_code + self.assignments:
            tree = ast.parse(code)

            child_to_parent = {}

            self._map_child_to_parent(child_to_parent, tree)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef | ast.ClassDef):
                    # We build a "child_to_parent" map so that for each AST node, we can find its parent node.
                    # In particular, if `parent` is an `ast.Module`, that means the current `node`
                    # (e.g., a FunctionDef or ClassDef) is defined at the "top level" of the module.
                    # This allows us to distinguish top-level definitions from those nested in a class or function.
                    #
                    # For example, if we only want to process function or class definitions that appear
                    # directly in the module (not nested in another class or function), we can check:
                    #   if isinstance(parent, ast.Module):
                    #       # node is a top-level definition

                    parent = child_to_parent.get(node)
                    if isinstance(parent, ast.Module):
                        # node is a top-level definition
                        local_names.add(node.name)

        rewriter = _QualifiedNameRewriter(local_names, self.user_defined_imports)

        assignments = []
        for code in self.assignments:
            tree = cst.parse_module(code)
            new_tree = tree.visit(rewriter)
            assignments.append(new_tree.code)

        source_code = []
        for code in self.source_code:
            tree = cst.parse_module(code)
            new_tree = tree.visit(rewriter)
            source_code.append(new_tree.code)

        required_dependencies = self._collect_required_dependencies(
            self.imports | self.fn_internal_imports
        )

        return (
            list(self.imports),
            list(dict.fromkeys(assignments)),
            source_code,
            required_dependencies,
        )


def run_ruff(code: str) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp_file:
        tmp_file.write(code)
        tmp_path = Path(tmp_file.name)

    try:
        subprocess.run(
            ["ruff", "check", "--isolated", "--select=I", "--fix", str(tmp_path)],
            check=True,
            capture_output=True,
            text=True,
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


class Closure(BaseModel):
    """Represents the closure of a function."""

    name: str
    signature: str
    code: str
    hash: str
    dependencies: dict[str, DependencyInfo]

    @classmethod
    @lru_cache(maxsize=128)
    def from_fn(cls, fn: Callable[..., Any]) -> Closure:
        """Create a closure from a function.

        Args:
            fn: The function to analyze

        Returns:
            Closure: The closure of the function.
        """
        collector = _DependencyCollector()
        imports, assignments, source_code, dependencies = collector.collect(fn)
        code = "{imports}\n\n{assignments}\n\n{source_code}".format(
            imports="\n".join(imports),
            assignments="\n".join(assignments),
            source_code="\n\n".join(source_code),
        )
        formatted_code = run_ruff(code)
        hash_value = hashlib.sha256(formatted_code.encode("utf-8")).hexdigest()
        return cls(
            name=get_qualified_name(fn),
            signature=run_ruff(_clean_source_code(fn, exclude_fn_body=True)).strip(),
            code=formatted_code,
            hash=hash_value,
            dependencies=dependencies,
        )


__all__ = ["Closure"]
