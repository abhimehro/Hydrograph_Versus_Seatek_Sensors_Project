import ast
import sys

def modify_data_loader():
    with open("utils/data_loader.py", "r") as f:
        source = f.read()

    tree = ast.parse(source)

    class DataLoaderTransformer(ast.NodeTransformer):
        def visit_ClassDef(self, node):
            if node.name == "DataLoader":
                # Ensure validate_file_size is imported at module level
                pass
            return self.generic_visit(node)

        def visit_FunctionDef(self, node):
            if node.name in ("_load_summary_data", "_load_hydro_data"):
                # We need to insert the validation call right after the try block or logging
                new_body = []
                for stmt in node.body:
                    if isinstance(stmt, ast.Try):
                        # Inside the try block
                        try_body = []
                        for try_stmt in stmt.body:
                            if isinstance(try_stmt, ast.Assign) and isinstance(try_stmt.value, ast.Call):
                                func = try_stmt.value.func
                                if isinstance(func, ast.Attribute) and func.attr == "read_excel":
                                    # Insert validate call before read_excel
                                    val_call = ast.Expr(
                                        value=ast.Call(
                                            func=ast.Name(id="validate_file_size", ctx=ast.Load()),
                                            args=[
                                                ast.Attribute(value=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="config", ctx=ast.Load()), attr="summary_file", ctx=ast.Load()),
                                                ast.Attribute(value=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="config", ctx=ast.Load()), attr="max_file_size_bytes", ctx=ast.Load())
                                            ],
                                            keywords=[]
                                        )
                                    )
                                    try_body.append(val_call)
                                elif isinstance(func, ast.Attribute) and func.attr == "ExcelFile":
                                    # Insert validate call before ExcelFile
                                    val_call = ast.Expr(
                                        value=ast.Call(
                                            func=ast.Name(id="validate_file_size", ctx=ast.Load()),
                                            args=[
                                                ast.Attribute(value=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="config", ctx=ast.Load()), attr="hydro_file", ctx=ast.Load()),
                                                ast.Attribute(value=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="config", ctx=ast.Load()), attr="max_file_size_bytes", ctx=ast.Load())
                                            ],
                                            keywords=[]
                                        )
                                    )
                                    try_body.append(val_call)

                            # Filter out our previous crude patch if it exists
                            if isinstance(try_stmt, ast.If):
                                test = try_stmt.test
                                if isinstance(test, ast.BoolOp) and isinstance(test.values[-1], ast.Compare):
                                    comp = test.values[-1]
                                    if isinstance(comp.left, ast.Attribute) and comp.left.attr == "st_size":
                                        continue # skip our old manual check

                            try_body.append(try_stmt)
                        stmt.body = try_body
                    new_body.append(stmt)
                node.body = new_body
            return node

    # Add import
    import_stmt = ast.ImportFrom(module='utils.security', names=[ast.alias(name='validate_file_size', asname=None)], level=0)
    tree.body.insert(5, import_stmt) # Insert after other imports

    transformer = DataLoaderTransformer()
    modified_tree = transformer.visit(tree)
    ast.fix_missing_locations(modified_tree)

    # Use astor if available, else standard ast.unparse (Python 3.9+)
    try:
        new_source = ast.unparse(modified_tree)
        with open("utils/data_loader.py", "w") as f:
            f.write(new_source)
        print("Successfully modified utils/data_loader.py")
    except AttributeError:
        print("Error: ast.unparse not available. Please use Python 3.9+")

modify_data_loader()
