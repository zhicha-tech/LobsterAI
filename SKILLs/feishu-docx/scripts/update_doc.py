#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新飞书文档内容脚本
用法: python update_doc.py --doc-id "文档ID" --content "内容" --mode append
"""

import sys
import os
import argparse
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_mcp_client import FeishuMCPClient
from config import get_feishu_credentials


def update_document(doc_id: str, content: str, mode: str = 'append') -> dict:
    """
    更新飞书文档内容

    Args:
        doc_id: 文档 ID
        content: 文档内容（Markdown 格式）
        mode: 更新模式，append（追加）或 overwrite（覆盖）

    Returns:
        操作结果字典
    """
    app_id, app_secret, _ = get_feishu_credentials()

    if not app_id or not app_secret:
        return {"success": False, "error": "未配置飞书凭证"}

    client = FeishuMCPClient(app_id=app_id, app_secret=app_secret)

    if not client.initialize():
        return {"success": False, "error": "MCP 初始化失败"}

    result = client.call_tool(
        tool_name='update-doc',
        arguments={
            'docID': doc_id,
            'markdown': content,
            'mode': mode
        },
        allowed_tools=['update-doc']
    )

    if result:
        return {"success": True, "data": result}
    else:
        return {"success": False, "error": "更新文档失败"}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='更新飞书文档内容')
    parser.add_argument('--doc-id', '-d', type=str, required=True, help='文档 ID')
    parser.add_argument('--content', '-c', type=str, help='文档内容（Markdown 格式）')
    parser.add_argument('--file', '-f', type=str, help='从文件读取内容')
    parser.add_argument('--mode', '-m', type=str, default='append',
                        choices=['append', 'overwrite'], help='更新模式: append(追加) 或 overwrite(覆盖)')
    parser.add_argument('--json', '-j', action='store_true', help='以 JSON 格式输出')

    args = parser.parse_args()

    # 获取内容
    content = args.content
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
        except IOError as e:
            print(f"❌ 文件读取失败: {e}")
            sys.exit(1)

    if not content:
        print("❌ 请通过 --content 或 --file 提供文档内容")
        sys.exit(1)

    result = update_document(args.doc_id, content, args.mode)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result['success']:
            print(f"✅ 文档更新成功!")
            data = result.get('data', {})
            if 'url' in data:
                print(f"   URL: {data['url']}")
        else:
            print(f"❌ {result['error']}")
            sys.exit(1)
