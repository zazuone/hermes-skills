#!/usr/bin/env python3
"""
feishu_task_tool.py — 飞书文档任务管理工具。

用于 cron job 自动化：读取每日任务日志、追加执行记录、更新任务状态。

用法:
  python3 feishu_task_tool.py read_tasks
  python3 feishu_task_tool.py append_log  "原记录"  "方案"  "结果"  "待完成"
  python3 feishu_task_tool.py update_tasks  '["task1"]'  '[]'  '["task1 (time)"]'
  python3 feishu_task_tool.py grant_permission  <doc_id>  <user_open_id>
"""

import os, sys, json, urllib.request
from datetime import datetime

# ============================================================
# 配置 — 保持不变
# ============================================================
TASK_DOC_ID = "Vua7d1EhOoDipqxwV4ocZUKJnMf"       # 📋 每日任务日志
LOG_DOC_ID  = "IMWodguGDoboILxP1wUc6hhlngd"         # 🗃 任务自动化 — 执行日志
USER_OPEN_ID = "ou_b2adf6153564b8a837b2a44f45182050"

# ============================================================
# Auth
# ============================================================
def get_token():
    app_id = os.environ["FEISHU_APP_ID"]
    app_secret = os.environ["FEISHU_APP_SECRET"]
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=json.dumps({"app_id": app_id, "app_secret": app_secret}).encode(),
        headers={"Content-Type": "application/json"}
    )
    return json.loads(urllib.request.urlopen(req).read())["tenant_access_token"]

token = None
def T():
    global token
    if not token:
        token = get_token()
    return token

def api(method, path, data=None):
    url = f"https://open.feishu.cn/open-apis{path}"
    h = {"Authorization": f"Bearer {T()}", "Content-Type": "application/json"}
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    return json.loads(urllib.request.urlopen(r).read())

# ============================================================
# Block helpers
# ============================================================
BK = {2:"text",3:"heading1",4:"heading2",5:"heading3",12:"bullet",22:"divider"}
def te(t, b=False):
    return {"text_run":{"content":t,"text_element_style":{"bold":b,"inline_code":False}}}
def mb(bt, els):
    k=BK[bt]; return {"block_type":bt,k:{"elements":els,"style":{}}}
def add_blocks(doc_id, blocks):
    for i in range(0,len(blocks),10):
        api("POST",f"/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
            json.dumps({"children":blocks[i:i+10]}).encode())

# ============================================================
# Read document content as plain text
# ============================================================
def read_doc_text(doc_id):
    """Read all blocks and return plain text."""
    resp = api("GET", f"/docx/v1/documents/{doc_id}/blocks/{doc_id}?page_size=500")
    items = []
    def walk(b):
        bt = b.get("block_type")
        if bt == 22:  # divider
            items.append("---")
            return
        for key in ("text","heading1","heading2","heading3","heading4","heading5","heading6","bullet","ordered"):
            if key in b:
                txt = "".join(e.get("text_run",{}).get("content","") for e in b[key].get("elements",[]))
                if txt.strip():
                    items.append(txt)
    walk(resp.get("data",{}).get("block",{}))
    for child in resp.get("data",{}).get("block",{}).get("children",[]):
        if isinstance(child, dict) and "block_id" in child:
            cid = child["block_id"]
            cresp = api("GET", f"/docx/v1/documents/{doc_id}/blocks/{cid}")
            walk(cresp.get("data",{}).get("block",{}))
    return "\n".join(items)

# ============================================================
# Parse tasks from document text
# ============================================================
def parse_tasks(text):
    """Parse three sections, return {pending:[], progress:[], completed:[]}"""
    result = {"pending": [], "progress": [], "completed": []}
    current = None
    for line in text.split("\n"):
        line = line.strip()
        if "待完成任务" in line:
            current = "pending"
        elif "当前进度" in line:
            current = "progress"
        elif "已完成" in line:
            current = "completed"
        elif line.startswith("- ") and current:
            result[current].append(line[2:])
    return result

# ============================================================
# Append execution log entry
# ============================================================
def append_log(original, plan, result_detail, remaining):
    """Append a record to the execution log doc."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    blocks = [
        {"block_type":22,"divider":{}},
        mb(5,[te(f"⏱ {now}",b=True)]),
        mb(12,[te(f"【原记录】{original}")]),
        mb(12,[te(f"【执行方案】{plan}")]),
        mb(12,[te(f"【执行结果】{result_detail}")]),
        mb(12,[te(f"【待完成】{remaining}")]),
    ]
    add_blocks(LOG_DOC_ID, blocks)
    return f"Log appended at {now}"

# ============================================================
# Update task sections (replace entire section content)
# ============================================================
def update_tasks(pending, progress, completed):
    """
    Update all three sections in the task doc.
    Each param is a list of task strings.
    This clears existing blocks inside each section and writes new ones.
    """
    new_blocks = []
    for tasks, section_name in [(pending,"待完成任务"),(progress,"当前进度"),(completed,"已完成")]:
        new_blocks.append({"block_type":22,"divider":{}})
        new_blocks.append(mb(3,[te(f"✅ {section_name}",b=True)]))
        if tasks:
            for t in tasks:
                new_blocks.append(mb(12,[te(t)]))
        else:
            new_blocks.append(mb(2,[te("（空）")]))
    
    # Delete all children of root, then add new blocks
    resp = api("GET", f"/docx/v1/documents/{TASK_DOC_ID}/blocks/{TASK_DOC_ID}")
    existing = resp.get("data",{}).get("block",{}).get("children",[])
    for child in existing:
        cid = child.get("block_id") or (child if isinstance(child,str) else None)
        if cid:
            api("DELETE", f"/docx/v1/documents/{TASK_DOC_ID}/blocks/{TASK_DOC_ID}/children/batch",
                json.dumps({"start_index":0,"end_index":len(existing)}).encode())
            break
    
    add_blocks(TASK_DOC_ID, new_blocks)
    return "Tasks updated"

# ============================================================
# CLI
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "read_tasks":
        text = read_doc_text(TASK_DOC_ID)
        tasks = parse_tasks(text)
        print(json.dumps(tasks, ensure_ascii=False))
    
    elif cmd == "append_log":
        if len(sys.argv) < 6:
            print("Usage: ... append_log <original> <plan> <result> <remaining>")
            sys.exit(1)
        result = append_log(*sys.argv[2:6])
        print(result)
    
    elif cmd == "update_tasks":
        if len(sys.argv) < 5:
            print("Usage: ... update_tasks '[task1]' '[]' '[task1 (time)]'")
            sys.exit(1)
        result = update_tasks(json.loads(sys.argv[2]), json.loads(sys.argv[3]), json.loads(sys.argv[4]))
        print(result)
    
    elif cmd == "grant_permission":
        doc_id = sys.argv[2] if len(sys.argv) > 2 else TASK_DOC_ID
        uid = sys.argv[3] if len(sys.argv) > 3 else USER_OPEN_ID
        data = json.dumps({"member_type":"openid","member_id":uid,"perm":"edit"}).encode()
        u = f"https://open.feishu.cn/open-apis/drive/v1/permissions/{doc_id}/members?type=docx&need_notification=false"
        r = json.loads(urllib.request.urlopen(urllib.request.Request(u,data=data,headers={
            "Authorization":f"Bearer {T()}","Content-Type":"application/json"},method="POST")).read())
        print(f"Permission: {'✅' if r.get('code')==0 else '❌'} {r.get('msg','')}")
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
