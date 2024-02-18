# Reference:
from typing import List, Tuple, Any, Union
from langchain.schema import AgentAction, AgentFinish
from langchain.agents import BaseSingleActionAgent
from langchain.base_language import BaseLanguageModel

class IntentAgent(BaseSingleActionAgent):
    llm: BaseLanguageModel
    trigger: str

    def choose_tools(self, query) -> List[str]:
        if self.trigger in query:
            return "generate image"
        else:
            return "language model"

    @property
    def input_keys(self):
        return ["input"]

    def plan(
            self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any
    ) -> Union[AgentAction, AgentFinish]:
        # only for single tool
        tool_name = self.choose_tools(kwargs["input"])
        return AgentAction(tool=tool_name, tool_input=kwargs["input"], log="")


    async def aplan(
            self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any
    ) -> Union[List[AgentAction], AgentFinish]:
        raise NotImplementedError("IntentAgent does not support async")