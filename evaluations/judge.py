import os
from typing import List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


class CriterionScore(BaseModel):
    criterion: str = Field(..., description="The criterion being evaluated")
    passed: bool = Field(..., description="Whether the response satisfies this criterion")
    reasoning: str = Field(..., description="One-sentence explanation of the verdict")


class JudgeResponse(BaseModel):
    scores: List[CriterionScore]


_llm = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
)
_judge = _llm.with_structured_output(JudgeResponse)


def evaluate(question: str, response: str, criteria: list[str]) -> JudgeResponse:
    criteria_block = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(criteria))
    return _judge.invoke(
        f"""You are an impartial evaluator assessing whether an AI assistant's response meets a set of quality criteria.

[USER QUESTION]
{question}

[ASSISTANT RESPONSE]
{response}

[CRITERIA TO EVALUATE]
{criteria_block}

Evaluate each criterion independently. Be strict but fair.
Return one score entry per criterion, in the same order as listed above."""
    )
