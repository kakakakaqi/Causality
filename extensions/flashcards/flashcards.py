# flashcards essentially ask about the edges of the graph
# from typing import TYPE_CHECKING
from dataclasses import dataclass
import os
from causality_lang import Node, Node_manager, Graph


@dataclass
class Question:
    question: str
    answer: str


_graph: Graph | None = None
_questions: list[Question] = []


def load(graph: Graph):
    global _graph
    _graph = graph


def attribute_questions(graph: Graph | None = None):
    graph = graph or _graph
    assert graph is not None
    nodes = graph.nodes
    for node in nodes.get_all():
        for child in node.children.get_all():
            _questions.append(
                Question(
                    question=f"{node.content} . {child.name} = ?",
                    answer=f"{child.content}",
                )
            )


def health_check():
    full_code = """
    protestant reformation (protref) : religious movement in 16th century Europe
    protref < (causes) social and political factors
    protref < (effects) religious diversity
    protref <caused> reldiv
    religious diversity (reldiv) : coexistence of multiple religions
    """
    (g := Graph()).parse(full_code)
    node_manager = g.nodes
    load(g)
    assert node_manager is not None
    global nodes
    nodes = node_manager.get_all()
    attribute_questions(g)


if __name__ == "__main__":
    health_check()
    print(_questions)
