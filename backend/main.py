from typing import Mapping, TypedDict, Optional, Any, Sequence, Literal, Iterable
from itertools import islice
import json
from datetime import datetime
from openai import OpenAI, NotGiven
import os
import io
from dotenv import load_dotenv

from openai.types import *


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


class ExtendedTaskItem(TaskItem):
    """Added after processing"""
    groupName: str
    processedDate: Optional[str]
    overview: str


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

def merge_lists[T: Mapping](base: list[T], new: list[T], on="id"):
    combined: dict[Any, T] = {}
    for item in base + new:
        combined[item[on]] = item
    return list(combined.values())


class TaskManager:
    def __init__(self):
        self._flat_tasks: list[ExtendedTaskItem] = []
        self.load_file()

    def load_file(self):
        tasks, flat_tasks = self._load_tasks()
        new_flat_tasks = self._sort_tasks(self._flatten_tasks(tasks))
        self._flat_tasks = merge_lists(new_flat_tasks, flat_tasks)

    @staticmethod
    def _load_tasks():
        with open("Tasks.json", "r", encoding="utf-8") as file:
            tasks: TaskList = json.load(file)
        try:
            with open("tasks_flat.json", "r", encoding="utf-8") as file:
                flat_tasks: list[ExtendedTaskItem] = json.load(file)
        except FileNotFoundError:
            flat_tasks = []
        return tasks, flat_tasks

    @staticmethod
    def _flatten_tasks(tasks: TaskList) -> list[ExtendedTaskItem]:
        return [
            {**item, "groupName": group["title"], "processedDate": None,
             "overview": f"{group["title"]}: {item["title"]} {(item.get('notes', '')).strip()}"}
            for group in tasks["items"]
            for item in group["items"]
        ]

    @staticmethod
    def _sort_tasks[T: TaskItem](tasks: list[T]):
        return sorted(
            tasks,
            key=lambda x: x.get("due") or x["created"]
        )

    def next(self, n: int):
        return list(islice(self._filter_used(self._flat_tasks), n))

    @staticmethod
    def _filter_used(tasks: Sequence[ExtendedTaskItem]):
        return filter(lambda x: x["status"] == "needsAction" and x["processedDate"] is None, tasks)

    def find_task(self, id: str) -> ExtendedTaskItem:
        return next(filter(lambda task: task["id"] == id, self._flat_tasks))

    def mark_save(self, tasks_ids: Iterable[str]):
        for task_id in tasks_ids:
            task = self.find_task(task_id)
            task["processedDate"] = datetime.now().isoformat()
        with open("tasks_flat.json", "w", encoding="utf-8") as file:
            json.dump(self._flat_tasks, file)

    @property
    def all_tasks(self):
        return "\n".join(task["overview"] for task in self._flat_tasks)


class AIFacade:
    def __init__(self) -> None:
        self.client = OpenAI()
        self.BATCH_PATH = "batch.json"

        try:
            with open(self.BATCH_PATH, "r") as file:
                self.__batch_metadata: Optional[Batch] = Batch.model_validate_json(file.read())
        except FileNotFoundError:
            self.__batch_metadata = None

    def _upload_batch(self, prompts: list[RequestInput]):
        print("Uploading batch...")
        batch_input_file = self.client.files.create(
            file=io.BytesIO(b"\n".join(bytes(json.dumps(prompt), "utf-8") for prompt in prompts)),
            purpose="batch",
        )
        return batch_input_file.id

    def submit_batch(self, prompts: list[RequestInput], *, metadata: Optional[BatchMetadata] = None):
        assert not self.batch_ongoing(), "Batch already submitted"
        file_id = self._upload_batch(prompts)
        self._batch_metadata = self.client.batches.create(
            input_file_id=file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata=metadata,
        )
        print("Submitted!")

    @property
    def _batch_metadata(self):
        return self.__batch_metadata

    @_batch_metadata.setter
    def _batch_metadata(self, val: Batch):
        self.__batch_metadata = val
        with open(self.BATCH_PATH, "w") as file:
            file.write(val.to_json())

    def batch_ongoing(self):
        # Impossible to annotate as type guard
        return self._batch_metadata is not None

    def fetch_batch(self):
        assert self.batch_ongoing(), "No batch submitted"
        self._batch_metadata = self.client.batches.retrieve(self._batch_metadata.id)
        status = self._batch_metadata.status
        response: Optional[str] = None
        match status:
            case "validating" | "in_progress" | "finalizing":
                return status, None
            case "completed":
                file_response = self.client.files.content(self._batch_metadata.output_file_id)
                return status, file_response.text #TODO: delete
        os.remove(self.BATCH_PATH)  # This technically leads to invalid state
        return status, response

    @property
    def metadata(self) -> Optional[BatchMetadata]:
        assert self.batch_ongoing(), "No batch submitted"
        return self._batch_metadata.metadata


class ResponseStyle:
    def __init__(self, template: str, model="gpt-4.1-mini-2025-04-14"):
        self.MODEL = model
        self.TEMPLATE = template

    def create_batch(self, tasks: Sequence[TaskItem], all_tasks: str) -> list[RequestInput]:
        return [
            {"custom_id": task["id"], "method": "POST", "url": "/v1/chat/completions",
             "body": {"model": self.MODEL,
                      "messages": [{"role": "system",
                                    "content": str(self.TEMPLATE).replace("<list>", all_tasks).replace("<element>",
                                                                                                       task[
                                                                                                           "overview"])}]}}
            for task in tasks
        ]


def parse_results(resp_text: str):
    resp_text = resp_text.strip()
    responses = [resp for resp in (json.loads(line) for line in resp_text.split("\n")) if resp["error"] is None]

    ids = [resp["custom_id"] for resp in responses]
    new_posts = [resp["response"]["body"]["choices"][0]["message"]["content"] for resp in responses]

    task_manager.mark_save(ids)
    metadata = ai_bridge.metadata

    try:
        with open("posts.json", "r", encoding="utf-8") as file:
            posts: dict[str, dict] = json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        posts = {}

    for new_post, id in zip(new_posts, ids):
        task = task_manager.find_task(id)
        posts[id] = {
            **metadata,
            "overview": task["overview"],
            "post": new_post
        }

    with open("posts.json", "w", encoding="utf-8") as file:
        json.dump(posts, file)


if __name__ == "__main__":
    load_dotenv()

    styles = {
        "tumblr": ResponseStyle(""""Here is my TODO list:
<list>
Focus on <element>
1. Thoughts before doing the task and what the problem is
2. Thoughts when starting the task
3. Thoughts while doing the task
4. Thoughts after finishing the task
5. Thoughts before writing a Reddit post
6. The reddit post. Optimize for encouragement and entertainment/interesting"""),
        "twitter": ResponseStyle(""""Here is my TODO list:
<list>
Focus on <element>
Make a Twitter post"""),
        "4chan": ResponseStyle(""""Here is my TODO list:
<list>
Focus on <element>
Make a 4chan post"""),
    }

    task_manager = TaskManager()
    ai_bridge = AIFacade()
    if ai_bridge.batch_ongoing():
        status, results = ai_bridge.fetch_batch()
        print(status)
        if results:
            parse_results(results)
    else:
        gen_number = int(input("How many posts would you like to generate? (default 0) ") or "0")
        if gen_number > 0:
            style = input(f"What style would you like to use? (options are {', '.join(styles.keys())}) ")
            assert style in styles, "Style not supported"
            style_agent = styles[style]
            ai_bridge.submit_batch(
                style_agent.create_batch(task_manager.next(gen_number), task_manager.all_tasks),
                metadata={
                    "platform": style,
                    "model": style_agent.MODEL,
                    "prompt": style_agent.TEMPLATE,
                }
            )

"""
The thing I tried different about this project was thinking really carefully about design patterns.
My takeaway is that like optimization, premature refactoring is really frustrating.
"""