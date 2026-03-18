---
name: lawyer-wechat-lead-images
description: 律师朋友圈获客图生成。从配置文件读取问题列表，按序号逐个生成专业营销海报。触发场景：生成律师获客图、朋友圈营销素材、律师营销海报、律师朋友圈、执行回款图片、劳动用工图片。当用户需要为律师业务制作朋友圈营销图片时使用此 skill。
version: 1.0.0
---

# 律师朋友圈获客图生成

按序从问题列表获取问题，生成律师朋友圈获客营销海报。

## 工作流程

### Step 1: 获取当前问题

运行问题管理脚本获取当前要处理的问题：

```bash
python scripts/question_manager.py --get-current
```

输出示例：
```json
{
  "valid": true,
  "question": "判决生效后对方拖着不还钱，我现在第一步该做什么？",
  "index": 1,
  "total": 50
}
```

**边界检查**：若 `valid` 为 `false`，说明已完成所有问题：
```json
{
  "valid": false,
  "message": "已完成所有 50 个问题，请更新问题列表",
  "index": 51,
  "total": 50
}
```

此时脚本已自动将序号重置为 1，需要提示用户更新问题列表。

### Step 2: 生成图片

使用当前问题作为 topic 调用生成脚本：

```bash
python scripts/generate_wechat_lead_images.py \
  --topic "{问题内容}" \
  --count 1 \
  --skip-text-model
```

参数说明：
- `--topic`: 使用 Step 1 获取的问题内容
- `--count 1`: 每次只生成一张图片
- `--skip-text-model`: 使用模板模式（更快更稳定）

### Step 3: 更新进度

生成成功后，更新序号到下一个问题：

```bash
python scripts/question_manager.py --advance
```

输出示例：
```json
{
  "success": true,
  "new_index": 2,
  "message": "已更新序号: 1 -> 2"
}
```

## 配置说明

### 配置文件位置

所有配置统一存放在 `~/.lawclaw.json` 的 `lawyerWechatLead` 字段中：

```json
{
  "lawyerWechatLead": {
    "questionsFilePath": "~/Desktop/律师获客问题.txt",
    "nextRunNum": 1,
    "lawyer": {
      "name": "张律师",
      "title": "执业律师",
      "firm": "某某律师事务所",
      "wechat": "your_wechat"
    },
    "brand": {
      "primary_color": "#B30000",
      "visual_style": "clean legal poster for WeChat Moments"
    },
    "compliance": {
      "global_disclaimer": "本文仅作普法交流，不构成个案法律意见。"
    },
    "models": {
      "image": {
        "enabled": true,
        "provider": "gemini_generate_content",
        "endpoint": "https://yunwu.ai/v1beta/models/gemini-3-pro-image-preview:generateContent",
        "model": "gemini-3-pro-image-preview",
        "api_key_env": "IMAGE_API_KEY"
      }
    }
  }
}
```

### 配置字段说明

| 字段 | 说明 |
|------|------|
| `questionsFilePath` | 问题文件路径，支持 `~` 表示用户目录 |
| `nextRunNum` | 下一个要处理的问题序号（从 1 开始） |
| `lawyer` | 律师信息（姓名、头衔、律所、联系方式等） |
| `brand` | 品牌风格配置（颜色、视觉风格等） |
| `compliance` | 合规配置（免责声明、禁止用语等） |
| `models` | 模型配置（文本模型、图片生成模型） |

### 问题文件格式

问题文件为纯文本格式，每行一个问题：

```
1. 判决生效后对方拖着不还钱，我现在第一步该做什么？
2. 我知道对方有资产，但法院查不到，线索该怎么提才有效？
3. 案件被终本后还有机会追回吗？
...
```

## 输出文件

生成结果保存在 `output/时间戳-主题/` 目录：

```
output/20260318-154534-执行领域的高频问题/
├── cards.json          # 结构化数据
├── posts.md            # 朋友圈配文
├── prompts.txt         # 图片生成提示词
└── images/
    └── 01.png          # 生成的图片
```

## 辅助命令

```bash
# 查看当前状态
python scripts/question_manager.py --status

# 获取完整配置
python scripts/question_manager.py --get-config

# 重置序号为 1
python scripts/question_manager.py --reset
```

## 注意事项

1. **API Key 配置**：图片生成需要设置环境变量 `IMAGE_API_KEY`
2. **生成耗时**：每张图片约 10-30 秒
3. **合规声明**：所有图片自动生成免责声明，请勿删除
4. **问题更新**：完成所有问题后，更新问题文件即可继续使用
5. **脚本路径**：采用相对于当前模块的相对路径。如 scripts/generate_wechat_lead_images.py 指代当前文件同级目录下的 scripts 子文件夹中的目标文件。
