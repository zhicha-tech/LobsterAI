---
name: email-send
description: |
  通过SMTP协议发送邮件，支持QQ邮箱和163邮箱。当用户需要发送邮件、群发邮件、带附件邮件时使用此skill。
  支持纯文本和HTML格式邮件，支持抄送、密送和多附件发送。
  触发场景：发送邮件、发邮件、邮件通知、带附件发邮件、群发邮件。
---

# 邮件发送 Skill

通过SMTP协议发送邮件，支持QQ邮箱和163邮箱。

## 配置

SMTP凭据从 `~/.lawclaw.json` 配置文件读取，格式如下：

```json
{
  "email": {
    "qq": {
      "account": "your@qq.com",
      "smtp_password": "授权码"
    },
    "163": {
      "account": "your@163.com",
      "smtp_password": "授权码"
    }
  }
}
```

## 使用方式

### QQ邮箱

```python
python scripts/qq.py -t recipient@example.com -s "邮件主题" -c "邮件内容"
```

### 163邮箱

```python
python scripts/net_easy_163.py -t recipient@example.com -s "邮件主题" -c "邮件内容"
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `-t, --to` | 收件人地址（必填，支持多个） |
| `-s, --subject` | 邮件主题（必填） |
| `-c, --content` | 邮件内容（必填） |
| `--html` | 内容为HTML格式 |
| `-a, --attachments` | 附件文件路径（支持多个） |
| `--cc` | 抄送地址（支持多个） |
| `--bcc` | 密送地址（支持多个） |
| `--from-name` | 发件人显示名称 |

## 示例

### 发送简单邮件

```bash
python scripts/qq.py -t user@example.com -s "测试邮件" -c "这是一封测试邮件"
```

### 发送HTML邮件

```bash
python scripts/qq.py -t user@example.com -s "HTML邮件" -c "<h1>标题</h1><p>内容</p>" --html
```

### 发送带附件的邮件

```bash
python scripts/qq.py -t user@example.com -s "带附件" -c "请查收附件" -a ./file1.pdf ./file2.docx
```

### 发送给多个收件人并抄送

```bash
python scripts/qq.py -t user1@example.com user2@example.com -s "通知" -c "内容" --cc boss@example.com
```

## 代码调用

也可以在Python代码中直接调用：

```python
from scripts.qq import send_email

# 发送简单邮件
send_email(
    to_addrs="recipient@example.com",
    subject="邮件主题",
    content="邮件内容"
)

# 发送带附件的HTML邮件
send_email(
    to_addrs=["user1@example.com", "user2@example.com"],
    subject="报告",
    content="<h1>月度报告</h1><p>详情见附件</p>",
    content_type="html",
    attachments=["./report.pdf"],
    cc=["manager@example.com"],
    from_name="系统通知"
)
```
