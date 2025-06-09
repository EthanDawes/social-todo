from typing import TypedDict, Optional, Literal

class TaskItem(TypedDict):
    notes: Optional[str]
    due: Optional[str]
    kind: str
    created: str
    id: str
    extra_notification_device_id: Optional[str]
    title: str
    task_type: str
    updated: str
    selfLink: str
    status: str
    completed: Optional[str]
    parent: Optional[str]


class TaskGroup(TypedDict):
    kind: str
    id: str
    title: str
    updated: str
    items: list[TaskItem]
    selfLink: str


class TaskList(TypedDict):
    kind: str
    items: list[TaskGroup]


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