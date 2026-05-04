from __future__ import annotations

import asyncio
import json
from copy import deepcopy
from typing import Any, Sequence
from urllib import error as urllib_error
from urllib import request as urllib_request

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.utils.function_calling import convert_to_openai_tool

from app.config import settings


class SparkOpenAICompatModel:
    """Minimal LangChain-compatible chat wrapper for Spark OpenAI endpoint.

    Supports invoke/ainvoke (non-streaming) and bind_tools().
    """

    def __init__(
        self,
        *,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        endpoint: str = "/chat/completions",
        temperature: float | None = None,
        timeout: float = 30.0,
        extra_body: dict[str, Any] | None = None,
        bound_tools: list[dict[str, Any]] | None = None,
    ) -> None:
        self.model = model or settings.OPENAI_MODEL
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = (base_url or settings.OPENAI_BASE_URL or "https://spark-api-open.xf-yun.com/v1").rstrip("/")
        self.endpoint = endpoint
        self.temperature = temperature
        self.timeout = timeout
        self.extra_body = extra_body or {}
        self.bound_tools = bound_tools or []

    def bind_tools(self, tools: Sequence[Any]) -> "SparkOpenAICompatModel":
        openai_tools = [convert_to_openai_tool(tool) for tool in tools]
        return SparkOpenAICompatModel(
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            endpoint=self.endpoint,
            temperature=self.temperature,
            timeout=self.timeout,
            extra_body=deepcopy(self.extra_body),
            bound_tools=openai_tools,
        )

    def invoke(self, input: str | BaseMessage | Sequence[Any], **kwargs: Any) -> AIMessage:
        messages = self._normalize_messages(input)
        payload = self._build_payload(messages, **kwargs)
        response_json = self._post_json(payload)
        return self._to_ai_message(response_json)

    async def ainvoke(self, input: str | BaseMessage | Sequence[Any], **kwargs: Any) -> AIMessage:
        return await asyncio.to_thread(self.invoke, input, **kwargs)

    def _normalize_messages(self, input: str | BaseMessage | Sequence[Any]) -> list[BaseMessage]:
        if isinstance(input, str):
            return [HumanMessage(content=input)]
        if isinstance(input, BaseMessage):
            return [input]
        if not isinstance(input, Sequence):
            raise TypeError(f"Unsupported input type for invoke(): {type(input)}")

        normalized: list[BaseMessage] = []
        for item in input:
            if isinstance(item, BaseMessage):
                normalized.append(item)
                continue
            if isinstance(item, tuple) and len(item) == 2:
                role, content = item
                if role in ("human", "user"):
                    normalized.append(HumanMessage(content=str(content)))
                elif role in ("system",):
                    normalized.append(SystemMessage(content=str(content)))
                else:
                    normalized.append(AIMessage(content=str(content)))
                continue
            if isinstance(item, dict):
                role = item.get("role", "user")
                content = item.get("content", "")
                if role == "system":
                    normalized.append(SystemMessage(content=str(content)))
                elif role == "assistant":
                    normalized.append(AIMessage(content=str(content)))
                elif role == "tool":
                    normalized.append(
                        ToolMessage(
                            content=str(content),
                            tool_call_id=str(item.get("tool_call_id") or "tool_call"),
                        )
                    )
                else:
                    normalized.append(HumanMessage(content=str(content)))
                continue
            normalized.append(HumanMessage(content=str(item)))

        return normalized

    def _serialize_messages(self, messages: list[BaseMessage]) -> list[dict[str, Any]]:
        serialized: list[dict[str, Any]] = []
        for msg in messages:
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            if isinstance(msg, HumanMessage):
                serialized.append({"role": "user", "content": content})
            elif isinstance(msg, SystemMessage):
                serialized.append({"role": "system", "content": content})
            elif isinstance(msg, ToolMessage):
                serialized.append(
                    {
                        "role": "tool",
                        "content": content,
                        "tool_call_id": msg.tool_call_id,
                    }
                )
            else:
                entry: dict[str, Any] = {"role": "assistant", "content": content}
                if isinstance(msg, AIMessage) and msg.tool_calls:
                    entry["tool_calls"] = [
                        {
                            "id": tc.get("id"),
                            "type": "function",
                            "function": {
                                "name": tc.get("name"),
                                "arguments": json.dumps(tc.get("args", {}), ensure_ascii=False),
                            },
                        }
                        for tc in msg.tool_calls
                    ]
                serialized.append(entry)
        return serialized

    def _build_payload(self, messages: list[BaseMessage], **kwargs: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": self._serialize_messages(messages),
            "stream": False,
        }
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if self.bound_tools:
            payload["tools"] = self.bound_tools

        payload.update(self.extra_body)
        payload.update(kwargs)
        return payload

    def _build_auth_header(self) -> str:
        return f"Bearer {self.api_key}"

    def _post_json(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}{self.endpoint}"
        request_body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib_request.Request(
            url=url,
            data=request_body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": self._build_auth_header(),
            },
        )
        try:
            with urllib_request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
        except urllib_error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Spark API HTTP {e.code}: {error_body}") from e
        except urllib_error.URLError as e:
            raise RuntimeError(f"Spark API network error: {e}") from e

        try:
            data = json.loads(body)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Spark API returned non-JSON response: {body[:200]}") from e

        code = data.get("code", 0)
        if code != 0:
            raise RuntimeError(
                f"Spark API error code={code}, message={data.get('message', 'Unknown error')}, body={data}"
            )
        return data

    def _to_ai_message(self, response_json: dict[str, Any]) -> AIMessage:
        choices = response_json.get("choices") or []
        message: dict[str, Any] = choices[0].get("message", {}) if choices else {}

        content = message.get("content", "")
        raw_tool_calls = message.get("tool_calls") or []

        tool_calls: list[dict[str, Any]] = []
        for tc in raw_tool_calls:
            function_data = tc.get("function", {})
            args_raw = function_data.get("arguments", "{}")
            try:
                parsed_args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
            except json.JSONDecodeError:
                parsed_args = {"raw": args_raw}

            tool_calls.append(
                {
                    "name": function_data.get("name", "tool"),
                    "args": parsed_args or {},
                    "id": tc.get("id") or "tool_call",
                }
            )

        return AIMessage(
            content=content,
            tool_calls=tool_calls,
            response_metadata={"raw": response_json},
        )


# User-requested import name for quick verification command.
YourNewModel = SparkOpenAICompatModel


def create_chat_model(*, temperature: float | None = None) -> SparkOpenAICompatModel:
    return SparkOpenAICompatModel(temperature=temperature)
