from datetime import datetime

from onyx.agents.agent_search.deep_search.initial.generate_initial_answer.states import (
    SubQuestionRetrievalState,
)
from onyx.agents.agent_search.deep_search.main.states import LoggerUpdate


def consolidate_retrieved_documents(
    state: SubQuestionRetrievalState,
) -> LoggerUpdate:
    node_start_time = datetime.now()

    return LoggerUpdate(log_messages=[f"{node_start_time} -- Retrieval consolidation"])
