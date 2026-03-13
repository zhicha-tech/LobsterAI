#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出飞书文档库中的文档
用法: python list_docs.py [--my-library] [--doc-id "文档ID"]
"""

import sys
import os
import argparse
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_mcp_client import FeishuMCPClient
from config import get_feishu_credentials


def list_documents(my_library: bool = True, doc_id: str = None, page_size: int = 20) -> dict:
    """
    列出飞书文档

    Args:
        my_library: 是否查询"我的文档库"
        doc_id: Wiki 文档 ID（当 my_library=False 时必填）
        page_size: 每页返回数量（1-50）

    Returns:
        文档列表字典
    """
    app_id, app_secret, _ = get_feishu_credentials()

    if not app_id or not app_secret:
        return {"success": False, "error": "未配置飞书凭证"}

    if not my_library and not doc_id:
        return {"success": False, "error": "查询指定文档时必须提供 doc_id"}

    client = FeishuMCPClient(app_id=app_id, app_secret=app_secret)

    if not client.initialize():
        return {"success": False, "error": "MCP 初始化失败"}

    arguments = {
        'my_library': my_library,
        'page_size': min(page_size, 50)
    }

    if doc_id:
        arguments['doc_id'] = doc_id

    result = client.call_tool(
        tool_name='list-docs',
        arguments=arguments,
        allowed_tools=['list-docs']
    )

    if result:
        return {"success": True, "data": result}
    else:
        return {"success": False, "error": "获取文档列表失败"}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='列出飞书文档')
    parser.add_argument('--my-library', '-m', action='store_true', default=True,
                        help='查询"我的文档库"（默认）')
    parser.add_argument('--doc-id', '-d', type=str, help='Wiki 文档 ID（查询指定文档的子文档）')
    parser.add_argument('--page-size', '-p', type=int, default=20, help='每页返回数量（1-50）')
    parser.add_argument('--json', '-j', action='store_true', help='以 JSON 格式输出')

    args = parser.parse_args()

    # 如果指定了 doc_id，则不使用 my_library
    my_library = not bool(args.doc_id)

    result = list_documents(my_library=my_library, doc_id=args.doc_id, page_size=args.page_size)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result['success']:
            data = result['data']
            nodes = data.get('nodes', [])
            has_more = data.get('has_more', False)
            print(f"✅ 找到 {len(nodes)} 个文档{'（还有更多）' if has_more else ''}:")
            print()
            for i, node in enumerate(nodes, 1):
                title = node.get('title', '无标题')
                url = node.get('url', '')
                has_child = node.get('has_child', False)
                print(f"{i}. {title}")
                if url:
                    print(f"   URL: {url}")
                if has_child:
                    print(f"   📁 包含子文档")
                print()
        else:
            print(f"❌ {result['error']}")
            sys.exit(1)
