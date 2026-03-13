---
name: feishu-docx-add-permisson
description: |
  调用飞书HTTP 服务，为新版文档(docx)批量增加用户协作者，授予可管理权限。
---
# 飞书新版文档批量增加协作者权限

为指定的新版文档(docx)批量添加用户协作者，并授予**可管理**权限。

## 接口信息

| 项目     | 值                                                                                    |
| -------- | ------------------------------------------------------------------------------------- |
| URL      | `https://open.feishu.cn/open-apis/drive/v1/permissions/:token/members/batch_create` |
| Method   | POST                                                                                  |
| 频率限制 | 100 次/分钟                                                                           |

## 前提条件

- 调用身份需要有该文档添加协作者的权限
- 调用身份与被授权用户需**互相可见**（联系人或同组织内可搜索，且互相未屏蔽）

## 请求参数

### 请求头

| 名称          | 类型   | 必填 | 说明                                        |
| ------------- | ------ | ---- | ------------------------------------------- |
| Authorization | string | 是   | `Bearer {tenant_access_token}`            |
| Content-Type  | string | 是   | 固定值：`application/json; charset=utf-8` |

### 路径参数

| 名称  | 类型   | 说明                            |
| ----- | ------ | ------------------------------- |
| token | string | 新版文档的 token（document_id） |

### 查询参数

| 名称              | 类型    | 必填 | 说明                                   |
| ----------------- | ------- | ---- | -------------------------------------- |
| type              | string  | 是   | **固定值：`docx`**（新版文档） |
| need_notification | boolean | 是   | 添加权限后是否通知对方，固定为 true    |

### 请求体

| 名称                  | 类型   | 必填 | 说明                                            |
| --------------------- | ------ | ---- | ----------------------------------------------- |
| members               | array  | 是   | 协作者列表，最多 10 个                          |
| members[].member_type | string | 是   | **固定值：`openid`**                    |
| members[].member_id   | string | 是   | 用户的 Open ID                                  |
| members[].perm        | string | 是   | **固定值：`full_access`**（可管理权限） |
| members[].type        | string | 是   | **固定值：`user`**                      |

### 请求体示例

```json
{
    "members": [
        {
            "member_type": "openid",
            "member_id": "ou_1234567890abcdef1234567890abcdef",
            "perm": "full_access",
            "type": "user"
        }
    ]
}
```

## 响应

### 响应体示例

```json
{
    "code": 0,
    "msg": "success",
    "data": {
        "members": [
            {
                "member_type": "openid",
                "member_id": "ou_1234567890abcdef1234567890abcdef",
                "perm": "full_access",
                "type": "user"
            }
        ]
    }
}
```

### 常见错误码

| HTTP状态码 | 错误码  | 描述     | 排查建议                                     |
| ---------- | ------- | -------- | -------------------------------------------- |
| 400        | 1063001 | 参数异常 | 检查 token 是否正确、用户 openid 是否有效    |
| 403        | 1063002 | 权限不足 | 为应用或用户添加文档协作者权限               |
| 400        | 1063003 | 非法操作 | 检查是否超过协作者数量上限、双方是否互相可见 |
| 429        | 1063006 | 请求频繁 | 稍后重试                                     |
| 500        | 1066001 | 内部错误 | 联系技术支持                                 |
