from typing import TypedDict, Annotated, Literal

from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.content_generator_agent import ContentGeneratorAgent
from app.agents.flashcard_agent import FlashcardAgent
from app.agents.notes_agent import NotesAgent
from app.agents.quiz_agent import QuizAgent
from app.agents.summary_agent import SummaryAgent


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    task: str
    query: str
    output: str
    material_id: str | None


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


    quiz_agent = QuizAgent()

    final_quiz = quiz_agent.generate_final_quiz(
        topic=state["query"],
        retrieved_content=retrieved_content,
        number_of_questions=10,
    )


    return {
        "messages": [
            AIMessage(content=final_quiz)
        ],
        "output": final_quiz,
    }



content_generator_agent = ContentGeneratorAgent()
notes_agent = NotesAgent()
flashcard_agent = FlashcardAgent()
quiz_agent = QuizAgent()
summary_agent = SummaryAgent()



workflow_builder = StateGraph(AgentState)


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


workflow = workflow_builder.compile()


if __name__ == "__main__":

    print("=" * 60)
    print("              PADHAI AGENT WORKFLOW")
    print("=" * 60)

    try:


        query = input(
            "\nEnter your query: "
        ).strip()


        task = input(
            "Enter task "
            "(content / notes / flashcards / quiz / summary): "
        ).strip()


        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        if not task:
            raise ValueError(
                "Task cannot be empty."
            )

        user_input: AgentState = {
            "messages": [
                HumanMessage(
                    content=query
                )
            ],
            "task": task,
            "query": query,
            "output": "",
            "material_id": None,
        }

        print("\n" + "=" * 60)
        print("                 RUNNING WORKFLOW")
        print("=" * 60)

        result = workflow.invoke(
            user_input
        )
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