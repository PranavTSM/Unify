# Google Calendar & Gmail MCP Server (Python)

This project implements a **Python-based MCP (Model Context Protocol) server** that provides an interface between **Large Language Models (LLMs)** and the **Google Calendar** and **Gmail APIs**.
It enables advanced scheduling, event management, and email workflows with seamless **MCP integration**.

---

## 📖 Documentation

* **Getting Started**: [GETTING\_STARTED.md](GETTING_STARTED.md)
* **Architecture & Reference**: [DOCS.md](DOCS.md)

---

## ✨ Features

### 🔑 Authentication

* Secure **OAuth 2.0 (Desktop App Flow)** for Google APIs.
* Automatic token storage and refresh.

### 📅 Google Calendar

* **Core Actions**

  * List calendars → `mcp_google_calendar_list_calendars`
  * Create calendars → `mcp_google_calendar_create_calendar`
  * Find events (basic/advanced filters) → `mcp_google_calendar_find_events`
  * Create detailed events → `mcp_google_calendar_create_event`
  * Quick-add events from text → `mcp_google_calendar_quick_add_event`
  * Update events → `mcp_google_calendar_update_event`
  * Delete events → `mcp_google_calendar_delete_event`
  * Add attendees → `mcp_google_calendar_add_attendee`
* **Advanced Scheduling & Analysis**

  * Check attendee response → `mcp_google_calendar_check_attendee_status`
  * Query free/busy slots across calendars → `mcp_google_calendar_query_free_busy`
  * Schedule mutual free slots automatically → `mcp_google_calendar_schedule_mutual`
  * Analyze busyness (daily event counts & durations) → `mcp_google_calendar_analyze_busyness`

### 📧 Gmail

* List labels → `gmail_list_labels`
* Search/list messages with filters → `gmail_list_messages`
* Get messages in multiple formats → `gmail_get_message`
* Send email (simple or raw RFC 2822) → `gmail_compose_and_send`, `gmail_send_raw`
* Modify labels (add/remove) → `gmail_modify_labels`

### ⚡ Server

* **FastAPI-based REST API** exposing Calendar & Gmail endpoints.
* **MCP Integration**: Provides tools via stdio using the `mcp_sdk` library.

---

## ⚙️ Setup

### 1. Enable Google APIs

Enable the following in your **Google Cloud Project**:

* Google Calendar API
* Gmail API

### 2. Create OAuth Client

* Create an **OAuth 2.0 Client (Desktop App)**.
* Add redirect URI:

  ```
  http://localhost:8080/oauth2callback
  ```
* Configure consent screen and select required scopes.

### 3. Configure Environment

Copy `example.env` → `.env` and update with your credentials and scopes.
Recommended scopes:

```dotenv
GOOGLE_SCOPES='https://www.googleapis.com/auth/calendar, https://www.googleapis.com/auth/gmail.readonly, https://www.googleapis.com/auth/gmail.send, https://www.googleapis.com/auth/gmail.labels, https://www.googleapis.com/auth/gmail.modify'
```

### 4. Install & Run

```bash
pip install -r requirements.txt
python run_server.py
```

For a detailed walkthrough, see [GETTING\_STARTED.md](GETTING_STARTED.md).

---

## 🌐 HTTP Endpoints

### Calendar

* `GET /calendars`
* `GET /calendars/{calendar_id}/events`
* `POST /freeBusy`
* `POST /schedule_mutual`

### Gmail

* `GET /gmail/labels`
* `GET /gmail/messages`
* `GET /gmail/messages/{message_id}`
* `POST /gmail/messages:sendRaw`
* `POST /gmail/messages:composeAndSend`
* `POST /gmail/messages/{message_id}:modify`

---

## 🛠️ MCP Tools

### Calendar

* `list_calendars`
* `find_events`
* `create_event`
* `quick_add_event`
* `update_event`
* `delete_event`
* `add_attendee`
* `check_attendee_status`
* `query_free_busy`
* `schedule_mutual`
* `analyze_busyness`

### Gmail

* `gmail_list_labels`
* `gmail_list_messages`
* `gmail_get_message`
* `gmail_compose_and_send`
* `gmail_send_raw`
* `gmail_modify_labels`

---

## 📌 Notes

* Works best with **LLM-powered assistants** for smart scheduling and email management.
* Supports **MCP stdio integration** for seamless AI workflows.
