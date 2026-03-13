---
name: ocr-extractor
description: 文档 OCR 文本提取工具，使用 MinerU 平台从 PDF、Word、PPT 文件中提取文本内容。当用户需要提取文档内容、识别扫描件文字、获取 PDF/Word/PPT 中的文本时使用此 skill。工作流程：1) 使用 aliyun-oss skill 上传文件获取 URL；2) 调用 MinerU API 提交 OCR 任务并轮询获取结果；3) 识别完成后使用 aliyun-oss skill 删除临时文件。
---
# OCR 文本提取工具

本 Skill 基于 MinerU 平台提供完整的文档 OCR 文本提取流程，支持 PDF、Word、PPT 等格式的文件内容提取。

## 工作流程

```
用户请求提取文档内容
    ↓
使用 aliyun-oss skill 上传文件到 OSS
    ↓
获取文件 URL
    ↓
提交 MinerU OCR 任务 → 轮询查询任务状态
    ↓
返回提取的文本内容
    ↓
使用 aliyun-oss skill 删除临时文件
```

## 前置要求

### 1. 环境变量配置

**使用 .lawclaw.json 配置文件**

在用户目录下创建 `.lawclaw.json` 文件：

```json
{
  "cloudPlatform":{
    "mineru": {
      "api_token": "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ..."
    }
  }
}
```

- Windows: `C:\Users\{用户名}\.lawclaw.json`
- macOS/Linux: `~/.lawclaw.json`

**阿里云 OSS 配置**（由 aliyun-oss skill 读取）：

```
access_key_id=your-access-key-id
access_key_secret=your-access-key-secret
region=oss-cn-hangzhou
bucket=your-bucket-name
```

### 2. 依赖

- aliyun-oss skill（用于文件上传和删除）
- Node.js（用于执行 OCR 脚本）

## 使用方法

### 提取文档内容

**适用场景**: 用户需要提取 PDF、Word、PPT 文件的文本内容，如 "提取这个 PDF 的内容"、"识别这份合同的文字"、"把 PPT 内容转成文字"

**执行步骤**:

1. **上传文件到 OSS**

   - 使用 `aliyun-oss` skill 上传文件
   - 获取文件的 OSS URL
2. **执行 OCR 识别**

   - 脚本会自动从 `用户目录/.lawclaw.json` 文件读取 `cloudPlatform.mineru.api_token`
   - 提交任务后自动轮询等待结果
   - 返回提取的文本内容
3. **删除临时文件**

   - 使用 `aliyun-oss` skill 删除 OSS 上的临时文件

**完整示例**:

```bash
# 1. 使用 aliyun-oss skill 上传文件（获取 URL）
# 上传文件并记录返回的 URL

# 2. 执行 OCR（脚本自动读取 .env 文件中的 YOUR_MINERU_TOKEN）
node scripts/ocr_extract.js "https://your-bucket.oss-region.aliyuncs.com/filename.pdf"

# 3. 使用 aliyun-oss skill 删除文件
node ../aliyun-oss/scripts/delete.js "filename.pdf"
```

## API 说明

使用 MinerU 文档解析 API 进行文档识别：

### 提交任务

- **API 地址**: `POST https://mineru.net/api/v4/extract/task`
- **请求头**:
  - `Authorization: Bearer {YOUR_MINERU_TOKEN}`
  - `Content-Type: application/json`
- **请求体**:

```json
{
  "url": "https://example.com/file.pdf",
  "model_version": "vlm"
}
```

### 查询任务

- **API 地址**: `GET https://mineru.net/api/v4/extract/task/{task_id}`
- **请求头**: `Authorization: Bearer {YOUR_MINERU_TOKEN}`

### 任务状态

- `PENDING` - 等待处理
- `PROGRESS` - 正在处理
- `SUCCESS` - 处理成功
- `FAILURE` - 处理失败

脚本会自动轮询查询任务状态，直到任务完成或超时（默认最大等待 5 分钟）。

## 支持的文件格式

- **PDF** - `.pdf`
- **Word** - `.doc`, `.docx`
- **PPT** - `.ppt`, `.pptx`
- **图片** - `.png`, `.jpg`, `.jpeg`

## 错误处理

常见错误及解决方法：

| 错误                | 原因                      | 解决方法                                                            |
| ------------------- | ------------------------- | ------------------------------------------------------------------- |
| 请配置 MinerU Token | API Token 未配置          | 检查 `~/.lawclaw.json` 中的 `cloudPlatform.mineru.api_token`                   |
| 提交任务失败 (401)  | Token 无效                | 检查 Token 是否正确，从 https://mineru.net/apiManage/token 重新获取 |
| 提交任务失败 (400)  | 文件格式不支持或 URL 无效 | 检查文件 URL 是否可访问                                             |
| 任务执行失败        | 文件处理出错              | 检查文件内容是否有效或损坏                                          |
| 任务超时            | 处理时间过长              | 大文件可能需要更长时间，请耐心等待                                  |

## 注意事项

1. **临时文件清理**: OCR 识别完成后务必删除 OSS 上的临时文件，避免占用存储空间
2. **轮询机制**: 脚本会自动轮询任务状态，每 5 秒查询一次，最多等待 60 次（5 分钟）
3. **大文件处理**: 对于大型文档，OCR 识别可能需要较长时间，请耐心等待
4. **URL 有效期**: 确保文件 URL 在 OCR 识别期间有效
5. **API Token 安全**: 请妥善保管 YOUR_MINERU_TOKEN，不要泄露给他人
