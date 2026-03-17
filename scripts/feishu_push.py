#!/usr/bin/env python3
"""
飞书推送模块
Feishu Push Module

支持两种推送方式：
1. 群 Webhook 推送
2. 私聊消息推送（需要 Open ID）
"""
import os
import sys
import json
import requests
from pathlib import Path

class FeishuPusher:
    """飞书推送客户端"""

    def __init__(self, app_id=None, app_secret=None):
        """
        初始化

        Args:
            app_id: 飞书应用 ID（可选，从环境变量读取）
            app_secret: 飞书应用密钥（可选，从环境变量读取）
        """
        self.app_id = app_id or os.environ.get('FEISHU_APP_ID')
        self.app_secret = app_secret or os.environ.get('FEISHU_APP_SECRET')
        self.webhook_url = os.environ.get('FEISHU_WEBHOOK')
        self.user_open_id = os.environ.get('FEISHU_USER_OPEN_ID')
        self._token = None

    def get_tenant_access_token(self):
        """获取 tenant_access_token"""
        if not self.app_id or not self.app_secret:
            return None

        if self._token:
            return self._token

        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()

            if result.get("code") == 0:
                self._token = result.get("tenant_access_token")
                return self._token
            else:
                print(f"❌ 获取 token 失败: {result}", file=sys.stderr)
                return None
        except Exception as e:
            print(f"❌ 网络错误: {e}", file=sys.stderr)
            return None

    def push_to_webhook(self, message):
        """
        推送到飞书群（Webhook）

        Args:
            message: 消息文本

        Returns:
            bool: 是否成功
        """
        if not self.webhook_url:
            return False

        data = {
            "msg_type": "text",
            "content": {
                "text": message
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                json=data,
                timeout=10
            )
            result = response.json()

            if result.get("code") == 0:
                print("✅ 消息已推送到飞书群", file=sys.stderr)
                return True
            else:
                print(f"❌ Webhook 推送失败: {result}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"❌ Webhook 推送错误: {e}", file=sys.stderr)
            return False

    def push_to_user(self, message, open_id=None):
        """
        推送到飞书私聊

        Args:
            message: 消息文本
            open_id: 用户 Open ID（可选，默认使用环境变量）

        Returns:
            bool: 是否成功
        """
        target_open_id = open_id or self.user_open_id

        if not target_open_id:
            return False

        token = self.get_tenant_access_token()
        if not token:
            return False

        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        params = {
            "receive_id_type": "open_id"
        }

        data = {
            "receive_id": target_open_id,
            "msg_type": "text",
            "content": json.dumps({
                "text": message
            })
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                params=params,
                timeout=10
            )
            result = response.json()

            if result.get("code") == 0:
                print("✅ 消息已发送到飞书私聊", file=sys.stderr)
                return True
            else:
                print(f"❌ 私聊推送失败: {result}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"❌ 私聊推送错误: {e}", file=sys.stderr)
            return False

    def push(self, message):
        """
        智能推送（自动选择可用的推送方式）

        推送优先级：
        1. 飞书私聊（如果配置了 Open ID）
        2. 飞书群 Webhook（如果配置了 Webhook URL）

        Args:
            message: 消息文本

        Returns:
            bool: 至少一种方式推送成功
        """
        success = False

        # 尝试私聊推送
        if self.user_open_id and self.app_id and self.app_secret:
            if self.push_to_user(message):
                success = True

        # 尝试 Webhook 推送
        if self.webhook_url:
            if self.push_to_webhook(message):
                success = True

        if not success:
            print("⚠️ 未配置飞书推送，跳过", file=sys.stderr)

        return success


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='飞书推送工具')
    parser.add_argument('message', nargs='?', help='要推送的消息（留空则从 stdin 读取）')
    parser.add_argument('--webhook', action='store_true', help='只使用 Webhook 推送')
    parser.add_argument('--user', action='store_true', help='只使用私聊推送')
    parser.add_argument('--open-id', help='目标用户 Open ID')

    args = parser.parse_args()

    # 读取消息
    message = args.message
    if not message:
        message = sys.stdin.read().strip()

    if not message:
        print("❌ 消息内容为空", file=sys.stderr)
        sys.exit(1)

    # 创建推送客户端
    pusher = FeishuPusher()

    # 选择推送方式
    if args.webhook:
        success = pusher.push_to_webhook(message)
    elif args.user:
        success = pusher.push_to_user(message, args.open_id)
    else:
        success = pusher.push(message)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
