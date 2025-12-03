
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage, AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

load_dotenv()

# Global variable
document_content = ""

# --- State ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# --- Tools ---
@tool
def update(content: str) -> str:
    """Updates the document with the provided content."""
    global document_content
    document_content = content
    return f"Document has been successfully updated!\n\nCurrent content:\n{document_content}"

@tool
def save(filename: str) -> str:
    """Save the current document to a text file and finish the process.

    Args:
        filename: Name for the text file
    """
    global document_content
    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(document_content)
        print(f"\nDocument has been saved to: {filename}.")
        return f"Document has been saved successfully to '{filename}'."
    except Exception as e:
        return f"Error saving document: {str(e)}"
    


tools = [update, save]


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash").bind_tools(tools)

# --- Agent node ---
def our_agent(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=(
        "You are Drafter, a helpful writing assistant. You help the user update and modify documents.\n\n"
        "- If the user wants to update or modify content, use the 'update' tool with the complete updated content.\n"
        "- If the user wants to save and finish, use the 'save' tool.\n"
        "- Always show the current document state after modifications.\n\n"
        f"Current document content:\n{document_content}"
    ))

    
    messages = list(state.get("messages", []))

    
    if not messages:
        user_message = HumanMessage(content="I'm ready to help you update a document. What would you like to create or change?")
    else:
        user_input = input("\nWhat would you like to do with the document? (e.g., Update: <content> | Save: <filename>)\n> ")
        print(f"\nUSER: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + messages + [user_message]

    # Invoke the LLM that is aware of tools
    response: AIMessage = llm.invoke(all_messages)

    print(f"\nAI: {response.content}")
    if getattr(response, "tool_calls", None):
        print(f"USING TOOLS: {[tc['name'] for tc in response.tool_calls]}")

    return {"messages": messages + [user_message, response]}


def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end the conversation."""
    messages = state.get("messages", [])
    if not messages:
        return "continue"

 
    for message in reversed(messages):
        if isinstance(message, ToolMessage):
            if getattr(message, "name", "") == "save":
                return "end"
            if ("saved" in message.content.lower()
                and "document" in message.content.lower()):
                return "end"
    return "continue"

def print_message(messages):
    """Pretty print only recent tool results."""
    if not messages:
        return
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"\nTOOL RESULT: {message.content}")

# --- Graph wiring ---
graph = StateGraph(AgentState)
graph.add_node("agent", our_agent)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_edge("agent", "tools")
graph.add_conditional_edges(
    "tools",
    should_continue,
    {"continue": "agent", "end": END},
)

app = graph.compile()

def run_document_agent():
    print("\n==== DRAFTER ====")
    state: AgentState = {"messages": []}

    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_message(step["messages"])

    print("\n==== DRAFTER FINISHED ====")

if __name__ == "__main__":
    run_document_agent()
