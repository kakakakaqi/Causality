# flashcards essentially ask about the edges of the graph
# from typing import TYPE_CHECKING
import os
from causality_lang import Node, Node_manager, Graph

node_manager: Node_manager | None = None


def load(nodes: Node_manager):
    node_manager = nodes


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
    load(g.nodes)
    assert node_manager is not None
    nodes = node_manager.get_all()


if __name__ == "__main__":
    health_check()
