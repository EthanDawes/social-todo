from typing import Mapping, TypedDict, Optional, Any, Sequence
from itertools import islice
import json
from datetime import datetime
from openai import OpenAI
import os


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


def merge_lists[T: Mapping](base: list[T], new: list[T], on="id"):
    combined: dict[Any, T] = {}
    for item in base + new:
        combined[item[on]] = item
    return list(combined.values())


class TaskManager:
    def __init__(self):
        self._flat_tasks: list[ExtendedTaskItem] = []
        self.load_file()

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
            {**item, "groupName": group["title"], "processedDate": None}
            for group in tasks["items"]
            for item in group["items"]
        ]

    @staticmethod
    def _sort_tasks[T: TaskItem](tasks: list[T]):
        return sorted(
            tasks,
            key=lambda x: x.get("due") or x["created"]
        )

    @staticmethod
    def _filter_used(tasks: Sequence[ExtendedTaskItem]):
        return filter(lambda x: x["status"] == "needsAction" and x["processedDate"] is None, tasks)

    def load_file(self):
        tasks, flat_tasks = self._load_tasks()
        new_flat_tasks = self._sort_tasks(self._flatten_tasks(tasks))
        self._flat_tasks = merge_lists(new_flat_tasks, flat_tasks)

    def _save(self):
        with open("tasks_flat.json", "w", encoding="utf-8") as file:
            json.dump(self._flat_tasks, file)

    def next(self, n: int):
        filtered = list(islice(self._filter_used(self._flat_tasks), n))
        for task in filtered:
            task["processedDate"] = datetime.now().isoformat()
        self._save()
        return filtered


class AIBridge:
    def __init__(self) -> None:
        self.client = OpenAI()
        self.BATCH_PATH = "batch_id"

        try:
            with open(self.BATCH_PATH, "r") as file:
                self.__batch_metadata = json.load(file)
        except FileNotFoundError:
            self.__batch_metadata = None

    def _upload_batch(self):
        batch_input_file = self.client.files.create(
            file=open("batchinput.jsonl", "rb"),
            purpose="batch"
        )
        return batch_input_file

    def submit_batch(self, tasks: Sequence[TaskItem]):
        assert not self.batch_ongoing(), "Batch already submitted"
        self._batch_metadata = self._upload_batch()
        self.client.batches.create(
            input_file_id=self._batch_metadata.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )

    @property
    def _batch_metadata(self):
        return self.__batch_metadata

    @_batch_metadata.setter
    def _batch_metadata(self, val: dict):
        self.__batch_metadata = val
        with open(self.BATCH_PATH, "w") as file:
            json.dump(val, file)

    def batch_ongoing(self):
        return self._batch_metadata is not None

    def fetch_batch(self):
        assert self.batch_ongoing(), "No batch submitted"
        self._batch_metadata = self.client.batches.retrieve(self._batch_metadata.id)
        match self._batch_metadata.status:
            case "validating" | "in_progress" | "finalizing":
                return None
            case "completed":
                file_response = self.client.files.content(self._batch_metadata.output_file_id)
                return file_response.text
        os.remove(self.BATCH_PATH)
        return None


class Converter:
    @staticmethod
    def create_batch(tasks: Sequence[TaskItem]):
        pass

    @staticmethod
    def save_results(posts):
        pass

if __name__ == "__main__":
    task_manager = TaskManager()
    ai_bridge = AIBridge()
    if ai_bridge.batch_ongoing:
        Converter.save_results(ai_bridge.fetch_batch())
    else:
        gen_number = int(input("How many posts would you like to generate? (default 0) ") or "0")
        if gen_number > 0:
            ai_bridge.submit_batch(Converter.create_batch(task_manager.next(gen_number)))
