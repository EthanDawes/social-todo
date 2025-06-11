import httplib2
from google.oauth2.credentials import Credentials
from google_auth_httplib2 import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
import os

# Scopes for full access to Google Tasks
SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            http = httplib2.Http()
            creds.refresh(Request(http))
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def download_all_tasks(service):
    tasklists = service.tasklists().list(maxResults=100).execute().get('items', [])
    all_tasks = {}
    for lst in tasklists:
        tasks = []
        request = service.tasks().list(tasklist=lst['id'], showCompleted=True, showDeleted=True)
        while request:
            result = request.execute()
            tasks.extend(result.get('items', []))
            request = service.tasks().list_next(request, result)
        all_tasks[lst['title']] = tasks
    return all_tasks

def main():
    creds = authenticate()
    service = build('tasks', 'v1', credentials=creds)
    all_tasks = download_all_tasks(service)
    with open('google_tasks_backup.json', 'w') as f:
        json.dump(all_tasks, f, indent=2)
    print("All tasks downloaded and saved to google_tasks_backup.json")

if __name__ == '__main__':
    main()
