#!/usr/bin/env python3
"""
Task Batch Processor - Converts tasks to social media posts using OpenAI Batch API
"""

import json
import os
import sys
from datetime import datetime
from typing import List
from openai import OpenAI
from types import *


class Config:
    """Configuration constants"""
    TASKS_FILE = "tasks.json"
    BATCH_STATUS_FILE = "batch_status.json"
    PROCESSED_TASKS_FILE = "processed_tasks.json"
    RESULTS_DIR = "results"
    BATCH_REQUESTS_FILE = "batch_requests.jsonl"
    MODEL = "gpt-4o"
    PLATFORM = "linkedin"  # Change as needed

    @classmethod
    def ensure_dirs(cls):
        """Ensure required directories exist"""
        os.makedirs(cls.RESULTS_DIR, exist_ok=True)


def load_json_file(filepath: str, default=None):
    """Load JSON file with error handling"""
    if not os.path.exists(filepath):
        return default if default is not None else {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {filepath}: {e}")
        return default if default is not None else {}


def save_json_file(filepath: str, data):
    """Save data to JSON file with error handling"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error saving {filepath}: {e}")
        return False


def get_unprocessed_tasks(task_list: TaskList, n: int) -> List[TaskItem]:
    """Select n unprocessed tasks sorted by creation date"""
    processed_tasks = load_json_file(Config.PROCESSED_TASKS_FILE, [])
    processed_ids = {task.get('id') for task in processed_tasks}

    all_tasks = []
    for group in task_list.get('items', []):
        for task in group.get('items', []):
            if task['id'] not in processed_ids and task.get('status') != 'completed':
                all_tasks.append({
                    **task,
                    'category': group['title']
                })

    # Sort by created date (oldest first)
    all_tasks.sort(key=lambda x: x.get('created', ''))

    return all_tasks[:n]


def create_prompt(all_tasks: List[dict], focus_task: dict, platform: str) -> str:
    """Create prompt for AI processing"""
    tasks_summary = []
    for task in all_tasks:
        category = task.get('category', 'General')
        title = task.get('title', '')
        description = task.get('notes', '') or ''
        tasks_summary.append(f"{category}: {title} - {description}".strip())

    focus_category = focus_task.get('category', 'General')
    focus_title = focus_task.get('title', '')
    focus_description = focus_task.get('notes', '') or ''
    focus_summary = f"{focus_category}: {focus_title} - {focus_description}".strip()

    all_todos_str = "\n".join(tasks_summary)

    return f"<all todos>\n{all_todos_str}\n</all todos>\n\nFocus on '{focus_summary}' and write a {platform} post"


def create_batch_request(tasks: List[dict], platform: str, model: str) -> List[RequestInput]:
    """Create batch request inputs"""
    requests = []

    for i, task in enumerate(tasks):
        prompt = create_prompt(tasks, task, platform)

        request_input: RequestInput = {
            "custom_id": f"task_{task['id']}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are a social media content creator specializing in {platform} posts. Create engaging, professional content based on the given tasks."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        }
        requests.append(request_input)

    return requests


def submit_batch_request(client: OpenAI, requests: List[RequestInput], metadata: List[BatchMetadata]) -> Optional[str]:
    """Submit batch request to OpenAI"""
    try:
        # Save requests to JSONL file
        with open(Config.BATCH_REQUESTS_FILE, 'w', encoding='utf-8') as f:
            for request in requests:
                f.write(json.dumps(request) + '\n')

        # Upload file
        with open(Config.BATCH_REQUESTS_FILE, 'rb') as f:
            batch_file = client.files.create(
                file=f,
                purpose="batch"
            )

        # Create batch
        batch = client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )

        # Save batch status
        batch_status = {
            "batch_id": batch.id,
            "status": batch.status,
            "created_at": datetime.now().isoformat(),
            "file_id": batch_file.id,
            "metadata": metadata
        }
        save_json_file(Config.BATCH_STATUS_FILE, batch_status)

        print(f"Batch request submitted successfully. Batch ID: {batch.id}")
        return batch.id

    except Exception as e:
        print(f"Error submitting batch request: {e}")
        return None


def check_batch_status(client: OpenAI) -> Optional[str]:
    """Check status of ongoing batch request"""
    batch_status = load_json_file(Config.BATCH_STATUS_FILE)
    if not batch_status or 'batch_id' not in batch_status:
        return None

    try:
        batch = client.batches.retrieve(batch_status['batch_id'])
        batch_status['status'] = batch.status
        batch_status['updated_at'] = datetime.now().isoformat()

        if hasattr(batch, 'request_counts'):
            batch_status['request_counts'] = {
                'total': batch.request_counts.total,
                'completed': batch.request_counts.completed,
                'failed': batch.request_counts.failed
            }

        save_json_file(Config.BATCH_STATUS_FILE, batch_status)

        print(f"Batch status: {batch.status}")
        return batch.status

    except Exception as e:
        print(f"Error checking batch status: {e}")
        return "error"


def process_completed_batch(client: OpenAI) -> bool:
    """Process completed batch and save results"""
    batch_status = load_json_file(Config.BATCH_STATUS_FILE)
    if not batch_status:
        return False

    try:
        batch = client.batches.retrieve(batch_status['batch_id'])

        if not batch.output_file_id:
            print("No output file available")
            return False

        # Download results
        result_file_response = client.files.content(batch.output_file_id)
        result_content = result_file_response.content.decode('utf-8')

        # Process each result
        processed_tasks = []
        metadata_map = {item['prompt']: item for item in batch_status.get('metadata', [])}

        for line in result_content.strip().split('\n'):
            if not line:
                continue

            try:
                result = json.loads(line)
                custom_id = result.get('custom_id', '')
                task_id = custom_id.replace('task_', '')

                if result.get('response') and result['response'].get('body'):
                    response_body = result['response']['body']
                    if response_body.get('choices') and len(response_body['choices']) > 0:
                        ai_response = response_body['choices'][0]['message']['content']

                        # Find matching metadata
                        matching_metadata = None
                        for metadata in batch_status.get('metadata', []):
                            if task_id in metadata.get('prompt', ''):
                                matching_metadata = metadata
                                break

                        if matching_metadata:
                            processed_task = {
                                "platform": matching_metadata['platform'],
                                "model": matching_metadata['model'],
                                "prompt": matching_metadata['prompt'],
                                "overview": matching_metadata['prompt'].split("Focus on '")[1].split("' and write")[
                                    0] if "Focus on '" in matching_metadata['prompt'] else "",
                                "post": ai_response,
                                "id": task_id,
                                "processed_at": datetime.now().isoformat()
                            }
                            processed_tasks.append(processed_task)

                            # Save individual result
                            result_filename = f"{Config.RESULTS_DIR}/task_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                            save_json_file(result_filename, processed_task)

            except json.JSONDecodeError as e:
                print(f"Error parsing result line: {e}")
                continue

        if processed_tasks:
            # Update processed tasks file
            existing_processed = load_json_file(Config.PROCESSED_TASKS_FILE, [])
            existing_processed.extend(processed_tasks)
            save_json_file(Config.PROCESSED_TASKS_FILE, existing_processed)

            print(f"Successfully processed {len(processed_tasks)} tasks")

            # Clean up batch status
            os.remove(Config.BATCH_STATUS_FILE)
            if os.path.exists(Config.BATCH_REQUESTS_FILE):
                os.remove(Config.BATCH_REQUESTS_FILE)

            return True

        return False

    except Exception as e:
        print(f"Error processing completed batch: {e}")
        return False


def main():
    """Main execution function"""
    if len(sys.argv) < 2:
        print("Usage: python script.py <number_of_tasks>")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Number of tasks must be an integer")
        sys.exit(1)

    # Initialize
    Config.ensure_dirs()
    client = OpenAI()

    # Check if there's an ongoing batch request
    batch_status = load_json_file(Config.BATCH_STATUS_FILE)
    if batch_status and 'batch_id' in batch_status:
        print("Found ongoing batch request. Checking status...")
        status = check_batch_status(client)

        if status == "completed":
            print("Batch completed! Processing results...")
            if process_completed_batch(client):
                print("Results saved successfully")
            else:
                print("Failed to process results")
            sys.exit(0)
        elif status == "failed":
            print("Batch request failed")
            sys.exit(1)
        else:
            print(f"Batch still in progress (status: {status})")
            sys.exit(0)

    # Load tasks
    task_list = load_json_file(Config.TASKS_FILE)
    if not task_list:
        print(f"No tasks found in {Config.TASKS_FILE}")
        sys.exit(1)

    # Select unprocessed tasks
    unprocessed_tasks = get_unprocessed_tasks(task_list, n)
    if not unprocessed_tasks:
        print("No unprocessed tasks found")
        sys.exit(0)

    print(f"Selected {len(unprocessed_tasks)} tasks for processing")

    # Create batch requests
    requests = create_batch_request(unprocessed_tasks, Config.PLATFORM, Config.MODEL)

    # Create metadata for each task
    metadata = []
    for task in unprocessed_tasks:
        prompt = create_prompt(unprocessed_tasks, task, Config.PLATFORM)
        metadata.append({
            "platform": Config.PLATFORM,
            "model": Config.MODEL,
            "prompt": prompt
        })

    # Submit batch request
    batch_id = submit_batch_request(client, requests, metadata)
    if batch_id:
        print("Batch request submitted successfully. Run the script again to check status.")
    else:
        print("Failed to submit batch request")
        sys.exit(1)


if __name__ == "__main__":
    main()