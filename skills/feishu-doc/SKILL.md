---
name: feishu-doc
description: Use when user asks for 飞书文档 / feishu doc / lark doc. Create, read, and populate Feishu/Lark documents via the Open API — authentication, document CRUD, block manipulation, and content formatting.
category: productivity
triggers:
  - "飞书文档"
  - "feishu doc"
  - "飞书"
  - "lark doc"
  - "创建飞书文档"
---

# Feishu Document API

Create and format Feishu documents programmatically using the Open API (`open.feishu.cn`).

## Prerequisites

Hermes running on Feishu platform automatically has `FEISHU_APP_ID` and `FEISHU_APP_SECRET` environment variables. These are the bot's credentials.

## Authentication

```python
import os, urllib.request, json

app_id = os.environ["FEISHU_APP_ID"]
app_secret = os.environ["FEISHU_APP_SECRET"]

req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": app_id, "app_secret": app_secret}).encode(),
    headers={"Content-Type": "application/json"}
)
resp = json.loads(urllib.request.urlopen(req).read())
token = resp["tenant_access_token"]
```

## Document CRUD

### Create a document

```python
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/docx/v1/documents",
    data=json.dumps({"title": "文档标题"}).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
)
resp = json.loads(urllib.request.urlopen(req).read())
doc_id = resp["data"]["document"]["document_id"]
```

### Read document content

```python
# Get page block
req = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}",
    headers={"Authorization": f"Bearer {token}"}
)
resp = json.loads(urllib.request.urlopen(req).read())
```

## Adding Content Blocks

The Feishu Docx API uses a block tree. Each block has a `block_type` and a top-level key matching the type name.

### Block type reference

| `block_type` | Key | Description |
|:--|:--|:--|
| 1 | `page` | Root page block |
| 2 | `text` | Body paragraph |
| 3 | `heading1` | H1 |
| 4 | `heading2` | H2 |
| 5 | `heading3` | H3 |
| 12 | `bullet` | Unordered list item |
| 13 | `ordered` | Ordered list item |
| 22 | `divider` | Horizontal rule |
| 31 | `table` | Table container |
| 32 | `table_cell` | Individual cell (NOT block_type 29 as older docs state) |

### Block construction helpers (concise pattern)

```python
BK = {2:"text", 3:"heading1", 4:"heading2", 5:"heading3", 12:"bullet", 22:"divider"}

def te(t, b=False):
    """Text element — the atomic content unit in every block."""
    return {"text_run": {"content": t, "text_element_style": {"bold": b}}}

def mb(bt, els):
    """Make block — wraps elements in the correct type key."""
    k = BK[bt]
    return {"block_type": bt, k: {"elements": els, "style": {}}}
```

This helper pattern keeps block construction concise on long scripts. Usage:

```python
blocks = [
    mb(3, [te("Section Title", b=True)]),           # heading1
    mb(12, [te("Bullet item")]),                      # bullet
    {"block_type": 22, "divider": {}},               # divider
]
```

### Add blocks to document (append at root)

```python
blocks = [...]  # build your block list

url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children"

# Send in batches of 10 (hard limit)
for i in range(0, len(blocks), 10):
    batch = blocks[i:i+10]
    req = urllib.request.Request(
        url,
        data=json.dumps({"children": batch}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    json.loads(urllib.request.urlopen(req).read())
```

### Tables — creation and cell population

Tables are created as **empty containers**. Cells are auto-generated and each contains a child text block (block_type 2) that you must populate individually.

**Step 1: Create the table (empty)**

```python
table_block = {
    "block_type": 31,  # table
    "table": {
        "property": {
            "row_size": 2,       # header + 1 data row
            "column_size": 3     # 3 columns
        }
    }
}

resp = api("POST", f"/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
           json.dumps({"children": [table_block]}).encode())
```

**Step 2: Get cell IDs from the response**

The response returns a `cells` array with block_ids in row-major order:

```python
cells = resp["data"]["children"][0]["table"]["cells"]
# e.g. ["doxcn...cell1", "doxcn...cell2", "doxcn...cell3",  # Row 0
#       "doxcn...cell4", "doxcn...cell5", "doxcn...cell6"]  # Row 1
```

**Step 3: Find the child text block inside each cell**

Cell block_type is **32** (not 29 as some older docs state). Each cell contains exactly one child text block (block_type 2). You must GET the cell, read its child, then PATCH that child:

```python
def get_child_text_block(doc_id, cell_id):
    """Fetch a table cell and return its child text block ID."""
    resp = api("GET", f"/docx/v1/documents/{doc_id}/blocks/{cell_id}")
    children = resp["data"]["block"]["children"]
    return children[0]  # always a single text block

def set_cell_content(doc_id, child_block_id, text, bold=False):
    """Set the text of a table cell's child text block."""
    api("PATCH", f"/docx/v1/documents/{doc_id}/blocks/{child_block_id}",
        json.dumps({"update_text_elements": {
            "elements": [{"text_run": {
                "content": text,
                "text_element_style": {"bold": bold}
            }}]
        }}).encode())
```

**Step 4: Populate cells**

```python
for cell_id, (text, is_bold) in zip(cell_ids, contents):
    child_id = get_child_text_block(doc_id, cell_id)
    set_cell_content(doc_id, child_id, text, is_bold)
```

**⚠️ Critical: Do NOT PATCH the cell (block_type 32) directly.** The `update_text_elements` operation on a table cell returns `code: 1770025` ("operation and block not match"). You must always target the **child text block** inside the cell.

**Resizing tables (adding rows)**

```python
# Update the table property to add rows
resp = api("PATCH", f"/docx/v1/documents/{doc_id}/blocks/{table_block_id}",
    json.dumps({"update_table_property": {
        "row_size": new_row_count,
        "column_size": 3
    }}).encode())
```

Note: After resizing, new cell block_ids do NOT automatically appear in the response. Re-fetch the table block to get updated cell IDs. New cells are blank and need cell population (Step 3-4).

**Design tip**: Given the complexity of populating many table rows one cell at a time, prefer using structured content (headings + bullets) for large datasets (10+ rows). Reserve tables for small summary tables (under 10 rows) where the visual layout justifies the API overhead.

## Sending the Doc Link to Chat

```python
# First list targets
# send_message(action='list')

# Then send
# send_message(
#     target='feishu:oc_xxx',
#     message=f"文档已创建 📄\n🔗 https://bytedance.feishu.cn/docx/{doc_id}"
# )
```

> ⚠️ `target='origin'` is NOT supported. Always `list` first to get the exact target string.

## Document Permissions & Sharing

### The Problem: bot-created docs live in the bot's private space

When you create a doc via API with `tenant_access_token`, the document belongs to the **bot application**, not the user. The user **cannot** see "权限管理" in the UI — they only see "申请权限". To give the user edit access:

**Method A: Drive API (requires TWO separate steps)**

```python
# Grant edit permission to a user by open_id
# USER_OPEN_ID comes from the session context header 'User ID: ou_xxx'
data = json.dumps({
    "member_type": "openid",
    "member_id": "ou_b2adf6153564b8a837b2a44f45182050",
    "perm": "edit"
}).encode()
url = f"https://open.feishu.cn/open-apis/drive/v1/permissions/{doc_id}/members?type=docx&need_notification=false"
# POST with Bearer token
```

**⚠️ Two-step process that catches most agents off guard:**

```
Step 1: 开发者后台                 Step 2: 租户管理员授权
  添加 API 权限                      打开授权链接
  发布新版本                         点"授权"
        ↓                                   ↓
  应用权限 (scope) ✅             应用身份权限 ✅
                                      ↓
                              API 调用才能成功
```

| 操作 | 所需 API 权限 (Step 1) | 错误码 |
|:--|:--|:--:|
| 创建文档 | `docx:document` | — |
| 增删协作者 | `docs:permission.member:create` | 99991672 |
| 查看协作者 | `docs:permission.member:retrieve` | 99991672 |
| 推荐：一起加 | `drive:file`（涵盖全部） | — |

**Step 1** — 在飞书开发者后台 → 权限管理 添加 scope → 创建新版本 → 发布
**Step 2** — 打开授权链接（在 99991672 错误里会返回）：
```
https://open.feishu.cn/app/{app_id}/auth?q=docs:permission.member:create
```
开发者后台 → 安全设置 → 应用授权 也可以找到入口。需要**租户管理员**账号登录，点"授权"后才生效。

> 🚨 常见误区：只做了 Step 1（加权限+发布）就以为行了。必须 Step 2 也完成。飞书把 API scope 和 "应用身份权限" 拆成两套独立系统。

**Method B: User-facing "添加文档应用" (no API needed)**

The user opens the doc → 「…」→「更多」→「添加文档应用」→ search for the bot app → add as editor. This is the recommended path for most use cases.

**Method C: Copy-paste (fastest, no auth headaches)**

Create the doc, extract the content as markdown, send it to the user's chat. They paste it into their own Feishu doc → they own it, they have edit permission by default.

### Alternative: Create doc in a shared folder/wiki

If the bot has been added as a group robot and that group has access to a folder/wiki, create docs there. The doc inherits the folder's permissions.

## Listing Documents

### List all files the bot has access to

```python
url = f"https://open.feishu.cn/open-apis/drive/v1/files?page_size=20"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
resp = json.loads(urllib.request.urlopen(req).read())
# resp["data"]["files"] — list of file objects
```

Response fields:

| Field | Type | Meaning |
|:--|:--|:--|
| `token` | str | Document token (use in docx API and permissions API) |
| `name` | str | Document title |
| `type` | str | `docx`, `sheet`, `file`, etc. |
| `owner_id` | str | Open ID of owner — `tenant_access_token` list shows bot-owned files |
| `url` | str | Full Feishu URL |
| `created_time` / `modified_time` | str | Unix timestamps |
| `parent_token` | str | Parent folder token |
| `has_more` | bool | Pagination flag |

**Required scope**: `drive:drive:readonly` (or `drive:drive`) — must be authorized via tenant admin auth URL:
```
https://open.feishu.cn/app/{app_id}/auth?q=drive:drive:readonly
```

> ⚠️ `drive/v1/files` lists files in the **bot's drive space** when using `tenant_access_token`. It does NOT list all files in the org — only those the bot owns or has been explicitly added to.

### Search files (requires `user_access_token`)

```python
url = "https://open.feishu.cn/open-apis/drive/v1/files/search"
data = json.dumps({"search_key": "", "file_types": ["docx"], "page_size": 50}).encode()
```

This endpoint **requires `user_access_token`** (a real user's token), not `tenant_access_token`. With `tenant_access_token` it returns `code: 99991663` (invalid token). Not usable in automated bot workflows.

### Build a document inventory

To give the user a list of every document the bot has ever created:

```python
url = f"https://open.feishu.cn/open-apis/drive/v1/files?page_size=100"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
resp = json.loads(urllib.request.urlopen(req).read())

files = resp["data"]["files"]
for f in files:
    print(f"📄 {f['name']}")
    print(f"   🔗 {f['url']}")
    print(f"   🆔 token: {f['token']}")
```

The bot's drive space is a flat namespace — no folders by default. Files are organized by `parent_token` (which is the root folder `nodcnFrLzVMwjMSbYAFwBJaiAmh` for bot-created docs).

## Updating and Deleting Blocks

### Update block content (PATCH)

You can update the text of an existing block using PATCH:

```python
# Update a text block's content
api("PATCH", f"/docx/v1/documents/{doc_id}/blocks/{block_id}",
    json.dumps({"update_text_elements": {
        "elements": [{"text_run": {
            "content": "New text content",
            "text_element_style": {}
        }}]
    }}).encode())
```

This works on text blocks (block_type 2), heading blocks (3-5), and bullet/ordered blocks (12-13).

### Delete children in bulk (batch_delete)

To clear all children from a parent block (e.g. reset a document root to empty):

```python
# First, GET the parent block to find its children
resp = api("GET", f"/docx/v1/documents/{doc_id}/blocks/{parent_block_id}")
existing = resp["data"]["block"]["children"]  # array of string block IDs

# Then batch delete all children
# start_index=0 (inclusive), end_index=N (exclusive) → deletes children[0:N]
api("DELETE", f"/docx/v1/documents/{doc_id}/blocks/{parent_block_id}/children/batch_delete",
    json.dumps({"start_index": 0, "end_index": len(existing)}).encode())
```

**⚠️ The endpoint is `batch_delete`, NOT `batch`.** Using `batch` (without `_delete`) returns HTTP 404. This is counterintuitive because the table resize endpoint uses `update_table_property` (a verb in the body, not the path) — but batch delete follows the REST convention of `DELETE` + path verb.

**⚠️ Indices are 0-based and end_index is exclusive.** `start_index=0, end_index=len(existing)` deletes all children. This is equivalent to a full reset of the block.

### Pattern: Full document rewrite

```python
# 1. Delete all existing children
resp = api("GET", f"/docx/v1/documents/{doc_id}/blocks/{doc_id}")
existing = resp["data"]["block"]["children"]
first = existing[0] if isinstance(existing[0], str) else existing[0]["block_id"]
# The first child's ID confirms the parent. Use doc_id as parent for root.
api("DELETE", f"/docx/v1/documents/{doc_id}/blocks/{doc_id}/children/batch_delete",
    json.dumps({"start_index": 0, "end_index": len(existing)}).encode())

# 2. Add new blocks
for i in range(0, len(new_blocks), 10):
    api("POST", f"/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
        json.dumps({"children": new_blocks[i:i+10]}).encode())
```

## Pitfalls

- **block_type / key mismatch**: `block_type: 3` requires key `heading1`, NOT `text`. Mismatch causes HTTP 400.
- **Batch limit**: Maximum 10 blocks per `POST children` request.
- **Title immutability**: Document title cannot be changed after creation via the blocks API — set it correctly on creation.
- **app_secret visibility**: The `FEISHU_APP_SECRET` env var is partially redacted when printed to console (`7XbNwh...VOWp`) but contains the full 32-char value in `os.environ`. Access via Python's `os.environ`, not by reading the truncated console output.
- **Rate limiting**: The Feishu Open API has per-app rate limits. Batch aggressively (10 blocks per call) to minimize requests.
- **No formatting API for messages**: Feishu chat messages support basic markdown (bold, code, links) but NOT tables or complex formatting. For rich layout, always create a doc and share the link.
- **Chinese quotation marks in shell heredocs break Python syntax**: When passing Python scripts containing Chinese text via `terminal`, Chinese quotation marks inside Python string literals can be misinterpreted by the shell, causing `SyntaxError: invalid syntax`. The fix: always write the Python script to a file with `write_file()` first, then execute it with `terminal(command='python3 /tmp/script.py')`. Shell heredocs are fine for ASCII-only Python code; for any script with Chinese text, use file-based execution.
- **Table row resize does NOT auto-create cells**: Calling `update_table_property` with a larger `row_size` returns code 0, but new cells are NOT generated — the field updates but cell count stays. Prefer creating tables with the final row count upfront. For 10+ rows, use structured text blocks (headings + bullets) instead of a table.
- **PATCH on table_cell (block_type 32) returns 1770025**: The `update_text_elements` call on a table_cell block gives "operation and block not match". Always GET the cell, find its child text block (block_type 2), then PATCH the child instead.
- **Children returned as strings, not dicts**: The API returns `children` as an array of plain string block IDs, NOT dict objects. Code checking `isinstance(child, dict) and "block_id" in child` silently skips ALL children. Handle both types: `cid = child if isinstance(child, str) else child.get("block_id", "")`
- **Bullet/ordered block text lacks markdown `- ` prefix**: When reading bullet (block_type 12) or ordered (block_type 13) content via the API, the extracted text is raw without list markers. Parsers expecting `- ` prefixes will miss all items. Strip prefixes at parse time or don't expect them.
