#!/usr/bin/env python3
"""
OSS 公共配置模块
"""

import json
import sys
from pathlib import Path

try:
    from alibabacloud_oss_v2 import Client
    from alibabacloud_oss_v2.config import Config
    from alibabacloud_oss_v2.credentials import StaticCredentialsProvider
except ImportError:
    print("错误: 缺少 alibabacloud-oss-v2 依赖")
    print("请运行: pip install alibabacloud-oss-v2")
    sys.exit(1)


def load_oss_config():
    """从 ~/.lawclaw.json 加载 OSS 配置

    支持两种配置路径：
    1. oss.access_key_id, oss.access_key_secret, oss.region, oss.bucket
    2. cloudPlatform.alicloud.oss.access_key_id 等

    Returns:
        dict: OSS 配置字典，包含 access_key_id, access_key_secret, region, bucket
    """
    config_path = Path.home() / ".lawclaw.json"

    if not config_path.exists():
        print(f"错误: 配置文件不存在: {config_path}")
        print("请在用户目录下创建 .lawclaw.json 文件，包含 OSS 配置")
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"错误: 配置文件格式错误: {e}")
        return None

    # 获取 OSS 配置（支持两种配置路径）
    oss_config = (
        config.get("oss")
        or config.get("cloudPlatform", {}).get("alicloud", {}).get("oss", {})
    )

    if not oss_config:
        print("错误: 配置文件中缺少 'oss' 或 'cloudPlatform.alicloud.oss' 配置项")
        return None

    required_keys = ["access_key_id", "access_key_secret", "region", "bucket"]
    missing_keys = [k for k in required_keys if k not in oss_config]

    if missing_keys:
        print(f"错误: OSS 配置缺少必要的字段: {', '.join(missing_keys)}")
        return None

    return oss_config


def normalize_region(region: str) -> str:
    """规范化 region 格式

    支持两种格式：
    - oss-cn-hangzhou (带 oss- 前缀)
    - cn-hangzhou (不带前缀)

    Returns:
        不带 oss- 前缀的 region
    """
    if region.startswith("oss-"):
        return region[4:]
    return region


def create_oss_client(config: dict) -> Client:
    """创建 OSS 客户端

    Args:
        config: OSS 配置字典

    Returns:
        OSS Client 实例
    """
    region = normalize_region(config["region"])

    credentials_provider = StaticCredentialsProvider(
        access_key_id=config["access_key_id"],
        access_key_secret=config["access_key_secret"],
    )

    cfg = Config(
        region=region,
        credentials_provider=credentials_provider,
    )

    return Client(cfg)


def get_object_url(config: dict, object_name: str) -> str:
    """生成对象访问 URL

    Args:
        config: OSS 配置字典
        object_name: 对象名称

    Returns:
        访问 URL
    """
    # URL 中使用带 oss- 前缀的完整 region
    region = config["region"]
    if not region.startswith("oss-"):
        region = f"oss-{region}"

    return f"https://{config['bucket']}.{region}.aliyuncs.com/{object_name}"
