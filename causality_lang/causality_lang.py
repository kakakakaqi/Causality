from __future__ import annotations
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Sequence, cast
import sys


FANCY_DEBUG_INFO: bool = True
RED = (255, 0, 0)
LIGHTRED = (255, 127, 127)
GREEN = (0, 255, 0)
LIGHTGREEN = (127, 255, 127)
BLUE = (0, 0, 255)
LIGHTBLUE = (127, 127, 255)


def format_str(
    txt: str,
    color: tuple[int, int, int] | Sequence[int] = (255, 255, 255),
    bold: bool = False,
    dim: bool = False,
    italic: bool = False,
    underline: bool = False,
    blink: bool = False,
    fast_blink: bool = False,
    reverse: bool = False,
    strikethrough: bool = False,
    double_under: bool = False,
):
    if FANCY_DEBUG_INFO:
        attrs = [
            (1, bold),
            (2, dim),
            (3, italic),
            (4, underline),
            (5, blink),
            (6, fast_blink),
            (7, reverse),
            (9, strikethrough),
            (21, double_under),
        ]
        encoding = ";".join(
            [
                str(code) for code, enabled in attrs if enabled
            ]  # add the encoding if the param is true
            + ["38;2"]  # RBG
            + list(map(str, color))  # add the color encodings
        )
        return f"\033[{encoding}m{txt}\033[0m"
    else:
        return txt


class Nodelang_error(Exception): ...  # marker class for custom errors


def nodelang_exception(base_error: type[BaseException]) -> type[BaseException]:
    # AI written
    """
    Create a Nodelang variant of any exception class that is safely subclassable.
    """
    if not (isinstance(base_error, type) and issubclass(base_error, BaseException)):
        raise TypeError(f"Expected an exception class, got {base_error!r}")

    # Already in hierarchy - return as-is
    if issubclass(base_error, Nodelang_error):
        return base_error

    # Use Any for bases tuple to bypass strict type checker validation
    bases: tuple[Any, ...] = (base_error, Nodelang_error)

    # CRITICAL EDGE CASES: Exception/BaseException create MRO conflicts
    if base_error in (Exception, BaseException):
        # Fall back to direct subclass of Nodelang_error
        bases = (Nodelang_error,)

    # Cast the result to tell type checker we know it's correct
    return cast(
        type[BaseException],
        type(
            f"Nodelang{base_error.__name__}",
            bases,
            {
                "__module__": __name__,
                "__doc__": f"Nodelang variant of {base_error.__name__}",
            },
        ),
    )


def handle_notelang_exception(func: Callable):
    @wraps(func)
    def wrapper(self, *args, **kwdargs):
        try:
            func(self, *args, **kwdargs)
        except BaseException as e:
            if isinstance(e, Nodelang_error):
                print(e)
            else:
                raise e
            sys.exit()

    return wrapper


class Node_manager:
    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}

    def add(self, node: Node):
        # if there is already that node
        if node.id in self._nodes.keys():
            raise SyntaxWarning("Redefinition of a node")
        self._nodes[node.id] = node

    def get(self, id: str) -> Node:
        if id not in self._nodes.keys():
            raise SyntaxError("Nonexistant node")
        return self._nodes[id]

    def get_all(self) -> list[Node]:
        return list(self._nodes.values())

    def find_node(self, id: str) -> Node:
        """BFS for node with an alias of id"""
        nd = self.get(id)
        frontier: list[Node] = [nd]

        while len(frontier):
            node = frontier.pop(0)
            if node.id == id:
                return node
            frontier.extend(node.children.get_all())

        raise RuntimeError("Not a thing")


class Connection_manager:
    def __init__(self) -> None:
        self._conns: dict[str, list[Node]] = {}

    def add(self, conn_type: str, nodes: list[Node]):
        if conn_type not in self._conns.keys():
            self._conns[conn_type] = []
        self._conns[conn_type].extend(nodes)


@dataclass
class Node:
    id: str
    name: str
    content: str
    children: Node_manager = field(default_factory=Node_manager)
    connections: Connection_manager = field(default_factory=Connection_manager)


class Graph:
    def __init__(self) -> None:
        self.nodes: Node_manager = Node_manager()

    def format_debug_info(self, debug_info: dict[str, Any]) -> str:
        features, values = debug_info.keys(), debug_info.values()
        max_len = max((map(len, features)))

        ret = ""

        for feature, value in zip(features, values):
            feature = feature.replace(
                "_", " "
            )  # _ is inevitable when passing in as **kwdargs, therefore reformat as ' ' here
            feature = f"<{feature}>"
            feature = format_str(feature, LIGHTGREEN, double_under=True)
            ret += f"{feature} {value}\n"

        return ret

    def parse(self, code: str):
        lines = [line.strip() for line in code.split("\n") if line.strip() != ""]
        for idx, line in enumerate(lines):
            # DEBUG INFO
            # context
            context_size = 3
            context = "".join(
                [
                    # |line#| line
                    format_str(f"\n|{j + 1}| {lines[j]}", underline=(idx == j))
                    # j - context size -> j + context size
                    for j in range(idx - context_size, idx + context_size + 1)
                    # if j in range
                    if j >= 0 and j < len(lines)
                ]
            )

            debug_info = {"context": context}

            # parsing
            self.parse_line(line, debug_info)

    @handle_notelang_exception
    def parse_line(self, line: str, debug_info: dict[str, Any]):
        # annotation
        if line[0:1] == "#":
            return
        # definition
        if (idx := line.find(":")) != -1:
            left = line[:idx].strip(" ")
            right = line[idx + 1 :].strip(" ")

            # check for alias
            if left[-1] == ")":
                alias = left[left.rfind("(") :][1:-1]
            else:
                alias = ""
            alias.strip(" ")
            name = left[: left.rfind("(")].strip(" ")

            if not len(alias):
                alias = name

            content = right.strip(" ")

            nd = Node(alias, name, content)
            self.nodes.add(nd)

            # print(f"alias: {alias}")
            # print(f"content: {content}")
            # print(f"node: {nd}")
            return

        # elaborations
        idx0 = line.find("<")
        idx1 = line.find(">")
        # if there is not an occurance of > or if > is before <, then it's an elaboration
        if idx0 != -1 and idx1 == -1 or idx1 < idx0:
            # elaboration
            left = line[:idx0].strip(" ")
            right = line[idx0 + 1 :].strip(" ")

            # find sub alias
            if right[0] == "(":
                alias = right[1 : right.find(")")]
            else:
                alias = ""
            alias.strip(" ")
            content = right[right.find(")") + 1 :].strip(" ")

            if not len(alias):
                alias = content

            new = Node(alias, alias, content)
            nd = self.nodes.get(left)
            nd.children.add(new)
            return

        # logical connection
        if idx0 < idx1:
            left = line[:idx0].strip(" ")
            connection = line[idx0 + 1 : idx1].strip(" ")
            right = line[idx1 + 1 :].strip(" ")

            origin = self.nodes.find_node(left)
            dests = []  # TODO: no append
            for txt in right.split("&"):
                txt.strip(" ")
                try:
                    nd = self.nodes.find_node(txt)
                except:
                    nd = Node(txt, txt, txt)
                dests.append(nd)

            origin.connections.add(connection, dests)

        raise nodelang_exception(SyntaxError)(
            f"{format_str('Invalid syntax', LIGHTRED, bold=True)}\n{self.format_debug_info(debug_info)}"
        )


if __name__ == "__main__":
    parser = Graph()
    lines = """
    protestant reformation (protref) : some event in Europe
    protref < (prots) there were protestants involved in this
    bozo
    cheese (cs): o hail the cheese
    """
    parser.parse(lines)
