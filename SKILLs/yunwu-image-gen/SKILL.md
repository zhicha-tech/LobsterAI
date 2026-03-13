---
name: yunwu-image-gen
description: 调用 yunwu.ai 的 Gemini API 生成图片。当用户需要生成图片、创建图像、文生图、AI绘图、生成公众号封面图时使用此 skill。支持自定义提示词生成图像，以及从文章标题或 Markdown 内容自动生成封面图。支持控制宽高比(1:1, 16:9, 9:16, 4:3, 3:4)和清晰度(1K, 2K, 4K)。
---
# Yunwu Image Generation

调用 yunwu.ai 的 Gemini API 进行图像生成。支持控制宽高比和图像清晰度。

## 工作流程

```
配置验证 → 构建提示词 → 调用 API → 保存图片 → 返回结果
```

## 前置要求

### 1. 配置文件

在 `用户目录下/ .lawclaw.json` 文件：

```json
{
  "cloudPlatform": {
    "yunwu": {
      "apiKey": "your-api-key"
    }
  }
}
```

- Windows: `C:\Users\{用户名}\.lawclaw.json`
- macOS/Linux: `~/.lawclaw.json`

### 2. 依赖

- Node.js 环境

## 快速命令

所有脚本位于 `scripts/` 目录下，需先进入 SKILL 目录：

```bash
cd {当前文件所在目录}
```

### 1. 生成图片

```bash
node scripts/generate_image.js generate "提示词" [输出路径] [宽高比] [清晰度]

# 示例
node scripts/generate_image.js generate "一只可爱的猫咪在草地上玩耍"
node scripts/generate_image.js generate "一只可爱的猫咪在草地上玩耍" output.png
node scripts/generate_image.js generate "一只可爱的猫咪在草地上玩耍" output.png 16:9
node scripts/generate_image.js generate "一只可爱的猫咪在草地上玩耍" output.png 16:9 2K
```

### 2. 生成公众号封面图

```bash
node scripts/generate_image.js cover "文章标题" [输出路径] [封面比例] [清晰度]

# 示例
node scripts/generate_image.js cover "10个提高工作效率的技巧"
node scripts/generate_image.js cover "10个提高工作效率的技巧" cover.png
node scripts/generate_image.js cover "10个提高工作效率的技巧" cover.png 2.35:1
node scripts/generate_image.js cover "10个提高工作效率的技巧" cover.png 2.35:1 2K
```

### 3. 查看支持的参数

```bash
# 查看支持的宽高比
node scripts/generate_image.js ratios

# 查看支持的图像大小
node scripts/generate_image.js sizes

# 查看帮助
node scripts/generate_image.js
```

## 参数说明

### 宽高比 (aspectRatio)

| 值       | 说明         |
| -------- | ------------ |
| `1:1`  | 正方形       |
| `16:9` | 横版宽屏     |
| `9:16` | 竖版（默认） |
| `4:3`  | 传统横版     |
| `3:4`  | 传统竖版     |

### 封面比例 (ratio)

| 值         | 映射到   | 说明               |
| ---------- | -------- | ------------------ |
| `2.35:1` | `16:9` | 电影宽银幕（默认） |
| `21:9`   | `16:9` | 超宽屏             |
| `16:9`   | `16:9` | 标准宽屏           |
| `9:16`   | `9:16` | 竖版               |
| `4:3`    | `4:3`  | 传统比例           |
| `3:4`    | `3:4`  | 传统竖版           |
| `1:1`    | `1:1`  | 正方形             |

### 图像清晰度 (imageSize)

| 值     | 说明                            |
| ------ | ------------------------------- |
| `1K` | 标准清晰度（默认用于 generate） |
| `2K` | 高清晰度（默认用于 cover）      |
| `4K` | 超高清                          |

## 使用场景

### 场景 1: 生成 AI 艺术图

```bash
node scripts/generate_image.js generate "赛博朋克风格的城市夜景，霓虹灯闪烁" art.png 16:9 2K
```

### 场景 2: 生成公众号封面

```bash
node scripts/generate_image.js cover "2024年最值得学习的10个AI工具" cover.png 2.35:1 2K
```

### 场景 3: 生成社交媒体配图

```bash
node scripts/generate_image.js generate "清新的早晨，阳光透过窗帘" social.png 1:1 1K
```

### 场景 4: 生成竖版海报

```bash
node scripts/generate_image.js generate "春节快乐，龙年大吉，红色喜庆背景" poster.png 9:16 2K
```

## 错误处理

| 错误                                          | 原因           | 解决方法                                                     |
| --------------------------------------------- | -------------- | ------------------------------------------------------------ |
| YUNWU_API_KEY environment variable is not set | API Key 未配置 | 检查 `~/.lawclaw.json` 中的 `cloudPlatform.yunwu.apiKey` |
| Failed to generate image                      | API 调用失败   | 检查网络连接和 API Key 有效性                                |
| No image generated from API                   | API 未返回图像 | 尝试修改提示词                                               |

## Resources

### scripts/

- `generate_image.js` - 图像生成的主要脚本

## API 端点

- **基础 URL**: `https://yunwu.ai/`
- **端点**: `v1beta/models/gemini-3-pro-image-preview:generateContent`
- **方法**: POST
- **认证**: Bearer Token (API Key)
