from typing import Annotated

from fastapi import Depends, Request

from app.agent import SQLAgent


def get_agent(request: Request) -> SQLAgent:
    return request.app.state.agent


AgentDep = Annotated[SQLAgent, Depends(get_agent)]
