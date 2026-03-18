#!/usr/bin/env python3
"""
律师朋友圈获客图 - 问题管理脚本

用于管理问题列表的读取和进度更新。
配置文件: ~/.lawclaw.json
问题文件: 由配置中的 lawyerWechatLead.questionsFilePath 指定
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def get_config_path() -> Path:
    """获取配置文件路径，兼容不同操作系统"""
    return Path.home() / ".lawclaw.json"


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    config_path = get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    # 支持 UTF-8 和 UTF-8 with BOM
    with config_path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_lawyer_wechat_lead_config() -> Dict[str, Any]:
    """加载 lawyerWechatLead 配置"""
    config = load_config()
    lawyer_wechat_lead = config.get("lawyerWechatLead", {})
    if not lawyer_wechat_lead:
        raise ValueError("配置文件中未找到 lawyerWechatLead 配置")
    return lawyer_wechat_lead


def save_config(config: Dict[str, Any]) -> None:
    """保存配置文件"""
    config_path = get_config_path()
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def get_questions_file_path(config: Dict[str, Any]) -> Path:
    """获取问题文件路径，兼容不同操作系统"""
    raw_path = config.get("lawyerWechatLead", {}).get("questionsFilePath", "")
    if not raw_path:
        raise ValueError("配置中未找到 lawyerWechatLead.questionsFilePath")

    # 展开 ~ 为用户目录，兼容不同操作系统
    return Path(raw_path).expanduser()


def parse_questions(file_path: Path) -> List[str]:
    """
    解析问题文件

    支持格式:
    1. 问题内容
    2. 问题内容
    ...
    """
    if not file_path.exists():
        raise FileNotFoundError(f"问题文件不存在: {file_path}")

    content = file_path.read_text(encoding="utf-8")
    questions: List[str] = []

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        # 匹配 "1. 问题内容" 格式
        match = re.match(r'^(\d+)\.\s*(.+)$', line)
        if match:
            questions.append(match.group(2).strip())

    return questions


def get_next_run_num(config: Dict[str, Any]) -> int:
    """获取下一个要运行的问题序号"""
    return config.get("lawyerWechatLead", {}).get("nextRunNum", 1)


def set_next_run_num(config: Dict[str, Any], value: int) -> None:
    """设置下一个要运行的问题序号"""
    if "lawyerWechatLead" not in config:
        config["lawyerWechatLead"] = {}
    config["lawyerWechatLead"]["nextRunNum"] = value


def cmd_get_current() -> Dict[str, Any]:
    """
    获取当前问题信息

    返回:
    - valid: 是否有效（未超出边界）
    - question: 当前问题内容
    - index: 当前序号（从1开始）
    - total: 问题总数
    - message: 提示信息（仅在无效时）
    """
    try:
        config = load_config()
        questions_path = get_questions_file_path(config)
        questions = parse_questions(questions_path)
        next_run_num = get_next_run_num(config)
        total = len(questions)

        if total == 0:
            return {
                "valid": False,
                "message": "问题列表为空，请添加问题",
                "index": next_run_num,
                "total": 0
            }

        # 边界检查：超出索引
        if next_run_num > total:
            # 重置为1
            set_next_run_num(config, 1)
            save_config(config)
            return {
                "valid": False,
                "message": f"已完成所有 {total} 个问题，请更新问题列表",
                "index": next_run_num,
                "total": total
            }

        # 返回当前问题
        question = questions[next_run_num - 1]
        return {
            "valid": True,
            "question": question,
            "index": next_run_num,
            "total": total
        }

    except FileNotFoundError as e:
        return {"valid": False, "message": str(e)}
    except ValueError as e:
        return {"valid": False, "message": str(e)}
    except Exception as e:
        return {"valid": False, "message": f"发生错误: {e}"}


def cmd_advance() -> Dict[str, Any]:
    """
    推进到下一个问题（在生成成功后调用）

    返回:
    - success: 是否成功
    - new_index: 新的序号
    - message: 提示信息
    """
    try:
        config = load_config()
        questions_path = get_questions_file_path(config)
        questions = parse_questions(questions_path)
        current_num = get_next_run_num(config)
        total = len(questions)

        new_index = current_num + 1

        # 如果超出边界，重置为1
        if new_index > total:
            new_index = 1

        set_next_run_num(config, new_index)
        save_config(config)

        return {
            "success": True,
            "new_index": new_index,
            "message": f"已更新序号: {current_num} -> {new_index}"
        }

    except Exception as e:
        return {"success": False, "message": f"发生错误: {e}"}


def cmd_reset() -> Dict[str, Any]:
    """
    重置序号为1

    返回:
    - success: 是否成功
    - new_index: 新的序号（总是1）
    - message: 提示信息
    """
    try:
        config = load_config()
        set_next_run_num(config, 1)
        save_config(config)

        return {
            "success": True,
            "new_index": 1,
            "message": "已重置序号为 1"
        }

    except Exception as e:
        return {"success": False, "message": f"发生错误: {e}"}


def cmd_status() -> Dict[str, Any]:
    """
    获取当前状态（不检查边界）

    返回:
    - config_path: 配置文件路径
    - questions_path: 问题文件路径
    - next_run_num: 当前序号
    - total: 问题总数
    - questions: 问题列表预览（前5个）
    """
    try:
        config = load_config()
        questions_path = get_questions_file_path(config)
        questions = parse_questions(questions_path)
        next_run_num = get_next_run_num(config)

        return {
            "config_path": str(get_config_path()),
            "questions_path": str(questions_path),
            "next_run_num": next_run_num,
            "total": len(questions),
            "questions_preview": questions[:5]
        }

    except Exception as e:
        return {"error": str(e)}


def cmd_get_config() -> Dict[str, Any]:
    """
    获取完整的 lawyerWechatLead 配置

    返回:
    - lawyer: 律师信息
    - brand: 品牌风格
    - compliance: 合规配置
    - models: 模型配置
    - questionsFilePath: 问题文件路径
    - nextRunNum: 当前序号
    """
    try:
        config = load_lawyer_wechat_lead_config()
        # 过滤掉敏感信息（如果有）
        result = {
            "lawyer": config.get("lawyer", {}),
            "brand": config.get("brand", {}),
            "compliance": config.get("compliance", {}),
            "models": config.get("models", {}),
            "questionsFilePath": config.get("questionsFilePath", ""),
            "nextRunNum": config.get("nextRunNum", 1)
        }
        return result
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="律师朋友圈获客图 - 问题管理脚本"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--get-current",
        action="store_true",
        help="获取当前问题信息"
    )
    group.add_argument(
        "--advance",
        action="store_true",
        help="推进到下一个问题（生成成功后调用）"
    )
    group.add_argument(
        "--reset",
        action="store_true",
        help="重置序号为1"
    )
    group.add_argument(
        "--status",
        action="store_true",
        help="获取当前状态"
    )
    group.add_argument(
        "--get-config",
        action="store_true",
        help="获取完整的 lawyerWechatLead 配置"
    )

    args = parser.parse_args()

    result: Dict[str, Any]

    if args.get_current:
        result = cmd_get_current()
    elif args.advance:
        result = cmd_advance()
    elif args.reset:
        result = cmd_reset()
    elif args.status:
        result = cmd_status()
    elif args.get_config:
        result = cmd_get_config()
    else:
        result = {"error": "未指定操作"}

    # 输出 JSON 结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
