#!/usr/bin/env python3
"""
使用预训练模型进行新闻分类
基于 Hugging Face 的中文情感分析模型
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from news_database import NewsDatabase

def classify_with_pretrained_model():
    """
    使用预训练的中文情感分析模型自动标注新闻

    推荐模型：
    1. hfl/chinese-roberta-wwm-ext (通用中文BERT)
    2. uer/roberta-base-finetuned-chinanews-chinese (中文新闻)
    3. fnlp/bart-base-chinese (中文生成式模型)
    """
    try:
        from transformers import pipeline
        print("📥 加载预训练模型...")

        # 使用zero-shot分类（无需训练）
        # 或使用通用情感分析模型
        classifier = pipeline(
            "zero-shot-classification",
            model="MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
            device=-1  # CPU
        )

        print("✅ 模型加载完成\n")

        db = NewsDatabase()

        # 获取未标注的新闻
        unlabeled = db.cursor.execute('''
            SELECT id, title, content FROM news WHERE sentiment IS NULL
        ''').fetchall()

        print(f"发现 {len(unlabeled)} 条未标注新闻\n")

        # 定义候选标签
        candidate_labels = ["利好消息", "利空消息", "中性消息"]
        labeled_count = 0

        for news in unlabeled:
            text = f"{news['title']} {news['content'] or ''}"[:512]  # 限制长度

            # Zero-shot分类
            result = classifier(text, candidate_labels)

            # 获取最高分的标签
            top_label = result['labels'][0]
            top_score = result['scores'][0]

            # 转换为系统标签
            if top_label == "利好消息":
                sentiment = "BULLISH"
            elif top_label == "利空消息":
                sentiment = "BEARISH"
            else:
                sentiment = "NEUTRAL"

            # 基于置信度计算重要性
            if top_score > 0.8:
                importance = 5
            elif top_score > 0.6:
                importance = 4
            elif top_score > 0.4:
                importance = 3
            else:
                importance = 2

            db.label_news(news['id'], sentiment, importance, labeled_by='pretrained_model')
            labeled_count += 1

            print(f"  {sentiment} (重要性{importance}, 置信度{top_score:.2f}) - {news['title'][:50]}")

        db.close()
        print(f"\n✅ 自动标注完成：{labeled_count} 条")

    except ImportError:
        print("❌ 缺少 transformers 库")
        print("安装: pip3 install transformers torch")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == '__main__':
    success = classify_with_pretrained_model()
    sys.exit(0 if success else 1)
