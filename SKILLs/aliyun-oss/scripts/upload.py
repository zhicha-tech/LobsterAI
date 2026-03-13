#!/usr/bin/env python3
"""
OSS文件上传脚本
用法: python upload.py <本地文件路径> <OSS对象名称> [选项]

示例:
  python upload.py ./examplefile.txt exampleobject.txt
  python upload.py ./examplefile.txt exampleobject.txt --no-overwrite
"""

import argparse
import os
import sys
from pathlib import Path

# 添加脚本目录到路径以便导入 config 模块
sys.path.insert(0, str(Path(__file__).parent))

from config import create_oss_client, get_object_url, load_oss_config
from alibabacloud_oss_v2.models import PutObjectRequest


def upload_file(local_path: str, object_name: str, overwrite: bool = True):
    """上传文件到 OSS"""
    config = load_oss_config()
    if not config:
        sys.exit(1)

    # 规范化本地文件路径
    local_path = os.path.normpath(local_path)

    # 检查本地文件是否存在
    if not os.path.exists(local_path):
        print(f"错误: 本地文件不存在: {local_path}")
        sys.exit(1)

    # 创建 OSS 客户端
    client = create_oss_client(config)

    # 准备 forbid_overwrite 参数
    forbid_overwrite = None if overwrite else "true"
    if not overwrite:
        print(f"正在上传: {local_path} -> oss://{config['bucket']}/{object_name} (禁止覆盖)")
    else:
        print(f"正在上传: {local_path} -> oss://{config['bucket']}/{object_name}")

    try:
        with open(local_path, "rb") as f:
            request = PutObjectRequest(
                bucket=config["bucket"],
                key=object_name,
                body=f,
                forbid_overwrite=forbid_overwrite,
            )
            result = client.put_object(request)

        print("上传成功!")
        print(f"  对象名称: {object_name}")
        print(f"  状态码: {result.status_code}")
        print(f"  ETag: {result.etag}")
        print(f"  URL: {get_object_url(config, object_name)}")

        return result

    except Exception as e:
        error_msg = str(e)
        if "FileAlreadyExists" in error_msg or "Precondition Failed" in error_msg:
            print("上传失败: 文件已存在 (使用 --no-overwrite 禁止覆盖同名文件)")
        else:
            print(f"上传失败: {error_msg}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="上传文件到阿里云 OSS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python upload.py ./example.txt example.txt
  python upload.py D:\\files\\example.txt example.txt
  python upload.py ./photo.jpg images/photo.jpg
  python upload.py ./important.txt important.txt --no-overwrite
"""
    )

    parser.add_argument("local_path", help="要上传的本地文件路径")
    parser.add_argument("object_name", help="OSS 中的对象名称")
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="禁止覆盖同名文件"
    )

    args = parser.parse_args()

    upload_file(args.local_path, args.object_name, overwrite=not args.no_overwrite)


if __name__ == "__main__":
    main()
