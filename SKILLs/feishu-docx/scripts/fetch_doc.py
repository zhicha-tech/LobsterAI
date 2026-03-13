#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取飞书文档内容脚本
用法: python fetch_doc.py --doc-id "文档ID"
"""

import sys
import os
import argparse
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_mcp_client import FeishuMCPClient
from config import get_feishu_credentials


def fetch_document(doc_id: str) -> dict:
    """
    获取飞书文档内容

    Args:
        doc_id: 文档 ID

    Returns:
        包含文档内容的字典
    """
    app_id, app_secret, _ = get_feishu_credentials()

    if not app_id or not app_secret:
        return {"success": False, "error": "未配置飞书凭证"}

    client = FeishuMCPClient(app_id=app_id, app_secret=app_secret)

    if not client.initialize():
        return {"success": False, "error": "MCP 初始化失败"}

    result = client.call_tool(
        tool_name='fetch-doc',
        arguments={'docID': doc_id},
        allowed_tools=['fetch-doc']
    )

    if result:
        return {"success": True, "data": result}
    else:
        return {"success": False, "error": "获取文档失败"}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='获取飞书文档内容')
    parser.add_argument('--doc-id', '-d', type=str, required=True, help='文档 ID')
    parser.add_argument('--json', '-j', action='store_true', help='以 JSON 格式输出')

    args = parser.parse_args()

    result = fetch_document(args.doc_id)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result['success']:
            data = result['data']
            print(f"✅ 文档内容获取成功!")
            if 'content' in data:
                print("\n" + "="*60)
                print(data['content'])
                print("="*60)
            elif 'markdown' in data:
                print("\n" + "="*60)
                print(data['markdown'])
                print("="*60)
            else:
                print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"❌ {result['error']}")
            sys.exit(1)
