# flashcards essentially ask about the edges of the graph
# from typing import TYPE_CHECKING
from dataclasses import dataclass
import os
from causality_lang.causality_lang import Node, Node_manager, Graph
import causality_lang

from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class Question:
    question: str
    answer: str


_graph: Graph | None = None
_questions: list[Question] = []

llm_client = OpenAI(
    base_url=open("key.key", "r").readlines()[0].strip(),
    api_key=open("key.key", "r").readlines()[1].strip(),
)


def load(graph: Graph):
    global _graph
    _graph = graph


def _call_llm(
    prompt: str, sys_prompt: str = "", model: str = "gpt-4.1-mini", **kwargs
) -> str:
    for i in range(10):
        try:
            resp = llm_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt},
                ],
                **kwargs,
            )
            break
        except Exception as e:
            print(prompt)
            if i == 4:
                raise e
            continue
    return resp.choices[0].message.content.strip()


def llm_question_formatting(
    questions: list[Question] | None = None,
    *,
    max_workers: int = 16,
    model: str = "gpt-3.5-turbo",
    **openai_kwargs,
) -> list[Question]:
    if not questions:
        questions = _questions

    def _task(id: int, prompt: str, sys_prompt: str) -> tuple[int, str]:
        return id, _call_llm(prompt, sys_prompt, model=model, **openai_kwargs)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        sys_prompt = """
You are a formatter that converts a structured question and its corresponding correct answer into a clear, human-readable question.

Task
1. Read the provided structured question and answer.
2. Output only the formatted question.

Rules
1. Do not include the answer, explanations, confirmations, or any extra text.
2. If the answer indicates a list (e.g., numbered items like 1., 2. or comma-separated values), format the question so it clearly expects multiple items.
3. Preserve the original meaning and intent of the question.
4. Do not add new content or reinterpret the question.

Output
Return the formatted question text only, with no additional commentary.
        """
        future_to_prompt = {
            pool.submit(_task, id, f"{q.question}\n{q.answer}", sys_prompt): q.question
            for id, q in enumerate(questions)
        }

        for future in as_completed(future_to_prompt):
            id, answer = future.result()
            questions[id].question = answer

    return questions


def gen_questions(graph: Graph | None = None):
    graph = graph or _graph
    assert graph is not None

    nodes = graph.nodes.get_all()

    # definitions
    for node in nodes:
        # Prefer name over id for human-facing questions
        term = node.name.strip()
        definition = node.content.strip()

        if term and definition:
            _questions.append(
                Question(
                    question=f"What is {term}?",
                    answer=definition,
                )
            )

    # elaborations
    for node in nodes:
        for child in node.children.get_all():
            parent_term = node.name.strip()
            child_term = child.name.strip()
            child_content = child.content.strip()

            if parent_term and child_term and child_content:
                _questions.append(
                    Question(
                        question=f"In the context of {parent_term}, what is {child_term}?",
                        answer=child_content,
                    )
                )

    # links
    for node in nodes:
        origin = node.name.strip()

        for relation, dests in node.connections._conns.items():
            relation = relation.strip()

            for dest in dests:
                target = dest.name.strip()

                if origin and relation and target:
                    _questions.append(
                        Question(
                            question=f"What does {origin} {relation}?",
                            answer=target,
                        )
                    )


def export_questions(f_dir: str, questions: list[Question] | None = None):
    if not questions:
        questions = _questions

    with open(f_dir, "w") as f:
        f.write("")
    with open(f_dir, "a") as f:
        for q in questions:
            sep0 = chr(8)
            print(f"{q.question=}\n{q.answer}\n\n")
            f.write(f"{q.question}{sep0}{q.answer}{sep0}\n")


def health_check():
    # full_code = open("./extensions/flashcards/sample.cl").read()
    full_code = open("./extensions/flashcards/sample2.cl").read()
    (g := Graph()).parse(full_code)
    node_manager = g.nodes
    load(g)
    assert node_manager is not None
    global nodes
    nodes = node_manager.get_all()
    gen_questions()
    llm_question_formatting(temperature=0.2)
    for q in _questions:
        print(q.question)
        print(q.answer)
        print()
    export_questions("stuff.qlst")


if __name__ == "__main__":
    health_check()
