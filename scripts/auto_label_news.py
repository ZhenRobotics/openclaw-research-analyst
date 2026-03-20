#!/usr/bin/env python3
"""
自动标注工具 - 使用关键词规则自动标注新闻
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from news_database import NewsDatabase

# 关键词规则（与monitor中相同）
KEYWORD_RULES = {
    'BULLISH': ['降息', '降准', '刺激', '利好', '并购', '重组', '突破',
                '上涨', '增长', '盈利', '业绩超预期', '战略合作', '新产品',
                '技术突破', '政策支持', '订单', '中标'],
    'BEARISH': ['退市', '诉讼', '处罚', '暴雷', '破产', '辞职', '亏损',
                '下跌', '风险', '警示', '调查', '违规', '造假', '裁员',
                '债务', '减值', '停牌', '监管']
}

def auto_label_news():
    """使用关键词规则自动标注未标注的新闻"""
    db = NewsDatabase()

    # 获取未标注的新闻
    unlabeled = db.cursor.execute('''
        SELECT id, title, content FROM news WHERE sentiment IS NULL
    ''').fetchall()

    print(f"发现 {len(unlabeled)} 条未标注新闻")

    labeled_count = 0

    for news in unlabeled:
        text = f"{news['title']} {news['content'] or ''}".lower()

        bullish_count = sum(1 for kw in KEYWORD_RULES['BULLISH'] if kw in text)
        bearish_count = sum(1 for kw in KEYWORD_RULES['BEARISH'] if kw in text)

        # 只标注有明确信号的（至少匹配2个关键词）
        if bullish_count >= 2 or bearish_count >= 2:
            if bullish_count > bearish_count:
                sentiment = 'BULLISH'
                importance = min(5, 3 + bullish_count)
            else:
                sentiment = 'BEARISH'
                importance = min(5, 3 + bearish_count)

            db.label_news(news['id'], sentiment, importance, labeled_by='auto_keyword')
            labeled_count += 1
            print(f"  标注: {sentiment} (重要性{importance}) - {news['title'][:50]}")

    db.close()
    print(f"\n✅ 自动标注完成：{labeled_count} 条")
    print(f"剩余未标注：{len(unlabeled) - labeled_count} 条（关键词不明确）")

if __name__ == '__main__':
    auto_label_news()
