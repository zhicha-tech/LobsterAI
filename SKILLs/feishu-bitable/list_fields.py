#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取多维表格字段列表
"""

import requests
import json

# 飞书配置
APP_ID = "cli_a925788df1f99cd6"
APP_SECRET = "R9FXqSIoXLmRSzScOV1kecENLx00atkK"
APP_TOKEN = "Cxu9bMv5qaqp7xsrIrecuUCeneg"
TABLE_ID = "tblJE4bs9PT10eUX"

# 获取 access_token
def get_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": APP_ID, "app_secret": APP_SECRET}

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result.get('code') == 0:
        return result['tenant_access_token']
    else:
        raise Exception(f"获取 token 失败: {result}")


# 获取字段列表
def get_fields(access_token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    return response.json()


# 主函数
print('正在获取 access_token...')
access_token = get_access_token()
print('✅ 获取成功\n')

print('正在获取字段列表...')
result = get_fields(access_token)

if result.get('code') == 0:
    fields = result.get('data', {}).get('items', [])
    print(f'\n共 {len(fields)} 个字段:\n')
    print('=' * 80)
    for field in fields:
        field_id = field.get('field_id', '')
        field_name = field.get('field_name', '')
        field_type = field.get('type', 0)
        type_names = {1: '多行文本', 2: '数字', 3: '单选', 4: '多选', 5: '日期', 7: '复选框', 11: '人员', 13: '电话号码', 15: 'URL', 17: '附件', 18: '关联', 19: '公式', 20: '双向关联', 21: '位置', 22: '群组', 23: '条码', 1001: '创建时间', 1002: '修改时间', 1003: '创建人', 1004: '修改人', 1005: '自动编号'}
        type_name = type_names.get(field_type, f'类型{field_type}')
        print(f'{field_id}: {field_name} ({type_name})')
    print('=' * 80)

    # 保存字段信息
    with open('fields_info.json', 'w', encoding='utf-8') as f:
        json.dump(fields, f, ensure_ascii=False, indent=2)
    print(f'\n字段信息已保存到: fields_info.json')
else:
    print(f'获取失败: {result}')
