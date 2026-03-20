#!/usr/bin/env python3
"""
163邮箱SMTP发送邮件脚本
支持文本邮件和HTML邮件，支持附件发送
支持隐私发送模式（多收件人时分别发送，互不可见）
"""

import smtplib
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
from pathlib import Path
from typing import Optional, List, Union

# 163邮箱SMTP配置
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465  # SSL端口

# 配置文件路径
CONFIG_PATH = Path.home() / ".lawclaw.json"


def load_config() -> dict:
    """加载配置文件"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_smtp_credentials() -> tuple:
    """从配置文件获取SMTP凭据"""
    config = load_config()
    email_config = config.get('email', {}).get('163', {})
    account = email_config.get('account', '')
    password = email_config.get('smtp_password', '')
    return account, password


def _build_message(
    to_addr: str,
    subject: str,
    content: str,
    content_type: str,
    attachments: Optional[List[str]],
    from_name: Optional[str],
    from_addr: str,
    cc: Optional[List[str]] = None
) -> MIMEMultipart:
    """构建邮件消息"""
    msg = MIMEMultipart()

    sender = formataddr((from_name or '', from_addr)) if from_name else from_addr
    msg['From'] = sender
    msg['To'] = to_addr
    msg['Subject'] = subject

    if cc:
        msg['Cc'] = ', '.join(cc)

    msg.attach(MIMEText(content, content_type, 'utf-8'))

    if attachments:
        for attachment_path in attachments:
            if not os.path.exists(attachment_path):
                print(f"警告: 附件不存在: {attachment_path}")
                continue

            with open(attachment_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)

                filename = os.path.basename(attachment_path)
                part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=('utf-8', '', filename)
                )
                msg.attach(part)

    return msg


def send_email(
    to_addrs: Union[str, List[str]],
    subject: str,
    content: str,
    content_type: str = "plain",
    attachments: Optional[List[str]] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    from_name: Optional[str] = None,
    from_addr: Optional[str] = None,
    password: Optional[str] = None,
    private: bool = True
) -> bool:
    """
    发送邮件

    Args:
        to_addrs: 收件人地址，可以是字符串或列表
        subject: 邮件主题
        content: 邮件内容
        content_type: 内容类型，"plain" 或 "html"
        attachments: 附件文件路径列表
        cc: 抄送地址列表
        bcc: 密送地址列表
        from_name: 发件人名称
        from_addr: 发件人地址（可选，默认从配置读取）
        password: SMTP密码（可选，默认从配置读取）
        private: 隐私模式，True时多收件人分别发送（互不可见），False时群发

    Returns:
        bool: 发送成功返回True，失败返回False
    """
    try:
        # 获取凭据
        if not from_addr or not password:
            config_addr, config_pwd = get_smtp_credentials()
            from_addr = from_addr or config_addr
            password = password or config_pwd

        if not from_addr or not password:
            raise ValueError("未找到SMTP凭据，请检查配置文件或提供参数")

        # 处理收件人地址
        if isinstance(to_addrs, str):
            to_addrs = [to_addrs]

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(from_addr, password)

            if private and len(to_addrs) > 1:
                # 隐私模式：分别发送给每个收件人
                success_count = 0
                for addr in to_addrs:
                    msg = _build_message(
                        to_addr=addr,
                        subject=subject,
                        content=content,
                        content_type=content_type,
                        attachments=attachments,
                        from_name=from_name,
                        from_addr=from_addr,
                        cc=cc
                    )
                    recipients = [addr]
                    if cc:
                        recipients.extend(cc)
                    if bcc:
                        recipients.extend(bcc)
                    server.sendmail(from_addr, recipients, msg.as_string())
                    success_count += 1
                    print(f"已发送至: {addr}")

                print(f"邮件发送成功: {subject} (共{success_count}位收件人)")
            else:
                # 普通模式：群发
                msg = _build_message(
                    to_addr=', '.join(to_addrs),
                    subject=subject,
                    content=content,
                    content_type=content_type,
                    attachments=attachments,
                    from_name=from_name,
                    from_addr=from_addr,
                    cc=cc
                )

                recipients = list(to_addrs)
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)

                server.sendmail(from_addr, recipients, msg.as_string())
                print(f"邮件发送成功: {subject}")

        return True

    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='163邮箱SMTP发送邮件')
    parser.add_argument('-t', '--to', required=True, nargs='+', help='收件人地址')
    parser.add_argument('-s', '--subject', required=True, help='邮件主题')
    parser.add_argument('-c', '--content', required=True, help='邮件内容')
    parser.add_argument('--html', action='store_true', help='内容为HTML格式')
    parser.add_argument('-a', '--attachments', nargs='*', help='附件文件路径')
    parser.add_argument('--cc', nargs='*', help='抄送地址')
    parser.add_argument('--bcc', nargs='*', help='密送地址')
    parser.add_argument('--from-name', help='发件人名称')
    parser.add_argument('--group', action='store_true', help='群发模式（收件人可见彼此邮箱）')
    parser.add_argument('--private', action='store_true', default=True, help='隐私模式（默认开启，收件人互不可见）')

    args = parser.parse_args()

    # 如果指定了 --group，则关闭隐私模式
    private_mode = not args.group

    success = send_email(
        to_addrs=args.to,
        subject=args.subject,
        content=args.content,
        content_type='html' if args.html else 'plain',
        attachments=args.attachments,
        cc=args.cc,
        bcc=args.bcc,
        from_name=args.from_name,
        private=private_mode
    )

    exit(0 if success else 1)


if __name__ == '__main__':
    main()
