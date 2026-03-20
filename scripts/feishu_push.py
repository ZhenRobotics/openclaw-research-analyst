#!/usr/bin/env python3
"""
飞书推送模块
Feishu Push Module

支持两种推送方式：
1. 群 Webhook 推送
2. 私聊消息推送（需要 Open ID）

v1.2.1 优化:
- 添加详细返回值（message_id, timestamp, method）
- 网络请求重试机制（最多2次）
- 推送历史日志记录
"""
import os
import sys
import json
import requests
import time
from pathlib import Path
from datetime import datetime

# Load Feishu configuration from .env.feishu
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / '.env.feishu'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass  # dotenv not installed, will use existing env vars

class FeishuPusher:
    """飞书推送客户端"""

    def __init__(self, app_id=None, app_secret=None, enable_logging=True):
        """
        初始化

        Args:
            app_id: 飞书应用 ID（可选，从环境变量读取）
            app_secret: 飞书应用密钥（可选，从环境变量读取）
            enable_logging: 是否启用推送历史日志
        """
        self.app_id = app_id or os.environ.get('FEISHU_APP_ID')
        self.app_secret = app_secret or os.environ.get('FEISHU_APP_SECRET')
        self.webhook_url = os.environ.get('FEISHU_WEBHOOK')
        self.user_open_id = os.environ.get('FEISHU_USER_OPEN_ID')
        self._token = None
        self.enable_logging = enable_logging
        self.max_retries = 2

        # Setup log directory
        if self.enable_logging:
            script_dir = Path(__file__).parent.parent
            self.log_dir = script_dir / 'logs'
            self.log_dir.mkdir(exist_ok=True)
            self.log_file = self.log_dir / 'feishu_push_history.log'

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

    def _log_push(self, method, success, message, error=None, message_id=None):
        """记录推送历史"""
        if not self.enable_logging:
            return

        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            status = "SUCCESS" if success else "FAILED"

            log_entry = {
                'timestamp': timestamp,
                'method': method,
                'status': status,
                'message_length': len(message),
                'message_preview': message[:50] + '...' if len(message) > 50 else message,
                'message_id': message_id,
                'error': error
            }

            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"⚠️ 日志记录失败: {e}", file=sys.stderr)

    def _request_with_retry(self, method, url, **kwargs):
        """带重试的请求"""
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    wait_time = attempt * 1  # 1s, 2s
                    time.sleep(wait_time)
                    print(f"🔄 重试 {attempt}/{self.max_retries}...", file=sys.stderr)

                response = requests.request(method, url, timeout=10, **kwargs)
                return response, None
            except requests.exceptions.Timeout as e:
                last_error = f"Timeout: {e}"
            except requests.exceptions.ConnectionError as e:
                last_error = f"ConnectionError: {e}"
            except Exception as e:
                last_error = f"Error: {e}"

        return None, last_error

    def push_to_webhook(self, message):
        """
        推送到飞书群（Webhook）

        Args:
            message: 消息文本

        Returns:
            dict: {
                'success': bool,
                'method': 'webhook',
                'message_id': str or None,
                'timestamp': str,
                'error': str or None
            }
        """
        result = {
            'success': False,
            'method': 'webhook',
            'message_id': None,
            'timestamp': datetime.now().isoformat(),
            'error': None
        }

        if not self.webhook_url:
            result['error'] = 'Webhook URL not configured'
            self._log_push('webhook', False, message, error=result['error'])
            return result

        data = {
            "msg_type": "text",
            "content": {
                "text": message
            }
        }

        response, error = self._request_with_retry(
            'POST',
            self.webhook_url,
            headers={'Content-Type': 'application/json'},
            json=data
        )

        if error:
            result['error'] = error
            print(f"❌ Webhook 推送错误: {error}", file=sys.stderr)
            self._log_push('webhook', False, message, error=error)
            return result

        try:
            response_data = response.json()

            if response_data.get("code") == 0:
                result['success'] = True
                result['message_id'] = response_data.get('data', {}).get('message_id')
                print("✅ 消息已推送到飞书群", file=sys.stderr)
                self._log_push('webhook', True, message, message_id=result['message_id'])
            else:
                result['error'] = str(response_data)
                print(f"❌ Webhook 推送失败: {response_data}", file=sys.stderr)
                self._log_push('webhook', False, message, error=result['error'])
        except Exception as e:
            result['error'] = str(e)
            print(f"❌ Webhook 响应解析错误: {e}", file=sys.stderr)
            self._log_push('webhook', False, message, error=result['error'])

        return result

    def push_to_user(self, message, open_id=None):
        """
        推送到飞书私聊

        Args:
            message: 消息文本
            open_id: 用户 Open ID（可选，默认使用环境变量）

        Returns:
            dict: {
                'success': bool,
                'method': 'private_chat',
                'message_id': str or None,
                'timestamp': str,
                'error': str or None
            }
        """
        result = {
            'success': False,
            'method': 'private_chat',
            'message_id': None,
            'timestamp': datetime.now().isoformat(),
            'error': None
        }

        target_open_id = open_id or self.user_open_id

        if not target_open_id:
            result['error'] = 'User Open ID not configured'
            self._log_push('private_chat', False, message, error=result['error'])
            return result

        token = self.get_tenant_access_token()
        if not token:
            result['error'] = 'Failed to get access token'
            self._log_push('private_chat', False, message, error=result['error'])
            return result

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

        response, error = self._request_with_retry(
            'POST',
            url,
            headers=headers,
            json=data,
            params=params
        )

        if error:
            result['error'] = error
            print(f"❌ 私聊推送错误: {error}", file=sys.stderr)
            self._log_push('private_chat', False, message, error=error)
            return result

        try:
            response_data = response.json()

            if response_data.get("code") == 0:
                result['success'] = True
                result['message_id'] = response_data.get('data', {}).get('message_id')
                print("✅ 消息已发送到飞书私聊", file=sys.stderr)
                self._log_push('private_chat', True, message, message_id=result['message_id'])
            else:
                result['error'] = str(response_data)
                print(f"❌ 私聊推送失败: {response_data}", file=sys.stderr)
                self._log_push('private_chat', False, message, error=result['error'])
        except Exception as e:
            result['error'] = str(e)
            print(f"❌ 私聊响应解析错误: {e}", file=sys.stderr)
            self._log_push('private_chat', False, message, error=result['error'])

        return result

    def push(self, message):
        """
        智能推送（自动选择可用的推送方式）

        推送优先级：
        1. 飞书私聊（如果配置了 Open ID）
        2. 飞书群 Webhook（如果配置了 Webhook URL）

        Args:
            message: 消息文本

        Returns:
            dict: {
                'success': bool,
                'results': list of dict (每个推送方式的详细结果),
                'message_ids': list of str (成功推送的消息ID)
            }
        """
        results = []
        message_ids = []

        # 尝试私聊推送
        if self.user_open_id and self.app_id and self.app_secret:
            result = self.push_to_user(message)
            results.append(result)
            if result['success'] and result['message_id']:
                message_ids.append(result['message_id'])

        # 尝试 Webhook 推送
        if self.webhook_url:
            result = self.push_to_webhook(message)
            results.append(result)
            if result['success'] and result['message_id']:
                message_ids.append(result['message_id'])

        success = any(r['success'] for r in results)

        if not success and not results:
            print("⚠️ 未配置飞书推送，跳过", file=sys.stderr)

        return {
            'success': success,
            'results': results,
            'message_ids': message_ids
        }


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
        result = pusher.push_to_webhook(message)
        success = result['success']
    elif args.user:
        result = pusher.push_to_user(message, args.open_id)
        success = result['success']
    else:
        result = pusher.push(message)
        success = result['success']

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
