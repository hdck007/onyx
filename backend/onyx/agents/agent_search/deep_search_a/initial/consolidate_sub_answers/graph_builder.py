from langgraph.graph import END
from langgraph.graph import START
from langgraph.graph import StateGraph

from onyx.agents.agent_search.deep_search_a.initial.consolidate_sub_answers.edges import (
    parallelize_initial_sub_question_answering,
)
from onyx.agents.agent_search.deep_search_a.initial.consolidate_sub_answers.nodes.decompose_orig_question import (
    decompose_orig_question,
)
from onyx.agents.agent_search.deep_search_a.initial.consolidate_sub_answers.nodes.format_initial_sub_answers import (
    format_initial_sub_answers,
)
from onyx.agents.agent_search.deep_search_a.initial.consolidate_sub_answers.states import (
    SQInput,
)
from onyx.agents.agent_search.deep_search_a.initial.consolidate_sub_answers.states import (
    SQState,
)
from onyx.agents.agent_search.deep_search_a.initial.generate_individual_sub_answer.graph_builder import (
    answer_query_graph_builder,
)
from onyx.utils.logger import setup_logger

logger = setup_logger()

test_mode = False


def consolidate_sub_answers_graph_builder() -> StateGraph:
    graph = StateGraph(
        state_schema=SQState,
        input=SQInput,
    )

    graph.add_node(
        node="decompose_orig_question",
        action=decompose_orig_question,
    )
    answer_sub_question_subgraph = answer_query_graph_builder().compile()
    graph.add_node(
        node="answer_sub_question_subgraph",
        action=answer_sub_question_subgraph,
    )

    graph.add_node(
        node="format_initial_sub_question_answers",
        action=format_initial_sub_answers,
    )

    ### Add edges ###

    # raph.add_edge(start_key=START, end_key="base_raw_search_subgraph")

    # graph.add_edge(
    #     start_key="start_agent_search",
    #     end_key="extract_entity_term",
    # )

    graph.add_edge(
        start_key=START,
        end_key="decompose_orig_question",
    )

    # graph.add_edge(
    #     start_key="LLM",
    #     end_key=END,
    # )

    # graph.add_edge(
    #     start_key=START,
    #     end_key="initial_sub_question_creation",
    # )

    graph.add_conditional_edges(
        source="decompose_orig_question",
        path=parallelize_initial_sub_question_answering,
        path_map=["answer_sub_question_subgraph"],
    )
    graph.add_edge(
        start_key="answer_sub_question_subgraph",
        end_key="format_initial_sub_question_answers",
    )

    graph.add_edge(
        start_key="format_initial_sub_question_answers",
        end_key=END,
    )

    # graph.add_edge(
    #     start_key="generate_refined_answer",
    #     end_key="check_refined_answer",
    # )

    # graph.add_edge(
    #     start_key="check_refined_answer",
    #     end_key=END,
    # )

    return graph
