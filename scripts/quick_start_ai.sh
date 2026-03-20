#!/bin/bash
#
# AI新闻监控系统 - 快速启动脚本
# Quick Start Script for AI News Monitoring System
#
# 用法: ./scripts/quick_start_ai.sh [stage]
# 阶段: collect, label, train, monitor

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}"
echo "════════════════════════════════════════════════════════"
echo "  AI驱动的重大新闻监控系统 - 快速启动"
echo "  AI-Powered Major News Monitoring System"
echo "════════════════════════════════════════════════════════"
echo -e "${NC}\n"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 已安装${NC}"

# 阶段1: 数据收集
stage_collect() {
    echo -e "\n${YELLOW}=== 阶段1: 数据收集 ===${NC}\n"

    # 创建必要目录
    mkdir -p "$PROJECT_DIR/data"
    mkdir -p "$PROJECT_DIR/logs"

    echo "📥 安装基础依赖..."
    pip3 install -q aiohttp requests 2>/dev/null || {
        echo -e "${RED}❌ 依赖安装失败${NC}"
        echo "请手动运行: pip3 install aiohttp requests"
        exit 1
    }

    echo -e "${GREEN}✅ 依赖安装完成${NC}\n"

    # 首次收集
    echo "📰 开始收集新闻（100条）..."
    cd "$PROJECT_DIR"
    python3 scripts/news_collector.py --limit 100

    echo -e "\n${GREEN}✅ 数据收集完成${NC}\n"

    # 显示统计
    python3 scripts/news_database.py stats

    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}下一步: 标注数据${NC}"
    echo "运行: ./scripts/quick_start_ai.sh label"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# 阶段2: 数据标注
stage_label() {
    echo -e "\n${YELLOW}=== 阶段2: 数据标注 ===${NC}\n"

    cd "$PROJECT_DIR"

    # 检查是否有数据
    stats_output=$(python3 scripts/news_database.py stats 2>/dev/null | grep "总新闻数" || echo "")

    if [[ -z "$stats_output" ]] || [[ "$stats_output" == *"0"* ]]; then
        echo -e "${RED}❌ 数据库中没有新闻数据${NC}"
        echo "请先运行: ./scripts/quick_start_ai.sh collect"
        exit 1
    fi

    echo "🏷️  启动标注工具..."
    echo "   - 使用数字键 1/2/3 选择情绪"
    echo "   - 输入 1-5 评分重要性"
    echo "   - 按 's' 跳过，'q' 退出"
    echo ""

    python3 scripts/news_labeling_tool.py label --batch-size 20

    echo -e "\n${GREEN}✅ 标注完成${NC}\n"

    # 显示标注进度
    python3 scripts/news_labeling_tool.py stats

    # 检查是否可以训练
    labeled_count=$(python3 -c "
from scripts.news_database import NewsDatabase
db = NewsDatabase()
stats = db.get_statistics()
print(stats['labeled_news'])
db.close()
" 2>/dev/null || echo "0")

    echo ""

    if [ "$labeled_count" -ge 50 ]; then
        echo -e "${GREEN}✅ 已标注 $labeled_count 条，可以开始训练！${NC}"
        echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}下一步: 训练模型${NC}"
        echo "运行: ./scripts/quick_start_ai.sh train"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    else
        echo -e "${YELLOW}⚠️  已标注 $labeled_count 条，建议至少标注 50 条${NC}"
        echo "继续标注: python3 scripts/news_labeling_tool.py label"
        echo "或使用关键词规则: ./scripts/quick_start_ai.sh monitor-keyword"
    fi
}

# 阶段3: 模型训练
stage_train() {
    echo -e "\n${YELLOW}=== 阶段3: 模型训练 ===${NC}\n"

    cd "$PROJECT_DIR"

    # 检查标注数据
    labeled_count=$(python3 -c "
from scripts.news_database import NewsDatabase
db = NewsDatabase()
stats = db.get_statistics()
print(stats['labeled_news'])
db.close()
" 2>/dev/null || echo "0")

    if [ "$labeled_count" -lt 50 ]; then
        echo -e "${RED}❌ 标注数据不足: $labeled_count 条${NC}"
        echo "需要至少 50 条标注数据"
        echo "运行: ./scripts/quick_start_ai.sh label"
        exit 1
    fi

    echo -e "${GREEN}✅ 标注数据充足: $labeled_count 条${NC}\n"

    # 安装AI依赖
    echo "📥 检查AI依赖..."

    if ! python3 -c "import torch, transformers, sklearn" 2>/dev/null; then
        echo "安装AI依赖（这可能需要几分钟）..."
        echo ""
        echo "1. PyTorch (CPU版本)"
        echo "2. Transformers"
        echo "3. scikit-learn"
        echo ""

        read -p "是否现在安装？[y/N] " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "安装中..."
            pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
            pip3 install transformers scikit-learn

            if [ $? -ne 0 ]; then
                echo -e "${RED}❌ 安装失败${NC}"
                echo "请手动安装: pip3 install -r requirements-ai.txt"
                exit 1
            fi
        else
            echo "取消训练"
            exit 0
        fi
    fi

    echo -e "${GREEN}✅ AI依赖已安装${NC}\n"

    # 训练模型
    echo "🤖 开始训练模型..."
    echo "   - 任务: 情绪分类 + 重要性评分"
    echo "   - 轮数: 3 epochs"
    echo "   - 预计时间: 10-30分钟（CPU）"
    echo ""

    python3 scripts/news_model_trainer.py both --epochs 3 --batch-size 8

    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✅ 模型训练完成${NC}\n"

        # 检查模型文件
        if [ -d "$PROJECT_DIR/models/sentiment_classifier/final_model" ]; then
            echo -e "${GREEN}✅ 情绪分类器已保存${NC}"
        fi

        if [ -d "$PROJECT_DIR/models/importance_scorer/final_model" ]; then
            echo -e "${GREEN}✅ 重要性评分器已保存${NC}"
        fi

        echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}下一步: 启动监控${NC}"
        echo "运行: ./scripts/quick_start_ai.sh monitor"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    else
        echo -e "${RED}❌ 模型训练失败${NC}"
        exit 1
    fi
}

# 阶段4: 启动监控（AI模式）
stage_monitor() {
    echo -e "\n${YELLOW}=== 阶段4: 启动监控（AI模式）===${NC}\n"

    cd "$PROJECT_DIR"

    # 检查模型
    if [ ! -d "$PROJECT_DIR/models/sentiment_classifier/final_model" ]; then
        echo -e "${RED}❌ 模型不存在${NC}"
        echo "请先训练模型: ./scripts/quick_start_ai.sh train"
        exit 1
    fi

    echo -e "${GREEN}✅ AI模型已就绪${NC}\n"

    # 检查飞书配置
    if [ -f "$PROJECT_DIR/.env.feishu" ]; then
        echo -e "${GREEN}✅ 飞书推送已配置${NC}\n"
    else
        echo -e "${YELLOW}⚠️  飞书推送未配置${NC}"
        echo "运行: python3 scripts/feishu_setup.py"
        echo "或跳过推送继续"
        echo ""
    fi

    echo "🔍 启动参数:"
    echo "   - 模式: AI自动分类"
    echo "   - 重要性阈值: >= 4"
    echo "   - 抓取间隔: 300 秒（5分钟）"
    echo ""

    read -p "按Enter启动，Ctrl+C停止..."

    python3 scripts/news_monitor.py --interval 300 --threshold 4
}

# 启动监控（关键词模式）
stage_monitor_keyword() {
    echo -e "\n${YELLOW}=== 启动监控（关键词模式）===${NC}\n"

    cd "$PROJECT_DIR"

    echo "🔍 启动参数:"
    echo "   - 模式: 关键词规则"
    echo "   - 重要性阈值: >= 4"
    echo "   - 抓取间隔: 300 秒（5分钟）"
    echo ""

    if [ -f "$PROJECT_DIR/.env.feishu" ]; then
        echo -e "${GREEN}✅ 飞书推送已配置${NC}\n"
    else
        echo -e "${YELLOW}⚠️  飞书推送未配置（可选）${NC}\n"
    fi

    read -p "按Enter启动，Ctrl+C停止..."

    python3 scripts/news_monitor.py --no-ai --interval 300 --threshold 4
}

# 显示帮助
show_help() {
    echo "用法: $0 [stage]"
    echo ""
    echo "阶段 (Stages):"
    echo "  collect          阶段1: 收集新闻数据"
    echo "  label            阶段2: 标注数据"
    echo "  train            阶段3: 训练AI模型"
    echo "  monitor          阶段4: 启动AI监控"
    echo "  monitor-keyword  启动监控（关键词模式，无需AI）"
    echo ""
    echo "完整流程:"
    echo "  1. ./scripts/quick_start_ai.sh collect"
    echo "  2. ./scripts/quick_start_ai.sh label"
    echo "  3. ./scripts/quick_start_ai.sh train"
    echo "  4. ./scripts/quick_start_ai.sh monitor"
    echo ""
    echo "快速测试（无AI）:"
    echo "  1. ./scripts/quick_start_ai.sh collect"
    echo "  2. ./scripts/quick_start_ai.sh monitor-keyword"
}

# 主函数
main() {
    case "${1:-help}" in
        collect)
            stage_collect
            ;;
        label)
            stage_label
            ;;
        train)
            stage_train
            ;;
        monitor)
            stage_monitor
            ;;
        monitor-keyword)
            stage_monitor_keyword
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ 未知阶段: $1${NC}\n"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
