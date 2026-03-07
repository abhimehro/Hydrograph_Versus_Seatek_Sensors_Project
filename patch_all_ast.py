import ast
import sys

def modify_config():
    with open("utils/config.py", "r") as f:
        tree = ast.parse(f.read())

    class ConfigTransformer(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            if node.name == "__init__":
                has_max_size = any(
                    isinstance(stmt, ast.Assign) and
                    isinstance(stmt.targets[0], ast.Attribute) and
                    stmt.targets[0].attr == "max_file_size_bytes"
                    for stmt in node.body
                )

                if not has_max_size:
                    max_size_assign = ast.Assign(
                        targets=[ast.Attribute(
                            value=ast.Name(id="self", ctx=ast.Load()),
                            attr="max_file_size_bytes",
                            ctx=ast.Store()
                        )],
                        value=ast.BinOp(
                            left=ast.BinOp(
                                left=ast.Constant(value=100),
                                op=ast.Mult(),
                                right=ast.Constant(value=1024)
                            ),
                            op=ast.Mult(),
                            right=ast.Constant(value=1024)
                        )
                    )
                    node.body.append(max_size_assign)
            return node

    tree = ConfigTransformer().visit(tree)
    with open("utils/config.py", "w") as f:
        f.write(ast.unparse(tree))
    print("Updated config.py")

def inject_validation(filepath):
    with open(filepath, "r") as f:
        tree = ast.parse(f.read())

    class FileOpTransformer(ast.NodeTransformer):
        def visit_Module(self, node):
            # Check if import already exists
            has_import = any(
                isinstance(stmt, ast.ImportFrom) and stmt.module == "utils.security"
                for stmt in node.body
            )

            if not has_import:
                # Add import right after the docstring or first existing import
                import_idx = 0
                for i, stmt in enumerate(node.body):
                    if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                        import_idx = i
                        break
                if import_idx == 0 and len(node.body) > 0 and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                    import_idx = 1

                node.body.insert(import_idx, ast.ImportFrom(
                    module="utils.security",
                    names=[ast.alias(name="validate_file_size", asname=None)],
                    level=0
                ))

            return self.generic_visit(node)

        def visit_Call(self, node):
            self.generic_visit(node)
            return node

        def visit_FunctionDef(self, node):
            self.generic_visit(node)

            # Find pd.read_excel or pd.ExcelFile calls
            new_body = []
            for stmt in node.body:
                if isinstance(stmt, ast.Try):
                    try_body = []
                    for try_stmt in stmt.body:
                        # Find assignments like df = pd.read_excel(file_path)
                        if isinstance(try_stmt, ast.Assign) and isinstance(try_stmt.value, ast.Call):
                            func = try_stmt.value.func
                            if isinstance(func, ast.Attribute) and func.attr in ("read_excel", "ExcelFile"):
                                # Ensure it's pandas by checking the module name
                                is_pd = False
                                if isinstance(func.value, ast.Name) and func.value.id == "pd":
                                    is_pd = True
                                elif isinstance(func.value, ast.Name) and func.value.id == "pandas":
                                    is_pd = True

                                if is_pd:
                                    # We found a pandas file read call.
                                    # Extract the file path argument. It's usually the first argument.
                                    if try_stmt.value.args:
                                        file_arg = try_stmt.value.args[0]

                                        # But read_excel could take an ExcelFile object, we only want string/Path
                                        # In our codebase:
                                        # DataLoader: pd.read_excel(self.config.summary_file) -> self.config.summary_file
                                        # DataLoader: pd.ExcelFile(self.config.hydro_file) -> self.config.hydro_file
                                        # Processor: pd.read_excel(self.file_path) -> self.file_path
                                        # We can inject validation if it looks like an attribute access (self.X)
                                        if isinstance(file_arg, ast.Attribute):
                                            # We need to construct max_file_size_bytes reference based on context.
                                            # If there's self.config, use self.config.max_file_size_bytes.
                                            # If not, try to get config globally or instantiate it, or just use a constant.
                                            # In processor.py, it's just `self.file_path`. We don't have config.
                                            # Let's import Config and instantiate or just use hardcoded limit for now,
                                            # or pass max_size if available.

                                            max_size_arg = None
                                            if filepath == "utils/data_loader.py":
                                                max_size_arg = ast.Attribute(
                                                    value=ast.Attribute(
                                                        value=ast.Name(id="self", ctx=ast.Load()),
                                                        attr="config",
                                                        ctx=ast.Load()
                                                    ),
                                                    attr="max_file_size_bytes",
                                                    ctx=ast.Load()
                                                )
                                            else:
                                                # Fallback: import Config and use its default
                                                max_size_arg = ast.BinOp(
                                                    left=ast.BinOp(
                                                        left=ast.Constant(value=100),
                                                        op=ast.Mult(),
                                                        right=ast.Constant(value=1024)
                                                    ),
                                                    op=ast.Mult(),
                                                    right=ast.Constant(value=1024)
                                                )

                                            val_call = ast.Expr(
                                                value=ast.Call(
                                                    func=ast.Name(id="validate_file_size", ctx=ast.Load()),
                                                    args=[file_arg, max_size_arg],
                                                    keywords=[]
                                                )
                                            )
                                            try_body.append(val_call)
                        try_body.append(try_stmt)
                    stmt.body = try_body
                elif isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                     # Non-try block pd.read_excel
                     func = stmt.value.func
                     if isinstance(func, ast.Attribute) and func.attr in ("read_excel", "ExcelFile"):
                         if isinstance(func.value, ast.Name) and func.value.id in ("pd", "pandas"):
                             if stmt.value.args and isinstance(stmt.value.args[0], ast.Attribute):
                                 file_arg = stmt.value.args[0]
                                 max_size_arg = ast.BinOp(left=ast.BinOp(left=ast.Constant(value=100), op=ast.Mult(), right=ast.Constant(value=1024)), op=ast.Mult(), right=ast.Constant(value=1024))
                                 val_call = ast.Expr(value=ast.Call(func=ast.Name(id="validate_file_size", ctx=ast.Load()), args=[file_arg, max_size_arg], keywords=[]))
                                 new_body.append(val_call)
                new_body.append(stmt)
            node.body = new_body
            return node

    tree = FileOpTransformer().visit(tree)
    with open(filepath, "w") as f:
        f.write(ast.unparse(tree))
    print(f"Updated {filepath}")

modify_config()
inject_validation("utils/data_loader.py")
inject_validation("utils/processor.py")

# Special handling for utils.utils.load_excel_file
def inject_utils_validation():
    with open("utils/utils.py", "r") as f:
        tree = ast.parse(f.read())

    class UtilsTransformer(ast.NodeTransformer):
        def visit_Module(self, node):
            import_idx = 0
            for i, stmt in enumerate(node.body):
                if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    import_idx = i
                    break
            if import_idx == 0 and len(node.body) > 0 and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                import_idx = 1

            node.body.insert(import_idx, ast.ImportFrom(
                module="utils.security",
                names=[ast.alias(name="validate_file_size", asname=None)],
                level=0
            ))
            return self.generic_visit(node)

        def visit_FunctionDef(self, node):
            if node.name == "load_excel_file":
                new_body = []
                for stmt in node.body:
                    if isinstance(stmt, ast.Try):
                        # Insert validate_file_size before the `with ExcelFile...`
                        val_call = ast.Expr(
                            value=ast.Call(
                                func=ast.Name(id="validate_file_size", ctx=ast.Load()),
                                args=[
                                    ast.Name(id="file_path", ctx=ast.Load()),
                                    ast.BinOp(
                                        left=ast.BinOp(
                                            left=ast.Constant(value=100),
                                            op=ast.Mult(),
                                            right=ast.Constant(value=1024)
                                        ),
                                        op=ast.Mult(),
                                        right=ast.Constant(value=1024)
                                    )
                                ],
                                keywords=[]
                            )
                        )
                        stmt.body.insert(0, val_call)
                    new_body.append(stmt)
                node.body = new_body
            return self.generic_visit(node)

    tree = UtilsTransformer().visit(tree)
    with open("utils/utils.py", "w") as f:
        f.write(ast.unparse(tree))
    print("Updated utils/utils.py")

inject_utils_validation()
