#!/bin/bash
#
# 中国市场智能定时任务
# China Market Smart Scheduler
#
# 功能 (Features):
# 1. 交易时段自动推送（工作日 09:30-15:00，每 10 分钟）
# 2. 收盘后日报生成（15:05）
# 3. 智能判断交易日（跳过周末和节假日）
#
# 使用方法 (Usage):
#   ./scripts/cn_market_schedule.sh install      # 安装定时任务
#   ./scripts/cn_market_schedule.sh uninstall    # 卸载定时任务
#   ./scripts/cn_market_schedule.sh run-intraday # 运行盘中推送（手动）
#   ./scripts/cn_market_schedule.sh run-eod      # 运行收盘日报（手动）
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/tmp/cn_market_schedule.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查是否为工作日（周一至周五）
is_weekday() {
    local day=$(date '+%u')  # 1=Monday, 7=Sunday
    [ "$day" -le 5 ]
}

# 检查是否在交易时段（09:30-15:00）
is_trading_hours() {
    local hour=$(date '+%H')
    local minute=$(date '+%M')
    local time=$((hour * 100 + minute))

    # 09:30 = 930, 15:00 = 1500
    [ "$time" -ge 930 ] && [ "$time" -le 1500 ]
}

# 检查是否为收盘后（15:00-16:00）
is_after_close() {
    local hour=$(date '+%H')
    local minute=$(date '+%M')
    local time=$((hour * 100 + minute))

    # 15:00 = 1500, 16:00 = 1600
    [ "$time" -ge 1500 ] && [ "$time" -lt 1600 ]
}

# 盘中推送（交易时段内）
run_intraday_push() {
    log "========== 盘中推送开始 =========="

    # 检查是否为工作日
    if ! is_weekday; then
        log "⏭️  跳过：非工作日（周末）"
        return 0
    fi

    # 检查是否在交易时段
    if ! is_trading_hours; then
        log "⏭️  跳过：不在交易时段（09:30-15:00）"
        return 0
    fi

    log "✅ 工作日 + 交易时段，执行推送..."

    # 加载飞书配置
    if [ -f "$SKILL_DIR/.env.feishu" ]; then
        source "$SKILL_DIR/.env.feishu"
        log "📝 已加载飞书配置"
    else
        log "⚠️  未找到 .env.feishu，跳过推送"
    fi

    # 生成并推送简报
    cd "$SKILL_DIR"

    if python3 scripts/cn_market_brief.py --push >> "$LOG_FILE" 2>&1; then
        log "✅ 简报推送成功"
    else
        log "❌ 简报推送失败"
        return 1
    fi

    log "========== 盘中推送完成 =========="
}

# 收盘日报（收盘后一次）
run_eod_report() {
    log "========== 收盘日报开始 =========="

    # 检查是否为工作日
    if ! is_weekday; then
        log "⏭️  跳过：非工作日（周末）"
        return 0
    fi

    # 检查是否为收盘后
    if ! is_after_close; then
        log "⏭️  跳过：不在收盘时段（15:00-16:00）"
        return 0
    fi

    log "✅ 工作日 + 收盘时段，生成日报..."

    # 加载飞书配置
    if [ -f "$SKILL_DIR/.env.feishu" ]; then
        source "$SKILL_DIR/.env.feishu"
        log "📝 已加载飞书配置"
    fi

    # 生成完整报告
    cd "$SKILL_DIR"

    if python3 scripts/cn_market_report.py --async >> "$LOG_FILE" 2>&1; then
        log "✅ 日报生成成功"

        # 推送精简简报
        if [ -n "$FEISHU_USER_OPEN_ID" ] || [ -n "$FEISHU_WEBHOOK" ]; then
            if python3 scripts/cn_market_brief.py --push >> "$LOG_FILE" 2>&1; then
                log "✅ 日报推送成功"
            else
                log "⚠️  日报推送失败"
            fi
        fi
    else
        log "❌ 日报生成失败"
        return 1
    fi

    log "========== 收盘日报完成 =========="
}

# 安装定时任务
install_cron() {
    echo -e "${YELLOW}📅 安装中国市场智能定时任务${NC}"
    echo ""

    # 备份当前 crontab
    BACKUP_FILE="$HOME/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
    crontab -l > "$BACKUP_FILE" 2>/dev/null || true
    echo -e "${GREEN}✅ Crontab 已备份到: $BACKUP_FILE${NC}"

    # 定义 cron 任务
    CRON_INTRADAY="*/10 9-14 * * 1-5 $SCRIPT_DIR/cn_market_schedule.sh run-intraday >> $LOG_FILE 2>&1"
    CRON_EOD="5 15 * * 1-5 $SCRIPT_DIR/cn_market_schedule.sh run-eod >> $LOG_FILE 2>&1"

    # 添加到 crontab
    (
        crontab -l 2>/dev/null | grep -v "cn_market_schedule.sh" || true
        echo ""
        echo "# 中国市场智能定时任务 (China Market Smart Scheduler)"
        echo "# 盘中推送: 工作日 09:30-15:00, 每 10 分钟"
        echo "$CRON_INTRADAY"
        echo "# 收盘日报: 工作日 15:05"
        echo "$CRON_EOD"
    ) | crontab -

    echo ""
    echo -e "${GREEN}✅ 定时任务已安装${NC}"
    echo ""
    echo -e "${BLUE}📋 已安装的任务:${NC}"
    echo "   1. 盘中推送: 工作日 09:30-14:59, 每 10 分钟"
    echo "   2. 收盘日报: 工作日 15:05"
    echo ""
    echo -e "${BLUE}📊 查看日志:${NC}"
    echo "   tail -f $LOG_FILE"
    echo ""
    echo -e "${BLUE}🔍 验证安装:${NC}"
    echo "   crontab -l | grep cn_market"
    echo ""
}

# 卸载定时任务
uninstall_cron() {
    echo -e "${YELLOW}🗑️  卸载中国市场智能定时任务${NC}"
    echo ""

    # 备份当前 crontab
    BACKUP_FILE="$HOME/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
    crontab -l > "$BACKUP_FILE" 2>/dev/null || true
    echo -e "${GREEN}✅ Crontab 已备份到: $BACKUP_FILE${NC}"

    # 移除相关任务
    crontab -l 2>/dev/null | grep -v "cn_market_schedule.sh" | grep -v "China Market Smart Scheduler" | crontab - || true

    echo ""
    echo -e "${GREEN}✅ 定时任务已卸载${NC}"
    echo ""
    echo -e "${BLUE}🔍 验证卸载:${NC}"
    echo "   crontab -l | grep cn_market"
    echo "   （应该没有输出）"
    echo ""
}

# 显示帮助
show_help() {
    cat << EOF
${BLUE}中国市场智能定时任务 (China Market Smart Scheduler)${NC}

${YELLOW}使用方法 (Usage):${NC}
  $0 install         安装定时任务 (Install cron jobs)
  $0 uninstall       卸载定时任务 (Uninstall cron jobs)
  $0 run-intraday    运行盘中推送 (Run intraday push - manual)
  $0 run-eod         运行收盘日报 (Run end-of-day report - manual)
  $0 status          查看任务状态 (Check status)
  $0 logs            查看日志 (View logs)

${YELLOW}功能说明 (Features):${NC}
  1. ${GREEN}盘中推送${NC}
     - 工作日 09:30-15:00
     - 每 10 分钟推送一次精简简报
     - 自动跳过周末和非交易时段

  2. ${GREEN}收盘日报${NC}
     - 工作日 15:05
     - 生成完整日报并推送精简版

${YELLOW}配置要求 (Configuration):${NC}
  1. 飞书推送配置: .env.feishu
  2. 日志文件: $LOG_FILE

${YELLOW}示例 (Examples):${NC}
  # 安装定时任务
  $0 install

  # 手动测试盘中推送
  $0 run-intraday

  # 查看日志
  $0 logs

  # 卸载定时任务
  $0 uninstall

${YELLOW}文档 (Documentation):${NC}
  FEISHU_QUICKSTART.md  - 飞书推送配置
  SMART_SCHEDULING.md   - 智能定时详细说明

EOF
}

# 查看状态
show_status() {
    echo -e "${BLUE}📊 中国市场智能定时任务状态${NC}"
    echo ""

    # 检查 crontab
    echo -e "${YELLOW}Crontab 状态:${NC}"
    if crontab -l 2>/dev/null | grep -q "cn_market_schedule.sh"; then
        echo -e "  ${GREEN}✅ 已安装${NC}"
        echo ""
        echo -e "${YELLOW}已安装的任务:${NC}"
        crontab -l 2>/dev/null | grep "cn_market_schedule.sh" | sed 's/^/  /'
    else
        echo -e "  ${RED}❌ 未安装${NC}"
    fi

    echo ""

    # 检查配置
    echo -e "${YELLOW}配置状态:${NC}"
    if [ -f "$SKILL_DIR/.env.feishu" ]; then
        echo -e "  ${GREEN}✅ .env.feishu 存在${NC}"
    else
        echo -e "  ${RED}❌ .env.feishu 不存在${NC}"
    fi

    echo ""

    # 日志文件
    echo -e "${YELLOW}日志文件:${NC}"
    if [ -f "$LOG_FILE" ]; then
        echo -e "  ${GREEN}✅ $LOG_FILE${NC}"
        echo -e "  最后 5 行:"
        tail -5 "$LOG_FILE" 2>/dev/null | sed 's/^/    /'
    else
        echo -e "  ${YELLOW}⚠️  日志文件不存在${NC}"
    fi

    echo ""
}

# 查看日志
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo -e "${BLUE}📋 最近 20 行日志:${NC}"
        echo ""
        tail -20 "$LOG_FILE"
        echo ""
        echo -e "${YELLOW}实时查看日志:${NC}"
        echo "  tail -f $LOG_FILE"
    else
        echo -e "${YELLOW}⚠️  日志文件不存在: $LOG_FILE${NC}"
    fi
}

# 主函数
main() {
    case "${1:-}" in
        install)
            install_cron
            ;;
        uninstall)
            uninstall_cron
            ;;
        run-intraday)
            run_intraday_push
            ;;
        run-eod)
            run_eod_report
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ 未知命令: ${1:-}${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
