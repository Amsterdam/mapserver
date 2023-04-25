from contextlib import contextmanager

indent: int = 0


def p(*strs: list[str]):
    print("  " * indent, end="")
    print(strs[0], end="")
    if len(strs) > 1:
        print(" ", end="")
    print_quoted(strs[1:])


def q(*strs: list[str]):
    print("  " * indent, end="")
    print_quoted(strs)


def print_quoted(strs: list[str]):
    print(*map(repr, strs))


@contextmanager
def block(typ: str):
    p(typ)
    global indent
    indent += 1
    yield
    indent -= 1
    p("END")
