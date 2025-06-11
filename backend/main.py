print("Loading...")
from random import shuffle
from typing import Mapping, Any, Sequence, Iterable
from itertools import islice
import json
from datetime import datetime
from openai import OpenAI
import io
from dotenv import load_dotenv

from openai.types import *
from prototype.backend.dl_gtasks import dl_gtasks
from task_types import *


class ExtendedTaskItem(TaskItem):
    """Added after processing"""
    groupName: str
    processedDate: Optional[str]
    overview: str


# Using lists instead of dicts (which would merge easier) b/c I need to use the list methods
def merge_lists[T: Mapping](base: list[T], new: list[T], on="id"):
    combined: dict[Any, T] = {}
    for item in base + new:
        if item[on] in combined:
            combined[item[on]] = {**item, **combined[item[on]]}
        else:
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
        self.save()

    @staticmethod
    def _load_tasks():
        with open("google_tasks_backup.json", "r", encoding="utf-8") as file:
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
            {**item, "groupName": groupName, "processedDate": None,
             "overview": f"{groupName}: {item["title"]} {item.get('notes', '').strip()}"}
            for groupName, items in tasks.items()
            for item in items
        ]

    @staticmethod
    def _sort_tasks[T: TaskItem](tasks: list[T]):
        return sorted(
            tasks,
            key=lambda x: x.get("due") or x["updated"]
        )

    def next(self, n: int) -> list[ExtendedTaskItem]:
        return list(islice(self._filter_used(self._flat_tasks), n))

    @staticmethod
    def _filter_used(tasks: Sequence[ExtendedTaskItem]):
        return filter(lambda x: x["status"] == "needsAction" and x["processedDate"] is None, tasks)

    def find_task(self, id: str) -> ExtendedTaskItem:
        return next(filter(lambda task: task["id"] == id, self._flat_tasks))

    def save(self):
        with open("tasks_flat.json", "w", encoding="utf-8") as file:
            json.dump(self._flat_tasks, file, indent=2)

    def mark_save(self, tasks_ids: Iterable[str]):
        for task_id in tasks_ids:
            task = self.find_task(task_id)
            task["processedDate"] = datetime.now().isoformat()
        self.save()

    @property
    def all_tasks(self):
        return [task["overview"] for task in self._flat_tasks]


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
                response = self.client.files.content(self._batch_metadata.output_file_id).text
        print("must manually remove", self.BATCH_PATH, "to make new batch")
        # os.remove(self.BATCH_PATH)  # This technically leads to invalid state
        return status, response

    @property
    def metadata(self) -> Optional[BatchMetadata]:
        assert self.batch_ongoing(), "No batch submitted"
        return self._batch_metadata.metadata


class ResponseStyle:
    def __init__(self, template: str, model="gpt-4.1-2025-04-14"):
        self.MODEL = model
        self.TEMPLATE = template

    def create_batch(self, tasks: Sequence[TaskItem], all_tasks: list[str]) -> list[RequestInput]:
        # TODO: including my entire task list is ~20k tokens. This is expensive and exceeds 90k limit. Solutions:
        # First 100 is ~1,400 tokens (much more reasonable)
        # Instruct to make all the output posts in one prompt (to reduce duplication) but could this have memory issues? + Parsing complexity
        shuffle(all_tasks)
        all_tasks = all_tasks[:100]
        return [
            {"custom_id": task["id"], "method": "POST", "url": "/v1/chat/completions",
             "body": {"model": self.MODEL,
                      "messages": [{"role": "system",
                                    "content": str(self.TEMPLATE).replace("<list>", "\n".join(all_tasks)).replace("<element>",
                                                                                                       task[
                                                                                                           "overview"])}]}}
            for task in tasks
        ]


def save_results(resp_text: str):
    resp_text = resp_text.strip()
    responses = [resp for resp in (json.loads(line) for line in resp_text.split("\n")) if resp["error"] is None]

    ids = [resp["custom_id"] for resp in responses]
    new_posts = [resp["response"]["body"]["choices"][0]["message"]["content"] for resp in responses]

    task_manager.mark_save(ids)
    metadata = ai_bridge.metadata

    with open("posts.json", "r", encoding="utf-8") as file:
        contents = file.read()  # Can only read once
        posts: dict[str, dict] = json.loads(contents) if len(contents) else {}

    for new_post, id in zip(new_posts, ids):
        task = task_manager.find_task(id)
        posts[id] = {
            **metadata,
            "overview": task["overview"],
            "post": new_post,
            "id": id,
        }

    with open("posts.json", "w", encoding="utf-8") as file:
        json.dump(posts, file, indent=2)


if __name__ == "__main__":
    load_dotenv()

    styles = {
        "tumblr": ResponseStyle("""Here is my TODO list:
<list>
Focus on <element>
1. Thoughts before doing the task and what the problem is
2. Thoughts when starting the task
3. Thoughts while doing the task
4. Thoughts after finishing the task
5. Thoughts about sharing with other people
Utilize queer humor, furry humor, programming humor, or a mix.
Do not add introductory or concluding sentences as the AI agent.
Format each section as a markdown header."""),
        "twitter": ResponseStyle("""Here is my TODO list:
<list>
Focus on <element>
Make a Twitter post"""),
        "4chan": ResponseStyle("""Here is my TODO list:
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
            save_results(results)
    else:
        if (input("Would you like to redownload your Google Tasks (default n) ") or "n")[0] == "y":
            dl_gtasks()
        gen_number = int(input("How many posts would you like to generate? (default 0) ") or "0")
        if gen_number > 0:
            style = input(f"What style would you like to use? (options are {', '.join(styles.keys())}) ")
            assert style in styles, "Style not supported"
            style_agent = styles[style]
            batch_tasks = task_manager.next(gen_number)
            print("Going to generate posts for:\n" + "\n".join(task["overview"] for task in batch_tasks))
            print("\nWith prompt\n" + style_agent.TEMPLATE)
            if (input("Is this ok? (default y) ") or "y")[0] != "y":
                exit(1)
            ai_bridge.submit_batch(
                style_agent.create_batch(batch_tasks, task_manager.all_tasks),
                metadata={
                    "platform": style,
                    "model": style_agent.MODEL,
                    "prompt": style_agent.TEMPLATE,
                }
            )
