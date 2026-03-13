#!/usr/bin/env python3
"""
OSS文件删除脚本
用法: python delete.py <OSS对象名称>

示例:
  python delete.py exampleobject.txt
  python delete.py "path/to/file.txt"
"""

import argparse
import sys
from pathlib import Path

# 添加脚本目录到路径以便导入 config 模块
sys.path.insert(0, str(Path(__file__).parent))

from config import create_oss_client, load_oss_config
from alibabacloud_oss_v2.models import DeleteObjectRequest


def delete_object(object_name: str):
    """从 OSS 删除文件"""
    config = load_oss_config()
    if not config:
        sys.exit(1)

    # 创建 OSS 客户端
    client = create_oss_client(config)

    print(f"正在删除: oss://{config['bucket']}/{object_name}")

    try:
        request = DeleteObjectRequest(
            bucket=config["bucket"],
            key=object_name,
        )
        result = client.delete_object(request)

        print("删除成功!")
        print(f"  对象名称: {object_name}")
        print(f"  状态码: {result.status_code}")

        return result

    except Exception as e:
        error_msg = str(e)
        if "NoSuchKey" in error_msg:
            print("删除失败: 文件不存在")
        else:
            print(f"删除失败: {error_msg}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="从阿里云 OSS 删除文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python delete.py example.txt
  python delete.py "images/photo.jpg"
"""
    )

    parser.add_argument("object_name", help="要删除的 OSS 对象名称")

    args = parser.parse_args()

    delete_object(args.object_name)


if __name__ == "__main__":
    main()
