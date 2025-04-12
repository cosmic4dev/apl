from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph
from typing import TypedDict
import os
from dotenv import load_dotenv
from typing import Optional
from pathlib import Path
from app.tools import write_post, write_comment, increment_like, connect_db
from app.agents import info_search, reasoning, creative, selector_agent
from app.tool_schemas import function_schemas

load_dotenv()

os.environ["OPENAI_API_KEY"] = ""
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
app = FastAPI()

class Question(BaseModel):
    question: str

# model variation
def get_llm_by_role(role: str):
    if role == "creative":
        return ChatOpenAI(model="gpt-4-1106-preview", temperature=0.9)
    elif role == "emotional":
        return ChatOpenAI(model="gpt-4-turbo", temperature=0.8)
    elif role == "factual":
        return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    else:
        return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)


# llm = ChatOpenAI(
#     model="gpt-3.5-turbo",
#     temperature=0)

class GraphState(TypedDict):
    input: str
    info: str
    reasoned: str
    final: str

# parallel style
class ParallelState(TypedDict, total=False):
    input: str
    info: str
    info_time: str
    reasoned: str
    reasoned_time: str
    creative: str
    creative_time: str
    final_answer: str
    final_time: str
    selected_from: str

def build_parallel_graph():
    workflow = StateGraph(ParallelState)

    workflow.add_node("info_node", info_search)
    workflow.add_node("reasoning_node", reasoning)
    workflow.add_node("creative_node", creative)
    workflow.add_node("selector", selector_agent)

    workflow.set_entry_point("info_node")

    workflow.add_edge("info_node", "reasoning_node")
    workflow.add_edge("info_node", "creative_node")
    workflow.add_edge("reasoning_node", "selector")
    workflow.add_edge("creative_node", "selector")

    workflow.set_finish_point("selector")

    return workflow.compile()


def build_blog_graph():
    class BlogState(TypedDict, total=False):
        question: str
        blog_post: str

    workflow = StateGraph(BlogState)
    workflow.add_node("blog_writer", blog_writer)
    workflow.set_entry_point("blog_writer")
    workflow.set_finish_point("blog_writer")
    return workflow.compile()


def blog_writer(state):
    topic = state.get("question") or "오늘의 기술 트렌드에 대해 써줘"
    style = state.get("style", "default")

    system_prompts = {
        "default": "당신은 Reddit에 짧고 임팩트 있는 메시지를 공유하는 유저입니다.",
        "controversial": "당신은 논쟁을 유발하는 테크 블로거입니다. 도발적이고 공격적인 관점으로 써주세요.",
        "emotional": "당신은 감성적인 블로그 작가입니다. 공감되고 감동적인 느낌으로 표현하세요.",
        "poetic": "당신은 시처럼 표현하는 작가입니다. 은유와 리듬을 담아 글을 써주세요.",
        "business": "당신은 전문가용 비즈니스 블로거입니다. 실용적이고 전문적인 문체로 써주세요.",
        "friendly": "당신은 친근한 말투의 블로거입니다. 편안하고 따뜻한 느낌으로 글을 써주세요."
    }

    prompt = system_prompts.get(style, system_prompts["default"])

    msg = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=topic)
    ]).content
    
    return {"blog_post": msg}

def blog_post_with_feedback(state: dict) -> dict:

    # 1. 메인 에이전트 글 작성
    topic = state.get("question", "오늘의 기술 트렌드에 대해 써줘")
    style = state.get("style", "default")

    llm_main = get_llm_by_role("writer")

    system_prompts = {
        "default": "당신은 Reddit에 짧고 임팩트 있는 메시지를 공유하는 유저입니다.",
        "business": "당신은 전문가용 비즈니스 블로거입니다. 실용적이고 전문적인 문체로 써주세요.",
        "emotional": "감성적인 관점에서 작성해 주세요.",
        # 기타 생략
    }

    main_post = llm_main.invoke([
        SystemMessage(content=system_prompts.get(style, system_prompts["default"])),
        HumanMessage(content=topic)
    ]).content

    # 2. 서브 에이전트 피드백 수집
    sub_agents = {
        "info": get_llm_by_role("info"),
        "reasoning": get_llm_by_role("reasoning"),
        "creative": get_llm_by_role("creative")
    }

    feedbacks = {}
    for agent_name, agent_llm in sub_agents.items():
        feedback = agent_llm.invoke([
            SystemMessage(content=f"너는 '{agent_name}' 역할의 서브 에이전트야. 메인 글에 대한 댓글을 작성해."),
            HumanMessage(content=main_post)
        ]).content
        feedbacks[f"{agent_name}_comment"] = feedback

    return {
        "blog_post": main_post,
        **feedbacks
    }
def info_commenter(state):
    llm = get_llm_by_role("info")
    comment = llm.invoke([
        SystemMessage(content="정보 수집 전문가로서 이 블로그 글에 댓글을 남겨주세요."),
        HumanMessage(content=state["blog_post"])
    ]).content
    return {"info_comment": comment}

def reasoning_commenter(state):
    llm = get_llm_by_role("reasoning")
    comment = llm.invoke([
        SystemMessage(content="논리적 전문가로서 이 블로그 글에 댓글을 남겨주세요."),
        HumanMessage(content=state["blog_post"])
    ]).content
    return {"reasoning_comment": comment}

def creative_commenter(state):
    llm = get_llm_by_role("creative")
    comment = llm.invoke([
        SystemMessage(content="창의적인 관점에서 이 블로그 글에 댓글을 남겨주세요."),
        HumanMessage(content=state["blog_post"])
    ]).content
    return {"creative_comment": comment}

def build_graph():
    workflow = StateGraph(ParallelState)

    workflow.add_node("start", lambda state: {})  # dummy start node
    workflow.add_node("info_node", info_search)
    workflow.add_node("reasoning_node", reasoning)
    workflow.add_node("creative_node", creative)
    workflow.add_node("selector", selector_agent)

    workflow.set_entry_point("start")

    # 병렬 실행
    workflow.add_edge("start", "info_node")
    workflow.add_edge("start", "reasoning_node")
    workflow.add_edge("start", "creative_node")

    # 최종 선택자에게 연결
    workflow.add_edge("info_node", "selector")
    workflow.add_edge("reasoning_node", "selector")
    workflow.add_edge("creative_node", "selector")

    workflow.set_finish_point("selector")

    return workflow.compile()


graph_executor = build_graph()


class RequestInput(BaseModel):
    mode: str  # "qa" or "blog_post"
    question: Optional[str] = None  # 없어도 괜찮게
    style: Optional[str] = "default"  # blog_post용 스타일

qa_executor = build_graph()
blog_executor = build_blog_graph()

parallel_executor = build_parallel_graph()


@app.post("/ask")
async def handle_request(input: RequestInput):
    if input.mode == "blog_post":
        result = blog_executor.invoke({
            "question": input.question,
            "style": input.style
        })
        return {
            "blog_post": result.get("blog_post"),
        }

    elif input.mode == "qa":
        result = parallel_executor.invoke({"input": input.question})
        return result

    return {"error": "Invalid mode."}


    