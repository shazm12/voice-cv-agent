from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from dotenv import load_dotenv
from tools.github_tools import GITHUB_TOOLS

load_dotenv()

_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    max_retries=2
)

_llm_with_tools = _llm.bind_tools(GITHUB_TOOLS)
_tool_map = {t.name: t for t in GITHUB_TOOLS}

_SYSTEM_PROMPT = """
You are a helpful Talent assistant who answers questions about the candidate's profile.
You have access to GitHub tools — use them when the caller asks about GitHub projects,
repositories, or profile. For resume questions, use the resume text provided.

Resume:
{resume_text}

Always keep your final answer to 2-3 sentences — this is a voice call.
"""


def answer(question: str, resume_text: str) -> str:

    messages = [
        SystemMessage(content=_SYSTEM_PROMPT.format(resume_text=resume_text)),
        HumanMessage(content=question)
    ]
    
    for _ in range(4):
        ai_msg = _llm_with_tools.invoke(messages)
        messages.append(ai_msg)
        if not ai_msg.tool_calls:
            break

        for tc in ai_msg.tool_calls:
            result = _tool_map[tc["name"]].invoke(tc["args"])
            messages.append(ToolMessage(
                content=str(result), tool_call_id=tc["id"]))

    return ai_msg.content
