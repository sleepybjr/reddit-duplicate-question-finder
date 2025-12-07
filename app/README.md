# Project Description
The purpose of this project is to serve as a backend for the Reddit Duplicate Question Finder.

It is a configurable tool which allows the use for extension of plugins for three core functions:
1. Query
2. Search
3. Summary

### Query
The query function takes an input from a Reddit post and generates a query string or questions to provide the search function. The default implementation uses Ollama LLM, but other methodology can be implemented as a replacement. The result of the query function is used by the search function.

### Search
The search function takes an input from query function result and begins searching different search API's or LLMs for answers to the question. The search function is special in the fact that multiple search API's or LLMs may be used to provide context for an aggregate answer. The default implementation uses Ollama LLM and SearXNG/Arctic-Shift, but other methodology can be implemented as a replacement or addition. The result of the search function is used by the summary function.

### Summary
The summary function takes an input from the search function and summarizes all the results into a final summary. The default implementation uses Ollama LLM, but other methodology can be implemented as a replacement. The result of the summary is passed back to the front end for display to the end user.

# Project Environment & Setup Guide

## Default Environment
- Windows 11
- Python 3.14
- Ollama
- SearXNG
- ArcticShift (online API)

## Software Installation
### Ollama
1. Install Ollama: https://ollama.com/
2. Run OllamaSetup.exe.
3. Click Install.
4. Open PowerShell.
5. Run ollama pull llama3.1

### SearXNG
https://docs.searxng.org/admin/installation.html
1. Install Docker Desktop.
2. Open Powershell.
3. docker compose up -d searxng

### Arctic-Shift
https://arctic-shift.photon-reddit.com/
1. API is used through the web.

## Environment Instructions
### Virtual Environment Creation:
```
python -m venv myenv
```

### Activate Virtual Environment
Run this **before every step**:

```
powershell
.\venv\Scripts\Activate.ps1
```

### Install Requirements
```
pip install -r requirements.txt
```

## Application Controls
#### Start Server
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Stop Server
```
CTRL + C
```

## Test Commands
### POST /generate_queries
```
$resp = Invoke-RestMethod -Uri "http://localhost:8000/generate_queries" `
    -Method POST `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body '{"title": "Good restaurants in Seattle?", "body": "Romantic places"}'

$resp | ConvertTo-Json -Depth 10
```

### POST /generate_search
```
$resp = Invoke-RestMethod -Uri "http://localhost:8000/generate_search" `
    -Method POST `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body '{"title": "Good restaurants in Seattle?", "body": "Romantic places"}'

$resp | ConvertTo-Json -Depth 10
```

### POST /generate_summary
```
$resp = Invoke-RestMethod -Uri "http://localhost:8000/generate_summary" `
    -Method POST `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body '{"title": "Good restaurants in Seattle?", "body": "Romantic places"}'

$resp | ConvertTo-Json -Depth 10
```