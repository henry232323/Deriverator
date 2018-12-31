import ast
from math import sin, cos, tan, sqrt, e, log, pi
from pprint import parseprint

def addition(a, b):
    #print(f"adding {a} and {b}")
    return ast.BinOp(left=derive(a), right=derive(b), op=ast.Add())
    return f"({derive(a)} + {derive(b)})"

def subtraction(a, b):
    return ast.BinOp(left=derive(a), right=derive(b), op=ast.Sub())
    return f"({derive(a)} - {derive(b)})"

def multiply(a, b):
    #print(f"multiplying {a} and {b}")
    leftmul = ast.BinOp(
        left=a,
        right=derive(b),
        op=ast.Mult()
    )
    rightmul = ast.BinOp(
        left=b,
        right=derive(a),
        op=ast.Mult()
    )
    return ast.BinOp(left=leftmul, right=rightmul, op=ast.Add())
    return f"({a} * {derive(b)} + {b} * {derive(a)})"

def divide(a, b):
    db = derive(b)
    leftmul = ast.BinOp(
        left=a,
        right=db,
        op=ast.Mult()
    )
    rightmul = ast.BinOp(
        left=b,
        right=derive(a),
        op=ast.Mult()
    )
    topsub = ast.BinOp(left=leftmul, right=rightmul, op=ast.Sub())
    bottompow = ast.BinOp(left=db, right=ast.Num(n=2), op=ast.Pow())
    return ast.BinOp(left=topsub, right=bottompow, op=ast.Div())

    return f"(({a} * {db} - {b} * {derive(a)}) / ({db} ** 2))"

def exponent(a, b):
    """
    return ast.BinOp(
        left=ast.BinOp(
            left=b,
            right=ast.BinOp(left=a,
                            right=ast.Num(n=b.n - 1),
                            op=ast.Pow()
            ),
            op=ast.Mult()
        ),
        right=derive(a),
        op=ast.Mult()
    )
    """
    #print(a, b)
    rs = ast.BinOp(
                left=ast.Num(n=e),
                right=ast.BinOp(
                    left=ast.Call(
                        ast.Name(id='log', ctx=ast.Load()),
                        [a],
                        []
                    ),
                    right=b,
                    op=ast.Mult()
                ),
                op=ast.Pow(),
            )
    return ast.BinOp(
        left=multiply(
            ast.Call(
                ast.Name(id='log', ctx=ast.Load()),
                [a],
                [],
            ),
            b
        ),
        right=rs,
        op=ast.Mult()
    )
    return f"(b * (a ** (b - 1)) * {derive(a)})"

def integer(a):
    #print("convering ints")
    return ast.Num(n=0)
    return "(0)"

def ln(a, base=None):
    if base == None:
        return ast.BinOp(
            left=ast.Num(n=1),
            right=a,
            op=ast.Div(),
        )
    else:
        return ast.BinOp(
            left=ast.Num(n=1),
            right=a,
            op=ast.Div(),
        )

def sinast(a):
    return ast.Call(ast.Name(id="cos", ctx=ast.Load()), [a], [])

def cosast(a):
    #print(1, a)
    return ast.BinOp(
            left=ast.Call(
                ast.Name(id="sin", ctx=ast.Load()),
                [a],
                []
            ),
            right=ast.Num(n = -1),
            op=ast.Mult()
    )

def derive(expr):
    #print(expr)
    if isinstance(expr, ast.BinOp):
        return operations[type(expr.op)](expr.left, expr.right)
    if isinstance(expr, ast.Name):
        #print("its a name", expr.id, expr.id == "x")
        if expr.id == "x":
            return ast.Num(n = 1)
        else:
            return ast.Num(n = 0)
    if isinstance(expr, ast.Num):
        return integer(expr)
    if isinstance(expr, ast.Call):
        fdrv = names.get(expr.func.id)
        if callable(fdrv):
            #print(fdrv)
            return ast.BinOp(
                left=fdrv(*expr.args),
                right=derive(expr.args[0]),
                op=ast.Mult()
            )
        elif isinstance(fdrv, str):
            return ast.BinOp(
                left=ast.Call(
                    ast.Name(id=fdrv, ctx=ast.Load()),
                    expr.args,
                    []
                ),
                right=derive(expr.args[0]),
                op=ast.Mult()
            )
        elif isinstance(fdrv, ast.AST):
            return ast.BinOp(
                left=fdrv,
                right=derive(expr.args[0]),
                op=ast.Mult()
            )
        else:
            #print("err! err!")
            raise RuntimeError(f"{expr.func.id} does not have a defined derivative!")

names = {
    "log": ln,
    "ln": ln,
    "sin": sinast,
    "cos": cosast,
}

operations = {
    ast.Mult: multiply,
    ast.Div: divide,
    ast.Add: addition,
    ast.Sub: subtraction,
    ast.Num: integer,
    ast.Pow: exponent,
}

def main(eq, name="foo", arg="x"):
    expr = f"""
def {name}({arg}):
    print("hello world", {arg})
    """
    p = ast.parse(expr)

    tree = ast.parse(eq)
    expr = list(ast.iter_child_nodes(tree))[0].value
    #parseprint(expr)
    a = derive(expr)
    p.body[0].body = [ast.Return(a)]
    ast.fix_missing_locations(p)
    final = p

    #parseprint(final)
    exec(compile(final, "<deriv>", "exec"), globals(), locals())
    return locals()[name]

import inspect

def fn(x):
    return 2 * x

def ddx(func):
    return main(inspect.getsourcelines(func)[1])

#print(exec(compile(main("2 * x ** 2 + 3"), "<fn>", "exec"), globals()))
quad = main("log(x)", 'quad')
print(quad(1))
