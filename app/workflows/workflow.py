import os

from typing import TypedDict, Annotated ,Literal 
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from app.agents.content_generator_agent import ContentGeneratorAgent
from app.agents.flashcard_agent import FlashcardAgent
from app.agents.notes_agent import NoteAgent
from app.agents.quiz_agent import QuizAgent
from app.agents.summary_agent import SummaryAgent
from langchain_core.messages import HumanMessage

class AgentState(TypedDict):
    message : Annotated[list,add_messages]
    task:str
    output:str

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

   if task == "content":
    return "content_generator"

   elif task == "notes":
    return "notes"

   elif task in ["flashcard", "flashcards"]:
    return "flashcard"

   elif task in ["quiz", "quizzes","mcq"]:
    return "quiz"

   elif task == "summary":
    return "summary" 

   else:
    raise ValueError(f"Unknown task: {task}")

def route_content_generator(state:AgentState) -> Literal["content_generator_tools","__end__"]:
  message = state['message']
  last_message = message[-1]

  if hasattr(last_message,"tool_calls") and last_message.tool_calls:
    return"content_generator_tools"

  state["output"] = last_message.content
  return "__end__"    

def route_notes(state: AgentState) -> Literal["notes_tools", "__end__"]:
    message = state["message"]
    last_message = message[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "notes_tools"

    state["output"] = last_message.content
    return "__end__"

def route_flashcards(state:AgentState) -> Literal["flashcard_tools","__end__"]:
  message = state['message']
  last_message = message[-1]

  if hasattr(last_message,"tool_calls") and last_message.tool_calls:
    return"flashcard_tools"
  state["output"] = last_message.content
  return "__end__"

def route_quiz(state:AgentState) -> Literal["quiz_tools","__end__"]:
  message = state['message']
  last_message = message[-1]

  if hasattr(last_message,"tool_calls") and last_message.tool_calls:
    return"quiz_tools"
  state["output"] = last_message.content
  return"__end__"

def route_summary(state:AgentState) -> Literal["summary_tools","__end__"]:
  message = state["message"]
  last_message = message[-1]

  if hasattr(last_message,"tool_calls") and last_message.tool_calls:
    return "summary_tools"
  state["output"] = last_message.content
  return "__end__"

content_generator_agent = ContentGeneratorAgent()
notes_agent = NoteAgent()
flashcard_agent = FlashcardAgent()
quiz_agent = QuizAgent()
summary_agent = SummaryAgent()

workflow_builder = StateGraph(AgentState) 

workflow_builder.add_node("content_generator",content_generator_agent.node)
workflow_builder.add_node("content_generator_tools",content_generator_agent.tools_node)
workflow_builder.add_node("notes",notes_agent.node)
workflow_builder.add_node("notes_tools",notes_agent.tools_node)                
workflow_builder.add_node("flashcard",flashcard_agent.node)
workflow_builder.add_node("flashcard_tools",flashcard_agent.tools_node)
workflow_builder.add_node("quiz",quiz_agent.node)
workflow_builder.add_node("quiz_tools",quiz_agent.tools_node)
workflow_builder.add_node("summary",summary_agent.node)
workflow_builder.add_node("summary_tools",summary_agent.tools_node)

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
        "__end__": END
    }
)

workflow_builder.add_edge("content_generator_tools","content_generator")

workflow_builder.add_conditional_edges(
    "notes",
    route_notes,
    {
        "notes_tools": "notes_tools",
        "__end__": END
    }
)

workflow_builder.add_edge("notes_tools","notes")

workflow_builder.add_conditional_edges(
    "flashcard",
    route_flashcards,
    {
        "flashcard_tools": "flashcard_tools",
        "__end__": END
    }
)
workflow_builder.add_edge("flashcard_tools","flashcard")

workflow_builder.add_conditional_edges(
    "quiz",
    route_quiz,
    {
        "quiz_tools": "quiz_tools",
        "__end__": END
    }
)

workflow_builder.add_edge("quiz_tools","quiz")

workflow_builder.add_conditional_edges(
    "summary",
    route_summary,
    {
        "summary_tools":"summary_tools",
        "__end__":END
    }
)

workflow_builder.add_edge("summary_tools","summary")
workflow = workflow_builder.compile()

if __name__ == "__main__":

    query = input("Enter your query: ")
    task = input("Enter the task: ")

    user_input = {
        "message": [HumanMessage(content=query)],
        "task": task,
        "output": "",
    }

    output = workflow.invoke(user_input)

    print(output["message"][-1].content)