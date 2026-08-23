from typing import TypedDict, Annotated, Literal

from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.content_generator_agent import ContentGeneratorAgent
from app.agents.flashcard_agent import FlashcardAgent
from app.agents.notes_agent import NotesAgent
from app.agents.quiz_agent import QuizAgent
from app.agents.summary_agent import SummaryAgent


# ============================================================
# PADHAI AGENT WORKFLOW
# ============================================================


# ------------------------------------------------------------
# 1. WORKFLOW STATE
# ------------------------------------------------------------

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    task: str
    query: str
    output: str


# ------------------------------------------------------------
# 2. TASK ROUTER
# ------------------------------------------------------------

def task_router(
    state: AgentState,
) -> Literal[
    "content_generator",
    "notes",
    "flashcard",
    "quiz",
    "summary",
]:

    task = state["task"].lower().strip()

    if task in ["content", "content_generator"]:
        return "content_generator"

    elif task in ["notes", "note"]:
        return "notes"

    elif task in ["flashcard", "flashcards"]:
        return "flashcard"

    elif task in ["quiz", "quizzes", "mcq", "mcqs"]:
        return "quiz"

    elif task in ["summary", "summarize"]:
        return "summary"

    else:
        raise ValueError(
            f"Unknown task: {task}. "
            f"Use content, notes, flashcards, quiz, or summary."
        )


# ------------------------------------------------------------
# 3. CONTENT GENERATOR ROUTER
# ------------------------------------------------------------

def route_content_generator(
    state: AgentState,
) -> Literal["content_generator_tools", "__end__"]:

    messages = state["messages"]

    if not messages:
        raise ValueError("No messages found in workflow state.")

    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "content_generator_tools"

    state["output"] = last_message.content

    return "__end__"


# ------------------------------------------------------------
# 4. NOTES ROUTER
# ------------------------------------------------------------

def route_notes(
    state: AgentState,
) -> Literal["notes_tools", "__end__"]:

    messages = state["messages"]

    if not messages:
        raise ValueError("No messages found in workflow state.")

    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "notes_tools"

    state["output"] = last_message.content

    return "__end__"


# ------------------------------------------------------------
# 5. FLASHCARD ROUTER
# ------------------------------------------------------------

def route_flashcards(
    state: AgentState,
) -> Literal["flashcard_tools", "__end__"]:

    messages = state["messages"]

    if not messages:
        raise ValueError("No messages found in workflow state.")

    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "flashcard_tools"

    state["output"] = last_message.content

    return "__end__"


# ------------------------------------------------------------
# 6. QUIZ ROUTER
#
# IMPORTANT:
# Quiz is different from the other agents.
#
# Flow:
#
# quiz
#   ↓
# quiz_tools
#   ↓
# quiz_final
#   ↓
# END
#
# We DO NOT send quiz_tools back to quiz.
# ------------------------------------------------------------

def route_quiz(
    state: AgentState,
) -> Literal["quiz_tools", "__end__"]:

    messages = state["messages"]

    if not messages:
        raise ValueError("No messages found in workflow state.")

    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "quiz_tools"

    # Normally the quiz agent should request the tool.
    # If it doesn't, stop safely.
    state["output"] = last_message.content

    return "__end__"


# ------------------------------------------------------------
# 7. SUMMARY ROUTER
# ------------------------------------------------------------

def route_summary(
    state: AgentState,
) -> Literal["summary_tools", "__end__"]:

    messages = state["messages"]

    if not messages:
        raise ValueError("No messages found in workflow state.")

    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "summary_tools"

    state["output"] = last_message.content

    return "__end__"


# ============================================================
# 8. QUIZ FINAL GENERATION NODE
# ============================================================

def generate_quiz_final(state: AgentState) -> dict:
    """
    Generate the final quiz using the educational content
    retrieved by the QuizAgent.

    This is intentionally separate from quiz.agent_node()
    because QuizAgent has a dedicated generate_final_quiz()
    method.
    """

    messages = state["messages"]

    if not messages:
        raise ValueError(
            "No messages available for final quiz generation."
        )

    # --------------------------------------------------------
    # The quiz tool places the retrieved educational content
    # into the conversation.
    #
    # Find the most recent message containing the retrieved
    # educational material.
    # --------------------------------------------------------

    retrieved_content = None

    for message in reversed(messages):

        content = getattr(message, "content", "")

        if content and isinstance(content, str):

            # Avoid accidentally using the original question
            # as the retrieved context.
            if content.strip() != state["query"].strip():

                retrieved_content = content
                break

    if not retrieved_content:
        raise ValueError(
            "No educational material was retrieved for quiz generation."
        )

    # --------------------------------------------------------
    # Create QuizAgent
    # --------------------------------------------------------

    quiz_agent = QuizAgent()

    # --------------------------------------------------------
    # Generate FINAL MCQ quiz
    # --------------------------------------------------------

    final_quiz = quiz_agent.generate_final_quiz(
        topic=state["query"],
        retrieved_content=retrieved_content,
        number_of_questions=10,
    )

    # --------------------------------------------------------
    # Return proper LangGraph state update
    # --------------------------------------------------------

    return {
        "messages": [
            AIMessage(content=final_quiz)
        ],
        "output": final_quiz,
    }


# ============================================================
# 9. CREATE AGENTS
# ============================================================

content_generator_agent = ContentGeneratorAgent()
notes_agent = NotesAgent()
flashcard_agent = FlashcardAgent()
quiz_agent = QuizAgent()
summary_agent = SummaryAgent()


# ============================================================
# 10. CREATE WORKFLOW BUILDER
# ============================================================

workflow_builder = StateGraph(AgentState)


# ============================================================
# 11. ADD AGENT NODES
# ============================================================

workflow_builder.add_node(
    "content_generator",
    content_generator_agent.agent_node,
)

workflow_builder.add_node(
    "content_generator_tools",
    content_generator_agent.tool_node,
)


workflow_builder.add_node(
    "notes",
    notes_agent.agent_node,
)

workflow_builder.add_node(
    "notes_tools",
    notes_agent.tool_node,
)


workflow_builder.add_node(
    "flashcard",
    flashcard_agent.agent_node,
)

workflow_builder.add_node(
    "flashcard_tools",
    flashcard_agent.tool_node,
)


workflow_builder.add_node(
    "quiz",
    quiz_agent.agent_node,
)

workflow_builder.add_node(
    "quiz_tools",
    quiz_agent.tool_node,
)

# IMPORTANT:
# Dedicated final quiz generation node
workflow_builder.add_node(
    "quiz_final",
    generate_quiz_final,
)


workflow_builder.add_node(
    "summary",
    summary_agent.agent_node,
)

workflow_builder.add_node(
    "summary_tools",
    summary_agent.tool_node,
)


# ============================================================
# 12. START → TASK ROUTER
# ============================================================

workflow_builder.add_conditional_edges(
    START,
    task_router,
    {
        "content_generator": "content_generator",
        "notes": "notes",
        "flashcard": "flashcard",
        "quiz": "quiz",
        "summary": "summary",
    },
)


# ============================================================
# 13. CONTENT GENERATOR ROUTING
# ============================================================

workflow_builder.add_conditional_edges(
    "content_generator",
    route_content_generator,
    {
        "content_generator_tools": "content_generator_tools",
        "__end__": END,
    },
)

workflow_builder.add_edge(
    "content_generator_tools",
    "content_generator",
)


# ============================================================
# 14. NOTES ROUTING
# ============================================================

workflow_builder.add_conditional_edges(
    "notes",
    route_notes,
    {
        "notes_tools": "notes_tools",
        "__end__": END,
    },
)

workflow_builder.add_edge(
    "notes_tools",
    "notes",
)


# ============================================================
# 15. FLASHCARD ROUTING
# ============================================================

workflow_builder.add_conditional_edges(
    "flashcard",
    route_flashcards,
    {
        "flashcard_tools": "flashcard_tools",
        "__end__": END,
    },
)

workflow_builder.add_edge(
    "flashcard_tools",
    "flashcard",
)


# ============================================================
# 16. QUIZ ROUTING
# ============================================================

workflow_builder.add_conditional_edges(
    "quiz",
    route_quiz,
    {
        "quiz_tools": "quiz_tools",
        "__end__": END,
    },
)

# IMPORTANT:
# DO NOT connect quiz_tools → quiz.
#
# Instead:
#
# quiz_tools → quiz_final → END

workflow_builder.add_edge(
    "quiz_tools",
    "quiz_final",
)

workflow_builder.add_edge(
    "quiz_final",
    END,
)


# ============================================================
# 17. SUMMARY ROUTING
# ============================================================

workflow_builder.add_conditional_edges(
    "summary",
    route_summary,
    {
        "summary_tools": "summary_tools",
        "__end__": END,
    },
)

workflow_builder.add_edge(
    "summary_tools",
    "summary",
)


# ============================================================
# 18. COMPILE WORKFLOW
# ============================================================

workflow = workflow_builder.compile()


# ============================================================
# 19. TEST WORKFLOW
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("              PADHAI AGENT WORKFLOW")
    print("=" * 60)

    try:

        # ----------------------------------------------------
        # USER QUERY
        # ----------------------------------------------------

        query = input(
            "\nEnter your query: "
        ).strip()

        # ----------------------------------------------------
        # TASK
        # ----------------------------------------------------

        task = input(
            "Enter task "
            "(content / notes / flashcards / quiz / summary): "
        ).strip()

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        if not task:
            raise ValueError(
                "Task cannot be empty."
            )

        # ----------------------------------------------------
        # INITIAL STATE
        # ----------------------------------------------------

        user_input: AgentState = {
            "messages": [
                HumanMessage(
                    content=query
                )
            ],
            "task": task,
            "query": query,
            "output": "",
        }

        # ----------------------------------------------------
        # RUN WORKFLOW
        # ----------------------------------------------------

        print("\n" + "=" * 60)
        print("                 RUNNING WORKFLOW")
        print("=" * 60)

        result = workflow.invoke(
            user_input
        )

        # ----------------------------------------------------
        # FINAL OUTPUT
        # ----------------------------------------------------

        print("\n" + "=" * 60)
        print("                 FINAL OUTPUT")
        print("=" * 60)

        if result.get("output"):

            print(
                result["output"]
            )

        elif result.get("messages"):

            final_message = result["messages"][-1]

            if hasattr(
                final_message,
                "content"
            ):

                print(
                    final_message.content
                )

            else:

                print(
                    final_message
                )

        else:

            print(
                "Workflow completed but "
                "produced no output."
            )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        print("\n" + "=" * 60)
        print("          WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:

        print("\n" + "=" * 60)
        print("                 WORKFLOW ERROR")
        print("=" * 60)

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        print(
            "\nPlease check the agent, RAG, "
            "LLM, and tool configuration."
        )