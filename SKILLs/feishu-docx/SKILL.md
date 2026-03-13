---
name: feishu-docx
description: |
  调用飞书 MCP HTTP 服务，实现云文档的创建、查看、更新等功能。
  适用场景：创建飞书文档、读取文档内容、更新文档。
---

# 飞书 MCP 文档助手

通过 **MCP HTTP 协议** 调用飞书官方 MCP 服务，管理云文档。

## 工作流程

```
配置验证 → 创建/列出文档 → 写入内容 → 添加权限 → 返回结果
```

## 快速命令

所有脚本位于 `scripts/` 目录下，需先进入 SKILL 目录：

```bash
cd {当前文件所在目录}
```

### 1. 验证配置

```bash
python scripts/list_tools.py
```

### 2. 创建文档

```bash
python scripts/create_doc.py --title "文档标题"
# 或使用短参数
python scripts/create_doc.py -t "文档标题"
# JSON 输出
python scripts/create_doc.py -t "文档标题" -j
```

### 3. 获取文档内容

```bash
python scripts/fetch_doc.py --doc-id "文档ID"
# 或
python scripts/fetch_doc.py -d "文档ID"
```

### 4. 更新文档内容

```bash
# 追加内容（默认）
python scripts/update_doc.py -d "文档ID" -c "Markdown 内容"

# 覆盖内容
python scripts/update_doc.py -d "文档ID" -c "内容" --mode overwrite

# 从文件读取内容
python scripts/update_doc.py -d "文档ID" -f content.md
```

### 5. 列出文档

```bash
# 列出"我的文档库"中的文档
python scripts/list_docs.py

# 指定返回数量
python scripts/list_docs.py -p 10

# JSON 输出
python scripts/list_docs.py -j
```

### 6. 添加文档权限

```bash
# 使用配置文件中的 openUserId
python scripts/add_permission.py -d "文档ID"

# 指定用户的 openId
python scripts/add_permission.py -d "文档ID" -o "ou_xxxx"

# 不通知用户
python scripts/add_permission.py -d "文档ID" --no-notify
```

## 配置管理

### 配置文件位置

`用户目录/.lawclaw.json`

### 配置格式

```json
{
  "channels": {
    "feishu": {
      "appId": "cli_xxxx",
      "appSecret": "xxxx",
      "openUserId": "ou_xxxx"
    }
  }
}
```

### 获取凭证

在 [飞书开放平台](https://open.feishu.cn/app) 创建自建应用，获取：
- **App ID**: `cli_xxxxxx`
- **App Secret**: `xxxxxxxx`
- **Open User ID**: 用户标识（用于添加权限）

## 支持的工具

| 工具名 | 功能 | 对应脚本 |
|--------|------|----------|
| `create-doc` | 创建云文档 | `create_doc.py` |
| `fetch-doc` | 获取文档内容 | `fetch_doc.py` |
| `update-doc` | 更新文档内容 | `update_doc.py` |
| `list-docs` | 列出我的文档库 | `list_docs.py` |
| `get-comments` | 获取文档评论 | - |
| `add-comments` | 添加文档评论 | - |
| 权限管理 | 添加协作者权限 | `add_permission.py` |

## 执行流程

### 场景：创建文档并写入内容

**注意**：
1. 创建文档和写入内容必须分两步执行。
2. 只要过程中创建了文档就必须添加用户权限

```bash
# 步骤 1: 创建空文档
python scripts/create_doc.py -t "会议纪要"
# 输出: Document ID: VZundx5z1oT4cqxwXdYcdZk7nvb

# 步骤 2: 写入内容
python scripts/update_doc.py -d "VZundx5z1oT4cqxwXdYcdZk7nvb" -c "
# 会议纪要

## 参会人员
- 张三
- 李四

## 讨论内容
...
"

# 步骤 3: 添加用户权限（**必须**）
python scripts/add_permission.py -d "VZundx5z1oT4cqxwXdYcdZk7nvb"
```

### 场景：查找并读取文档

```bash
# 列出我的文档库
python scripts/list_docs.py

# 读取文档内容
python scripts/fetch_doc.py -d "找到的文档ID"
```

## 通用 MCP 客户端

如需调用其他 MCP 工具，可使用通用客户端：

```bash
# 调用任意工具
python scripts/feishu_mcp_client.py --tool create-doc --args '{"title": "文档标题"}'

# 列出所有工具
python scripts/feishu_mcp_client.py --list-tools

# 使用短参数
python scripts/feishu_mcp_client.py -t update-doc -a '{"docID": "xxx", "markdown": "内容", "mode": "append"}'
```

## 故障排除

### 调用脚本时出现参数错误
使用 `scripts/list_tools` 列出工具的所需要的参数，进行比对修正

### MCP 初始化失败 (404)

```
❌ HTTP 错误: 404
```

**解决方案**：
- 检查网络连接
- 确认 App ID 和 App Secret 正确
- 稍后重试

### 权限不足

```
⚠️ 工具执行返回错误: [PERMISSION_DENIED]
```

**解决方案**：
在飞书开放平台为应用添加相应权限

### 添加权限失败 (1063002)

```
❌ 错误码: 1063002, 错误信息: Permission denied
```

**解决方案**：
- 确保应用有文档协作者权限
- 确保调用身份与被授权用户互相可见

## 文件结构

```
feishu-docx/
├── skill.md                      # 本文档
├── references/
│   └── add-permission.md         # 权限 API 参考
└── scripts/
    ├── config.py                 # 配置管理模块
    ├── feishu_mcp_client.py      # MCP HTTP 客户端（通用）
    ├── list_tools.py             # 验证配置、列出工具
    ├── create_doc.py             # 创建文档
    ├── fetch_doc.py              # 获取文档内容
    ├── update_doc.py             # 更新文档内容
    ├── list_docs.py              # 列出我的文档库
    └── add_permission.py         # 添加协作者权限
```

## 技术栈

- **协议**: MCP (Model Context Protocol) over HTTP
- **认证**: tenant_access_token
- **端点**: https://mcp.feishu.cn/mcp
- **数据格式**: JSON-RPC 2.0
- **依赖**: Python 3.7+, requests

## 参考文档

- **飞书 MCP 文档**: https://open.feishu.cn/document/mcp
- **MCP 协议规范**: https://modelcontextprotocol.io
