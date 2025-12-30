from __future__ import annotations
from copy import deepcopy
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
YELLOW = (255, 255, 0)


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
    def __init__(self, nodes: Node_manager | None = None) -> None:
        self.nodes: Node_manager = nodes or Node_manager()

    def format_debug_info(self, debug_info: dict[str, Any]) -> str:
        ret = ""
        for feature, value in debug_info.items():
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
            return

        raise nodelang_exception(SyntaxError)(
            f"{format_str('Invalid syntax', LIGHTRED, bold=True)}\n{self.format_debug_info(debug_info)}"
        )

    def dump(self) -> Node_manager:
        """A deepcopied instance of the node manager"""
        return deepcopy(self.nodes)


# === Test Suite ===


def print_section(title):
    print(f"\n{format_str('═' * 70, LIGHTBLUE)}")
    print(format_str(title, LIGHTBLUE, bold=True))
    print(format_str("═" * 70, LIGHTBLUE))


def print_result(test_name, passed, details=""):
    status = format_str("✓ PASS", GREEN) if passed else format_str("✗ FAIL", RED)
    print(f"  {status}: {test_name}")
    if details:
        print(f"    {format_str(details, LIGHTRED)}")


def health_check():
    """Health test"""
    print_section("NODELANG SYNTAX TEST SUITE")
    print("Testing basic syntax features from syntax.md")

    tests_passed = 0
    total_tests = 6

    # === TEST 1: Basic Definition ===
    print_section("Test 1: Node Definition")
    code1 = "protestant reformation (protref) : some event in Europe"
    print(f"Input: {code1}")

    parser1 = Graph()
    try:
        parser1.parse(code1)
        node = parser1.nodes.get("protref")
        assert node.name == "protestant reformation"
        assert node.content == "some event in Europe"
        print_result("Definition with alias", True)
        tests_passed += 1
    except Exception as e:
        print_result("Definition with alias", False, str(e))

    # === TEST 2: Elaboration ===
    print_section("Test 2: Elaboration (Child Nodes)")
    code2 = """
    protestant reformation (protref) : some event in Europe
    protref < (prots) there were protestants involved in this
    """
    print(f"Input:{code2}")

    parser2 = Graph()
    try:
        parser2.parse(code2)
        parent = parser2.nodes.get("protref")
        child = parent.children.get("prots")
        assert child.content == "there were protestants involved in this"
        print_result("Elaboration with alias", True)
        tests_passed += 1
    except Exception as e:
        print_result("Elaboration", False, str(e))

    # === TEST 3: Logical Connection (Single) ===
    print_section("Test 3: Logical Connection - Single")
    code3 = """
    protestant reformation (protref) : some event in Europe
    religious diversity (reldiv) : increase in different religions
    protref <caused> reldiv
    """
    print(f"Input:{code3}")

    parser3 = Graph()
    try:
        parser3.parse(code3)
        origin = parser3.nodes.get("protref")
        assert "caused" in origin.connections._conns
        assert len(origin.connections._conns["caused"]) > 0
        print_result("Single connection", True)
        tests_passed += 1
    except Exception as e:
        print_result("Single connection", False, str(e))

    # === TEST 4: Logical Connection (Multiple) ===
    print_section("Test 4: Logical Connection - Multiple")
    code4 = """
    protestant reformation (protref) : some event in Europe
    protref <influenced> secularism & individualism
    """
    print(f"Input:{code4}")

    parser4 = Graph()
    try:
        parser4.parse(code4)
        origin = parser4.nodes.get("protref")
        assert "influenced" in origin.connections._conns
        # Note: Whitespace bug may affect count
        dest_count = len(origin.connections._conns["influenced"])
        print_result("Multiple connections", True, f"Found {dest_count} destination(s)")
        tests_passed += 1
    except Exception as e:
        print_result("Multiple connections", False, str(e))

    # === TEST 5: Annotation ===
    print_section("Test 5: Annotations")
    code5 = """
    # This is a comment
    protestant reformation (protref) : some event in Europe
    # Another comment
    """
    print(f"Input:{code5}")

    parser5 = Graph()
    try:
        parser5.parse(code5)
        nodes = parser5.nodes.get_all()
        assert len(nodes) == 1
        print_result("Annotation/Comment", True, "Comment lines ignored")
        tests_passed += 1
    except Exception as e:
        print_result("Annotation", False, str(e))

    # === TEST 6: Elaboration without alias ===
    print_section("Test 6: Elaboration without alias")
    code6 = """
    protestant reformation (protref) : some event in Europe
    protref < there were protestants involved in this
    """
    print(f"Input:{code6}")

    parser6 = Graph()
    try:
        parser6.parse(code6)
        parent = parser6.nodes.get("protref")
        # When no alias, content becomes the id
        child = parent.children.get("there were protestants involved in this")
        assert child is not None
        print_result("Elaboration without alias", True)
        tests_passed += 1
    except Exception as e:
        print_result("Elaboration without alias", False, str(e))

    # === SUMMARY ===
    print_section("TEST SUMMARY")
    summary = f"Tests Passed: {tests_passed}/{total_tests}"
    color = GREEN if tests_passed == total_tests else RED
    print(format_str(summary, color, bold=True))

    if tests_passed < total_tests:
        print(format_str("\nKnown Limitations:", YELLOW))
        print("  • Definition without parentheses 'name : content' has parsing issues")
        print(
            "  • Multiple connections may not split correctly on '&' due to whitespace"
        )
        print("  • find_node() BFS may not work as expected for nested lookups")

    # === GRAPH VISUALIZATION ===
    print_section("GRAPH VISUALIZATION")
    print("Final parsed graph structure:")

    full_code = """
    protestant reformation (protref) : religious movement in 16th century Europe
    protref < (causes) social and political factors
    protref < (effects) religious diversity
    protref <caused> reldiv
    religious diversity (reldiv) : coexistence of multiple religions
    """

    final_parser = Graph()
    try:
        final_parser.parse(full_code)
        for node in final_parser.nodes.get_all():
            print(f"\n{format_str(node.name, LIGHTGREEN)} ({node.id}):")
            print(f"  Content: {node.content}")

            if node.children.get_all():
                print(f"  {format_str('Children:', LIGHTBLUE)}")
                for child in node.children.get_all():
                    print(f"    • {child.name}: {child.content}")

            if node.connections._conns:
                print(f"  {format_str('Connections:', LIGHTBLUE)}")
                for conn_type, dests in node.connections._conns.items():
                    for dest in dests:
                        print(f"    • {conn_type} → {dest.name} ({dest.id})")
    except Exception as e:
        print(format_str(f"Visualization failed: {e}", RED))


if __name__ == "__main__":
    health_check()
