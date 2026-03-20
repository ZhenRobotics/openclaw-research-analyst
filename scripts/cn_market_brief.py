#!/usr/bin/env python3
"""
中国市场一键简报
China Market Brief - One-Click Summary

快速生成中国市场精简简报（≤120字）
Quick generation of China market brief summary (≤120 chars)

Usage:
    python3 scripts/cn_market_brief.py              # 生成简报
    python3 scripts/cn_market_brief.py --push       # 生成并推送到飞书
    python3 scripts/cn_market_brief.py --json       # JSON 格式输出
"""
import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

# Get skill directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
REPORTS_DIR = os.path.join(SKILL_DIR, 'reports')

def generate_brief(push=False, json_output=False):
    """
    生成精简简报

    Args:
        push: 是否推送到飞书
        json_output: 是否以 JSON 格式输出

    Returns:
        dict: 包含简报内容和文件路径
    """
    # Build command
    cmd = [
        'python3',
        os.path.join(SCRIPT_DIR, 'cn_market_report.py'),
        '--async',
        '--brief'
    ]

    if push:
        cmd.append('--push')

    # Execute
    try:
        result = subprocess.run(
            cmd,
            cwd=SKILL_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )

        # Parse output
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        # Extract brief content (everything before the file path line)
        lines = stdout.split('\n')
        brief_lines = []
        file_path = None
        push_success = False
        push_error = None

        # Parse stderr for status
        for line in stderr.split('\n'):
            if '✅ 精简简报已保存:' in line:
                file_path = line.split('✅ 精简简报已保存:')[1].strip()
            elif '✅ 飞书推送成功' in line:
                push_success = True
            elif '❌ 飞书推送失败' in line:
                push_success = False
                push_error = line

        # Brief is in stdout
        brief_content = stdout

        # Find the latest brief file if not extracted from stderr
        if not file_path:
            brief_files = sorted(
                Path(REPORTS_DIR).glob('cn_market_brief_*.txt'),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            if brief_files:
                file_path = str(brief_files[0])

        # Read brief from file
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract only the brief part (before metadata)
                brief_parts = content.split('\n\n生成时间:')
                if brief_parts:
                    brief_content = brief_parts[0].strip()

        result_data = {
            'success': result.returncode == 0,
            'brief': brief_content,
            'file_path': file_path,
            'timestamp': datetime.now().isoformat(),
            'pushed': push_success if push else False,
            'push_error': push_error if push and not push_success else None
        }

        if json_output:
            import json
            print(json.dumps(result_data, ensure_ascii=False, indent=2))
        else:
            # Print brief
            print(brief_content)
            if file_path:
                print(f"\n📄 已保存: {file_path}", file=sys.stderr)
            if push:
                if push_success:
                    print("✅ 已推送到飞书", file=sys.stderr)
                else:
                    print("❌ 飞书推送失败", file=sys.stderr)
                    if push_error:
                        print(f"   {push_error}", file=sys.stderr)

        return result_data

    except subprocess.TimeoutExpired:
        print("❌ 生成超时（> 60秒）", file=sys.stderr)
        return {'success': False, 'error': 'timeout'}
    except Exception as e:
        print(f"❌ 生成失败: {e}", file=sys.stderr)
        return {'success': False, 'error': str(e)}


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='中国市场一键简报 | China Market Brief - One-Click Summary',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例 (Examples):
  python3 scripts/cn_market_brief.py              # 生成简报
  python3 scripts/cn_market_brief.py --push       # 生成并推送
  python3 scripts/cn_market_brief.py --json       # JSON 输出

推送配置 (Push Configuration):
  需要配置 .env.feishu 文件，参考 FEISHU_QUICKSTART.md
  Configure .env.feishu file, see FEISHU_QUICKSTART.md
        """
    )

    parser.add_argument(
        '--push',
        action='store_true',
        help='推送到飞书 (Push to Feishu)'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='JSON 格式输出 (JSON output format)'
    )

    args = parser.parse_args()

    # Generate brief
    result = generate_brief(push=args.push, json_output=args.json)

    # Exit code
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
