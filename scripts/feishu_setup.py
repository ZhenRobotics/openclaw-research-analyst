#!/usr/bin/env python3
"""
飞书推送配置向导
Feishu Push Setup Wizard
"""
import os
import sys
import requests
import argparse
from pathlib import Path


def get_tenant_access_token(app_id, app_secret):
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {
        "app_id": app_id,
        "app_secret": app_secret
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()

        if result.get("code") != 0:
            print(f"❌ 获取 token 失败: {result}")
            return None

        print("✅ 成功获取 tenant_access_token")
        return result.get("tenant_access_token")
    except Exception as e:
        print(f"❌ 网络错误: {e}")
        return None


def get_open_id_by_mobile(app_id, app_secret, mobile):
    """通过手机号获取 Open ID"""
    token = get_tenant_access_token(app_id, app_secret)
    if not token:
        return None

    # 确保手机号带国家代码
    if not mobile.startswith('+'):
        mobile = f'+86{mobile}'

    url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    params = {
        "user_id_type": "open_id"
    }

    data = {
        "mobiles": [mobile]
    }

    try:
        response = requests.post(url, headers=headers, json=data, params=params, timeout=10)
        result = response.json()

        if result.get("code") != 0:
            print(f"❌ 查询失败: {result}")
            return None

        user_list = result.get("data", {}).get("user_list", [])
        if user_list and user_list[0].get("user_id"):
            open_id = user_list[0]["user_id"]
            print(f"\n✅ 成功获取 Open ID: {open_id}")
            return open_id
        else:
            print("\n❌ 未找到该手机号对应的用户")
            print("   可能原因：")
            print("   1. 手机号未注册飞书")
            print("   2. 应用缺少权限（需要 contact:user.id:readonly）")
            print(f"   3. 开通权限: https://open.feishu.cn/app/{app_id}/auth")
            return None
    except Exception as e:
        print(f"❌ 查询错误: {e}")
        return None


def test_webhook(webhook_url):
    """测试 Webhook 推送"""
    data = {
        "msg_type": "text",
        "content": {
            "text": "🧪 飞书推送测试 - 配置成功！"
        }
    }

    try:
        response = requests.post(
            webhook_url,
            headers={'Content-Type': 'application/json'},
            json=data,
            timeout=10
        )
        result = response.json()

        if result.get("code") == 0:
            print("✅ Webhook 推送测试成功！")
            print("   请检查飞书群是否收到测试消息")
            return True
        else:
            print(f"❌ Webhook 推送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ Webhook 测试错误: {e}")
        return False


def test_private_message(app_id, app_secret, open_id):
    """测试私聊推送"""
    token = get_tenant_access_token(app_id, app_secret)
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

    import json
    data = {
        "receive_id": open_id,
        "msg_type": "text",
        "content": json.dumps({
            "text": "🧪 飞书推送测试 - 配置成功！"
        })
    }

    try:
        response = requests.post(url, headers=headers, json=data, params=params, timeout=10)
        result = response.json()

        if result.get("code") == 0:
            print("✅ 私聊推送测试成功！")
            print("   请检查飞书是否收到测试消息")
            return True
        elif result.get("code") == 230013:
            print("❌ 私聊推送失败: 机器人无权限给该用户发送消息")
            print("   解决方法：")
            print("   1. 在飞书中搜索并添加你的机器人")
            print("   2. 给机器人发送任意消息（如：你好）")
            print("   3. 重新运行此测试")
            return False
        else:
            print(f"❌ 私聊推送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 私聊测试错误: {e}")
        return False


def interactive_setup():
    """交互式配置向导"""
    print("=" * 60)
    print("飞书推送配置向导")
    print("Feishu Push Setup Wizard")
    print("=" * 60)
    print()

    # 选择推送方式
    print("请选择推送方式：")
    print("1. 群 Webhook 推送（推荐用于团队）")
    print("2. 私聊推送（推荐用于个人）")
    print("3. 两种都配置")
    print()

    choice = input("请输入选项 (1/2/3): ").strip()

    env_file = Path(__file__).parent.parent / ".env.feishu"
    config_lines = []

    if choice in ['1', '3']:
        print("\n--- 配置群 Webhook ---")
        webhook = input("请输入 Webhook URL: ").strip()
        if webhook:
            config_lines.append(f"export FEISHU_WEBHOOK=\"{webhook}\"")
            print("\n测试 Webhook...")
            test_webhook(webhook)

    if choice in ['2', '3']:
        print("\n--- 配置私聊推送 ---")
        app_id = input("请输入 App ID: ").strip()
        app_secret = input("请输入 App Secret: ").strip()

        if app_id and app_secret:
            config_lines.append(f"export FEISHU_APP_ID=\"{app_id}\"")
            config_lines.append(f"export FEISHU_APP_SECRET=\"{app_secret}\"")

            print("\n获取 Open ID...")
            mobile = input("请输入你的手机号（用于注册飞书的号码）: ").strip()

            if mobile:
                open_id = get_open_id_by_mobile(app_id, app_secret, mobile)
                if open_id:
                    config_lines.append(f"export FEISHU_USER_OPEN_ID=\"{open_id}\"")

                    print("\n测试私聊推送...")
                    test_private_message(app_id, app_secret, open_id)

    # 保存配置
    if config_lines:
        with open(env_file, 'w') as f:
            f.write("# 飞书推送配置\n")
            f.write("# 由 feishu_setup.py 自动生成\n\n")
            f.write("\n".join(config_lines))
            f.write("\n")

        print(f"\n✅ 配置已保存到: {env_file}")
        print("\n使用方法：")
        print(f"  source {env_file}")
        print("  python3 scripts/cn_market_report.py --async --push")
    else:
        print("\n⚠️ 未生成配置文件")


def main():
    parser = argparse.ArgumentParser(description='飞书推送配置工具')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互式配置向导')
    parser.add_argument('--get-open-id', action='store_true', help='获取用户 Open ID')
    parser.add_argument('--test-webhook', help='测试 Webhook URL')
    parser.add_argument('--test-private', action='store_true', help='测试私聊推送')

    args = parser.parse_args()

    if args.interactive or len(sys.argv) == 1:
        interactive_setup()
    elif args.get_open_id:
        app_id = os.environ.get('FEISHU_APP_ID') or input("App ID: ").strip()
        app_secret = os.environ.get('FEISHU_APP_SECRET') or input("App Secret: ").strip()
        mobile = input("手机号: ").strip()

        if app_id and app_secret and mobile:
            get_open_id_by_mobile(app_id, app_secret, mobile)
    elif args.test_webhook:
        test_webhook(args.test_webhook)
    elif args.test_private:
        app_id = os.environ.get('FEISHU_APP_ID')
        app_secret = os.environ.get('FEISHU_APP_SECRET')
        open_id = os.environ.get('FEISHU_USER_OPEN_ID')

        if not all([app_id, app_secret, open_id]):
            print("❌ 请先设置环境变量：FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_USER_OPEN_ID")
            sys.exit(1)

        test_private_message(app_id, app_secret, open_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
