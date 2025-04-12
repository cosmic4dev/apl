from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os

os.environ["OPENAI_API_KEY"] = ""
llm_info = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
llm_reasoning = ChatOpenAI(model="gpt-4", temperature=0.5)
llm_creative = ChatOpenAI(model="gpt-4-1106-preview", temperature=0.9)

def info_search(state):
    msg = llm_info.invoke([
        SystemMessage(content="""
            너는 정보 수집 에이전트야.
            다음 글을 읽고 간단한 댓글을 달아줘. 
            글이 마음에 들면 'tools.py에 있는 increment_like()을 호출해줘.
        """),
        HumanMessage(content=state.get("input"))
    ]).content
    return {"info": msg}

def reasoning(state):
    msg = llm_reasoning.invoke([
        SystemMessage(content="""
                      너는 논리적 판단에 능한 전문가야.
                      다음 글을 읽고 간단한 댓글을 달아줘. 
            글이 마음에 들면 tools.py에 있는 increment_like()을 호출해줘."""),
        HumanMessage(content=state.get("input"))
    ]).content
    return {"reasoned": msg}

def creative(state):
    msg = llm_creative.invoke([
        SystemMessage(content="""
                      너는 창의적인 제안을 잘하는 전문가야.
                      다음 글을 읽고 간단한 댓글을 달아줘. 
            글이 마음에 들면 tools.py에 있는 increment_like()을 호출해줘."""),
        HumanMessage(content=state.get("input"))
    ]).content
    return {"creative": msg}


def selector_agent(state):
    question = state.get("input", "").lower()

    candidates = {
        "info": state.get("info", ""),
        "reasoned": state.get("reasoned", ""),
        "creative": state.get("creative", "")
    }

    def score(answer):
        # 입력과의 관련성 점수 + 텍스트 길이 보정
        relevance = sum(1 for word in question.split() if word in answer.lower())
        return relevance * 2 + min(len(answer), 300) / 100

    best_key = max(candidates, key=lambda k: score(candidates[k]))
    best_answer = candidates[best_key]

    return {
        "final_answer": best_answer,
        "selected_from": best_key,
        "info": candidates["info"],
        "reasoned": candidates["reasoned"],
        "creative": candidates["creative"]
    }
