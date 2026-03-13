---
name: aliyun-oss
description: 阿里云OSS文件上传和删除工具。当用户需要上传文件到OSS或从OSS删除文件时使用此skill。支持禁止覆盖同名文件的上传选项。配置信息从用户目录/.lawclaw.json文件读取。
---
# 阿里云OSS 文件上传/删除工具

本Skill提供阿里云OSS的简单文件上传和删除功能。

## 功能

1. **上传文件** - 将本地文件上传到OSS
2. **删除文件** - 从OSS删除指定文件

## 前置要求

1. 安装依赖:

```bash
pip install alibabacloud-oss-v2
```

2. 配置文件 (`~/.lawclaw.json`):

```json
{
  "cloudPlatform": {
    "alicloud": {
      "oss": {
        "access_key_id": "your-access-key-id",
        "access_key_secret": "your-access-key-secret",
        "region": "oss-cn-hangzhou",
        "bucket": "your-bucket-name"
      }
    }
  }
}
```

或简化格式：

```json
{
  "oss": {
    "access_key_id": "your-access-key-id",
    "access_key_secret": "your-access-key-secret",
    "region": "oss-cn-hangzhou",
    "bucket": "your-bucket-name"
  }
}
```

## 使用方法

### 1. 上传文件

**适用场景**: 用户需要上传文件到OSS，如 "上传文件到OSS"、"把本地文件传到OSS"、"将文件存到阿里云存储"

**执行脚本**:

```bash
python scripts/upload.py <本地文件路径> <OSS对象名称> [选项]
```

**参数说明**:

- `本地文件路径` - 要上传的本地文件完整路径（支持Windows路径如 `D:\path\file.txt`）
- `OSS对象名称` - OSS中的文件路径，如 `folder/file.txt`
- `--no-overwrite` - 可选，禁止覆盖同名文件

**示例**:

```bash
# 基本上传
python scripts/upload.py ./example.txt example.txt

# Windows路径
python scripts/upload.py D:\files\example.txt example.txt

# 上传到指定目录
python scripts/upload.py ./photo.jpg images/photo.jpg

# 禁止覆盖同名文件
python scripts/upload.py ./important.txt important.txt --no-overwrite
```

**代码示例**:

```python
from alibabacloud_oss_v2 import Client
from alibabacloud_oss_v2.config import Config
from alibabacloud_oss_v2.credentials import StaticCredentialsProvider
from alibabacloud_oss_v2.models import PutObjectRequest

# 创建客户端
credentials_provider = StaticCredentialsProvider(
    access_key_id='your-access-key-id',
    access_key_secret='your-access-key-secret',
)
cfg = Config(
    region='cn-hangzhou',  # 注意：不要带 oss- 前缀
    credentials_provider=credentials_provider,
)
client = Client(cfg)

# 上传文件（带禁止覆盖选项）
with open('local_file.txt', 'rb') as f:
    request = PutObjectRequest(
        bucket='your-bucket-name',
        key='remote_file.txt',
        body=f,
        forbid_overwrite='true',  # 禁止覆盖
    )
    client.put_object(request)
```

### 2. 删除文件

**适用场景**: 用户需要删除OSS上的文件，如 "删除OSS文件"、"从OSS删掉某个文件"

**执行脚本**:

```bash
python scripts/delete.py <OSS对象名称>
```

**参数说明**:

- `OSS对象名称` - 要删除的OSS文件路径，如 `folder/file.txt`

**示例**:

```bash
# 删除根目录文件
python scripts/delete.py example.txt

# 删除指定目录文件
python scripts/delete.py "images/photo.jpg"
```

**代码示例**:

```python
from alibabacloud_oss_v2 import Client
from alibabacloud_oss_v2.config import Config
from alibabacloud_oss_v2.credentials import StaticCredentialsProvider
from alibabacloud_oss_v2.models import DeleteObjectRequest

# 创建客户端
credentials_provider = StaticCredentialsProvider(
    access_key_id='your-access-key-id',
    access_key_secret='your-access-key-secret',
)
cfg = Config(
    region='cn-hangzhou',  # 注意：不要带 oss- 前缀
    credentials_provider=credentials_provider,
)
client = Client(cfg)

# 删除文件
request = DeleteObjectRequest(
    bucket='your-bucket-name',
    key='exampleobject.txt',
)
client.delete_object(request)
```

## 用户意图判断

当用户提到以下内容时，触发相应操作：

| 用户意图关键词                  | 执行操作           |
| ------------------------------- | ------------------ |
| 上传、传到、存入、发送文件到OSS | 使用 `upload.py` |
| 删除、移除、清理OSS文件         | 使用 `delete.py` |

## 配置文件说明

配置文件路径: `~/.lawclaw.json` (用户目录下的 .lawclaw.json 文件)

支持两种配置路径：
- `cloudPlatform.alicloud.oss.*` (推荐)
- `oss.*` (简化格式)

| 字段名            | 说明           | 示例                     |
| ----------------- | -------------- | ------------------------ |
| access_key_id     | AccessKey ID   | LTAI5tAhEHKdmDhSaA5b9r4r |
| access_key_secret | AccessKey Secret | xxxxxxxxxxxxxx         |
| region            | Bucket所在地域 | oss-cn-hangzhou          |
| bucket            | Bucket名称     | my-bucket                |

## 常见地域列表

- `oss-cn-hangzhou` - 华东1（杭州）
- `oss-cn-shanghai` - 华东2（上海）
- `oss-cn-beijing` - 华北1（北京）
- `oss-cn-shenzhen` - 华南1（深圳）
- `oss-cn-wulanchabu` - 华北5（乌兰察布）

## 错误处理

常见错误码:

- `NoSuchKey` - 文件不存在（删除时）
- `FileAlreadyExists` - 文件已存在（上传时使用了禁止覆盖选项）
- `InvalidAccessKeyId` - AccessKey ID无效
- `SignatureDoesNotMatch` - AccessKey Secret错误
