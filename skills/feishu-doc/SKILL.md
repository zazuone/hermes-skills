---
name: feishu-doc
description: Create, read, and populate Feishu/Lark documents via the Open API — authentication, document CRUD, block manipulation, and content formatting.
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

### Block construction pattern

```python
BLOCK_TYPE_TO_KEY = {
    2: "text", 3: "heading1", 4: "heading2", 5: "heading3",
    6: "heading4", 7: "heading5", 8: "heading6",
    12: "bullet", 13: "ordered", 22: "divider",
}

def make_block(bt, elements):
    key = BLOCK_TYPE_TO_KEY[bt]
    return {"block_type": bt, key: {"elements": elements, "style": {}}}

def text_element(txt, bold=False):
    return {"text_run": {"content": txt, "text_element_style": {"bold": bold}}}
```

### Add blocks to document (append at root)

```python
blocks = [
    make_block(3, [text_element("Section Title", bold=True)]),
    make_block(12, [text_element("List item")]),
    {"block_type": 22, "divider": {}},
]

url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children"

# Send in batches of 10
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

## Pitfalls

- **block_type / key mismatch**: `block_type: 3` requires key `heading1`, NOT `text`. Mismatch causes HTTP 400.
- **Batch limit**: Maximum 10 blocks per `POST children` request.
- **Title immutability**: Document title cannot be changed after creation via the blocks API — set it correctly on creation.
- **app_secret visibility**: The `FEISHU_APP_SECRET` env var is partially redacted when printed to console (`7XbNwh...VOWp`) but contains the full 32-char value in `os.environ`. Access via Python's `os.environ`, not by reading the truncated console output.
- **Rate limiting**: The Feishu Open API has per-app rate limits. Batch aggressively (10 blocks per call) to minimize requests.
- **No formatting API for messages**: Feishu chat messages support basic markdown (bold, code, links) but NOT tables or complex formatting. For rich layout, always create a doc and share the link.
