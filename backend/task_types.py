from typing import TypedDict, Optional, Literal, Any


class TaskItem(TypedDict):
    kind: str
    id: str
    etag: str
    title: str
    updated: str
    selfLink: str
    position: str
    notes: Optional[str]
    status: str
    due: Optional[str]
    completed: Optional[str]
    links: list[Any]
    webViewLink: str
    parent: Optional[str]


# Map category name to tasks
TaskList = dict[str, list[TaskItem]]


class RequestMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class RequestBody(TypedDict):
    model: str
    messages: list[RequestMessage]


class RequestInput(TypedDict):
    custom_id: str
    method: Literal["POST", "GET", "PUT", "DELETE"]
    url: str
    body: RequestBody


class BatchMetadata(TypedDict):
    platform: str
    model: str
    prompt: str
