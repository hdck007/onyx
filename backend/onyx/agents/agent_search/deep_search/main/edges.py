from collections.abc import Hashable
from datetime import datetime
from typing import cast
from typing import Literal

from langchain_core.runnables import RunnableConfig
from langgraph.types import Send

from onyx.agents.agent_search.deep_search.initial.generate_individual_sub_answer.states import (
    AnswerQuestionOutput,
)
from onyx.agents.agent_search.deep_search.initial.generate_individual_sub_answer.states import (
    SubQuestionAnsweringInput,
)
from onyx.agents.agent_search.deep_search.main.states import MainState
from onyx.agents.agent_search.deep_search.main.states import (
    RequireRefinemenEvalUpdate,
)
from onyx.agents.agent_search.models import GraphConfig
from onyx.agents.agent_search.shared_graph_utils.utils import make_question_id
from onyx.utils.logger import setup_logger

logger = setup_logger()


def route_initial_tool_choice(
    state: MainState, config: RunnableConfig
) -> Literal["tool_call", "start_agent_search", "logging_node"]:
    agent_config = cast(GraphConfig, config["metadata"]["config"])
    if state.tool_choice is not None:
        if (
            agent_config.behavior.use_agentic_search
            and agent_config.tooling.search_tool is not None
            and state.tool_choice.tool.name == agent_config.tooling.search_tool.name
        ):
            return "start_agent_search"
        else:
            return "tool_call"
    else:
        return "logging_node"


def parallelize_initial_sub_question_answering(
    state: MainState,
) -> list[Send | Hashable]:
    edge_start_time = datetime.now()
    if len(state.initial_sub_questions) > 0:
        # sub_question_record_ids = [subq_record.id for subq_record in state["sub_question_records"]]
        # if len(state["sub_question_records"]) == 0:
        #     if state["config"].use_persistence:
        #         raise ValueError("No sub-questions found for initial decompozed questions")
        #     else:
        #         # in this case, we are doing retrieval on the original question.
        #         # to make all the logic consistent, we create a new sub-question
        #         # with the same content as the original question
        #         sub_question_record_ids = [1] * len(state["initial_decomp_questions"])

        return [
            Send(
                "answer_query_subgraph",
                SubQuestionAnsweringInput(
                    question=question,
                    question_id=make_question_id(0, question_num + 1),
                    log_messages=[
                        f"{edge_start_time} -- Main Edge - Parallelize Initial Sub-question Answering"
                    ],
                ),
            )
            for question_num, question in enumerate(state.initial_sub_questions)
        ]

    else:
        return [
            Send(
                "ingest_answers",
                AnswerQuestionOutput(
                    answer_results=[],
                ),
            )
        ]


# Define the function that determines whether to continue or not
def continue_to_refined_answer_or_end(
    state: RequireRefinemenEvalUpdate,
) -> Literal["create_refined_sub_questions", "logging_node"]:
    if state.require_refined_answer_eval:
        return "create_refined_sub_questions"
    else:
        return "logging_node"


def parallelize_refined_sub_question_answering(
    state: MainState,
) -> list[Send | Hashable]:
    edge_start_time = datetime.now()
    if len(state.refined_sub_questions) > 0:
        return [
            Send(
                "answer_refined_question_subgraphs",
                SubQuestionAnsweringInput(
                    question=question_data.sub_question,
                    question_id=make_question_id(1, question_num),
                    log_messages=[
                        f"{edge_start_time} -- Main Edge - Parallelize Refined Sub-question Answering"
                    ],
                ),
            )
            for question_num, question_data in state.refined_sub_questions.items()
        ]

    else:
        return [
            Send(
                "ingest_refined_sub_answers",
                AnswerQuestionOutput(
                    answer_results=[],
                ),
            )
        ]
