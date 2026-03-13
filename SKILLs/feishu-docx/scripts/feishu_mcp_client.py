#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书 MCP 客户端（HTTP 远程调用版）
严格遵循飞书 MCP 协议规范，通过 HTTP 请求调用远程 MCP 服务
"""

import requests
import json
from typing import Optional, Dict, List, Any


class FeishuMCPClient:
    """
    飞书 MCP 协议客户端
    通过 HTTP 请求调用 https://mcp.feishu.cn/mcp 服务
    """

    def __init__(self, app_id: str = None, app_secret: str = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.mcp_endpoint = "https://mcp.feishu.cn/mcp"
        self.auth_endpoint = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        self.request_id = 0
        self.available_tools = []

    def get_access_token(self) -> str:
        """
        获取 tenant_access_token
        有效期 2 小时，剩余 30 分钟内重新获取会返回新 token
        """
        if self.access_token:
            return self.access_token

        if not self.app_id or not self.app_secret:
            raise ValueError("未配置 app_id 和 app_secret")

        try:
            response = requests.post(
                self.auth_endpoint,
                headers={'Content-Type': 'application/json; charset=utf-8'},
                json={
                    "app_id": self.app_id,
                    "app_secret": self.app_secret
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            if result.get('code') != 0:
                raise Exception(f"获取 token 失败: {result.get('msg')}")

            self.access_token = result['tenant_access_token']
            expire = result.get('expire', 7200)
            print(f"✅ 成功获取访问令牌（有效期 {expire} 秒）")

            return self.access_token

        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {e}")

    def _make_mcp_request(self, method: str, params: dict = None,
                          allowed_tools: List[str] = None) -> Optional[Dict]:
        """
        发送 MCP HTTP 请求

        Args:
            method: MCP 方法 (initialize, tools/list, tools/call)
            params: 请求参数
            allowed_tools: 允许的工具列表
        """
        try:
            token = self.get_access_token()

            # 构建请求头
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'X-Lark-MCP-TAT': token
            }

            # 添加允许的工具列表
            if allowed_tools:
                headers['X-Lark-MCP-Allowed-Tools'] = ','.join(allowed_tools)

            # 构建请求体 (JSON-RPC 2.0)
            self.request_id += 1
            body = {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "method": method
            }

            if params:
                body["params"] = params

            # 发送请求
            response = requests.post(
                self.mcp_endpoint,
                headers=headers,
                json=body,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()

            # 检查错误
            if 'error' in result:
                error_code = result['error'].get('code')
                error_msg = result['error'].get('message', '未知错误')
                print(f"❌ MCP 请求失败 [{error_code}]: {error_msg}")
                return None

            return result.get('result')

        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP 错误: {e.response.status_code}")
            print(f"   响应: {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}")
            return None

    def initialize(self) -> bool:
        """
        初始化 MCP 连接
        方法: initialize
        """
        print("\n🔄 正在初始化 MCP 连接...")

        result = self._make_mcp_request("initialize")

        if result:
            server_info = result.get('serverInfo', {})
            protocol_version = result.get('protocolVersion', 'unknown')
            print(f"✅ MCP 初始化成功")
            print(f"   协议版本: {protocol_version}")
            print(f"   服务端: {server_info.get('name', 'Unknown')} v{server_info.get('version', 'Unknown')}")
            return True
        else:
            print("❌ MCP 初始化失败")
            return False

    def list_tools(self, allowed_tools: List[str] = None) -> List[Dict]:
        """
        列出可用的 MCP 工具
        方法: tools/list

        Args:
            allowed_tools: 允许的工具列表，如 ['create-doc', 'fetch-doc']
        """
        print("\n📋 获取可用工具列表...")

        result = self._make_mcp_request(
            method="tools/list",
            allowed_tools=allowed_tools
        )

        if result and 'tools' in result:
            tools = result['tools']
            self.available_tools = tools

            print(f"✅ 发现 {len(tools)} 个可用工具:")
            print()
            for i, tool in enumerate(tools, 1):
                name = tool.get('name', 'Unknown')
                desc = tool.get('description', '无描述')
                # 截断过长的描述
                if len(desc) > 60:
                    desc = desc[:60] + "..."
                print(f"{i}. {name}")
                print(f"   描述: {desc}")
                print()

            return tools
        else:
            print("⚠️ 没有获取到可用工具")
            return []

    def call_tool(self, tool_name: str, arguments: Dict[str, Any],
                  allowed_tools: List[str] = None) -> Optional[Dict]:
        """
        调用 MCP 工具
        方法: tools/call

        Args:
            tool_name: 工具名称，如 'create-doc'
            arguments: 工具参数
            allowed_tools: 允许的工具列表（必须包含 tool_name）
        """
        print(f"\n🔧 调用工具: {tool_name}")
        print(f"📦 参数: {json.dumps(arguments, ensure_ascii=False, indent=2)}")

        # 确保工具在允许列表中
        if allowed_tools:
            if tool_name not in allowed_tools:
                allowed_tools = allowed_tools + [tool_name]
        else:
            allowed_tools = [tool_name]

        # 构建参数
        params = {
            "name": tool_name,
            "arguments": arguments
        }

        result = self._make_mcp_request(
            method="tools/call",
            params=params,
            allowed_tools=allowed_tools
        )

        if result:
            # 检查结果是否包含错误
            if result.get('isError'):
                content = result.get('content', [])
                if content and len(content) > 0:
                    error_text = content[0].get('text', '{}')
                    try:
                        error_json = json.loads(error_text)
                        error_detail = error_json.get('error', '未知错误')
                        print(f"⚠️ 工具执行返回错误: {error_detail}")
                        return None
                    except:
                        print(f"⚠️ 工具执行返回错误: {error_text}")
                        return None

            # 解析成功结果
            content = result.get('content', [])
            if content and len(content) > 0:
                text = content[0].get('text', '{}')
                try:
                    data = json.loads(text)
                    return data
                except:
                    return {'text': text}
        else:
            print("❌ 工具调用失败")

        return None

    def verify_credentials(self) -> bool:
        """
        验证凭证是否有效
        通过尝试 initialize 来验证
        """
        try:
            return self.initialize()
        except Exception as e:
            print(f"❌ 凭证验证失败: {e}")
            return False


if __name__ == '__main__':
    import os
    import argparse

    parser = argparse.ArgumentParser(description='飞书 MCP 客户端命令行工具')
    parser.add_argument('--tool', '-t', type=str, help='要调用的工具名称，如 create-doc、fetch-doc')
    parser.add_argument('--args', '-a', type=str, help='工具参数，JSON 格式字符串，如 \'{"title": "文档标题"}\'')
    parser.add_argument('--list-tools', '-l', action='store_true', help='列出所有可用工具')
    parser.add_argument('--allowed-tools', type=str, help='允许的工具列表，逗号分隔，如 create-doc,fetch-doc')

    args = parser.parse_args()

    app_id = os.environ.get('FEISHU_APP_ID')
    app_secret = os.environ.get('FEISHU_APP_SECRET')

    if not app_id or not app_secret:
        print("❌ 请设置环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET")
        exit(1)

    client = FeishuMCPClient(app_id=app_id, app_secret=app_secret)

    # 初始化连接
    if not client.initialize():
        print("❌ MCP 初始化失败")
        exit(1)

    # 解析允许的工具列表
    allowed_tools = None
    if args.allowed_tools:
        allowed_tools = [t.strip() for t in args.allowed_tools.split(',')]

    # 列出工具
    if args.list_tools:
        client.list_tools(allowed_tools)
        exit(0)

    # 调用工具
    if args.tool:
        # 解析参数
        tool_args = {}
        if args.args:
            try:
                tool_args = json.loads(args.args)
            except json.JSONDecodeError as e:
                print(f"❌ 参数 JSON 解析失败: {e}")
                print(f"   请确保参数是有效的 JSON 格式，如: '{{\"title\": \"文档标题\"}}'")
                exit(1)

        # 调用工具
        result = client.call_tool(args.tool, tool_args, allowed_tools)

        if result:
            print("\n✅ 工具调用成功")
            print("="*80)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("="*80)
        else:
            print("❌ 工具调用失败")
            exit(1)
        exit(0)

    # 无参数时显示帮助信息
    parser.print_help()
