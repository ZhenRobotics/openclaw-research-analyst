#!/usr/bin/env python3
"""
新闻数据库管理
News Database Manager

用于存储、标注和管理新闻数据，为AI模型训练做准备
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import hashlib

class NewsDatabase:
    """新闻数据库管理类"""

    def __init__(self, db_path=None):
        """
        初始化数据库连接

        Args:
            db_path: 数据库文件路径，默认为 data/news.db
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent / 'data' / 'news.db'

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self._create_tables()

    def _create_tables(self):
        """创建数据库表结构"""

        # 新闻表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                source TEXT NOT NULL,
                url TEXT,
                publish_time TIMESTAMP,
                fetch_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                -- 原始数据（JSON格式）
                raw_data TEXT,

                -- 标注字段
                sentiment TEXT CHECK(sentiment IN ('BULLISH', 'BEARISH', 'NEUTRAL', NULL)),
                importance INTEGER CHECK(importance BETWEEN 1 AND 5),
                affected_stocks TEXT,  -- JSON数组
                tags TEXT,  -- JSON数组

                -- 标注元数据
                labeled_by TEXT,
                labeled_at TIMESTAMP,

                -- AI预测结果
                predicted_sentiment TEXT,
                predicted_importance REAL,
                prediction_confidence REAL,
                predicted_at TIMESTAMP,

                -- 状态
                is_major BOOLEAN DEFAULT 0,
                is_pushed BOOLEAN DEFAULT 0,
                pushed_at TIMESTAMP,

                -- 索引字段
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 股票相关新闻索引
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                stock_name TEXT,
                news_id INTEGER NOT NULL,
                relevance_score REAL,
                FOREIGN KEY (news_id) REFERENCES news(id)
            )
        ''')

        # 关键词表（用于简单分类）
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT UNIQUE NOT NULL,
                category TEXT CHECK(category IN ('BULLISH', 'BEARISH')),
                weight REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 训练数据集
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id INTEGER NOT NULL,
                split TEXT CHECK(split IN ('train', 'val', 'test')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (news_id) REFERENCES news(id)
            )
        ''')

        # 创建索引
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_news_sentiment
            ON news(sentiment)
        ''')

        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_news_importance
            ON news(importance)
        ''')

        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_news_publish_time
            ON news(publish_time DESC)
        ''')

        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_stock_code
            ON stock_news(stock_code)
        ''')

        self.conn.commit()

    def generate_news_id(self, title, source, publish_time):
        """生成唯一的新闻ID"""
        content = f"{source}:{title}:{publish_time}"
        return hashlib.md5(content.encode()).hexdigest()

    def add_news(self, title, content, source, url=None, publish_time=None,
                 raw_data=None, affected_stocks=None, tags=None):
        """
        添加新闻

        Args:
            title: 标题
            content: 内容
            source: 来源（eastmoney, sina, cls, tencent, ths）
            url: URL
            publish_time: 发布时间
            raw_data: 原始数据（dict）
            affected_stocks: 相关股票列表
            tags: 标签列表

        Returns:
            news_id: 新闻ID，如果已存在返回 None
        """
        if publish_time is None:
            publish_time = datetime.now()

        news_id = self.generate_news_id(title, source, publish_time)

        try:
            self.cursor.execute('''
                INSERT INTO news (
                    news_id, title, content, source, url, publish_time,
                    raw_data, affected_stocks, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                news_id,
                title,
                content,
                source,
                url,
                publish_time,
                json.dumps(raw_data, ensure_ascii=False) if raw_data else None,
                json.dumps(affected_stocks, ensure_ascii=False) if affected_stocks else None,
                json.dumps(tags, ensure_ascii=False) if tags else None
            ))

            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # 新闻已存在
            return None

    def label_news(self, news_id, sentiment, importance,
                   affected_stocks=None, tags=None, labeled_by='human'):
        """
        标注新闻

        Args:
            news_id: 新闻数据库ID
            sentiment: 情绪（BULLISH/BEARISH/NEUTRAL）
            importance: 重要性（1-5）
            affected_stocks: 相关股票列表
            tags: 标签列表
            labeled_by: 标注者
        """
        self.cursor.execute('''
            UPDATE news
            SET sentiment = ?,
                importance = ?,
                affected_stocks = ?,
                tags = ?,
                labeled_by = ?,
                labeled_at = CURRENT_TIMESTAMP,
                is_major = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            sentiment,
            importance,
            json.dumps(affected_stocks, ensure_ascii=False) if affected_stocks else None,
            json.dumps(tags, ensure_ascii=False) if tags else None,
            labeled_by,
            1 if importance >= 4 else 0,
            news_id
        ))

        self.conn.commit()

    def get_unlabeled_news(self, limit=10):
        """获取未标注的新闻"""
        self.cursor.execute('''
            SELECT id, news_id, title, content, source, publish_time
            FROM news
            WHERE sentiment IS NULL
            ORDER BY publish_time DESC
            LIMIT ?
        ''', (limit,))

        return [dict(row) for row in self.cursor.fetchall()]

    def get_labeled_news(self, split=None, limit=None):
        """
        获取已标注的新闻

        Args:
            split: 数据集分割（train/val/test），None表示所有
            limit: 返回数量限制
        """
        if split:
            query = '''
                SELECT n.*, t.split
                FROM news n
                JOIN training_data t ON n.id = t.news_id
                WHERE n.sentiment IS NOT NULL
                  AND t.split = ?
                ORDER BY n.publish_time DESC
            '''
            params = [split]
        else:
            query = '''
                SELECT *
                FROM news
                WHERE sentiment IS NOT NULL
                ORDER BY publish_time DESC
            '''
            params = []

        if limit:
            query += ' LIMIT ?'
            params.append(limit)

        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]

    def get_major_news(self, hours=24, limit=50):
        """
        获取重大新闻

        Args:
            hours: 最近多少小时的新闻
            limit: 返回数量
        """
        self.cursor.execute('''
            SELECT *
            FROM news
            WHERE importance >= 4
              AND publish_time >= datetime('now', '-' || ? || ' hours')
            ORDER BY importance DESC, publish_time DESC
            LIMIT ?
        ''', (hours, limit))

        return [dict(row) for row in self.cursor.fetchall()]

    def mark_as_pushed(self, news_id):
        """标记新闻已推送"""
        self.cursor.execute('''
            UPDATE news
            SET is_pushed = 1,
                pushed_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (news_id,))

        self.conn.commit()

    def add_prediction(self, news_id, sentiment, importance, confidence):
        """
        添加AI预测结果

        Args:
            news_id: 新闻数据库ID
            sentiment: 预测情绪
            importance: 预测重要性
            confidence: 置信度
        """
        self.cursor.execute('''
            UPDATE news
            SET predicted_sentiment = ?,
                predicted_importance = ?,
                prediction_confidence = ?,
                predicted_at = CURRENT_TIMESTAMP,
                is_major = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            sentiment,
            importance,
            confidence,
            1 if importance >= 4.0 else 0,
            news_id
        ))

        self.conn.commit()

    def get_statistics(self):
        """获取数据库统计信息"""
        stats = {}

        # 总新闻数
        self.cursor.execute('SELECT COUNT(*) FROM news')
        stats['total_news'] = self.cursor.fetchone()[0]

        # 已标注数
        self.cursor.execute('SELECT COUNT(*) FROM news WHERE sentiment IS NOT NULL')
        stats['labeled_news'] = self.cursor.fetchone()[0]

        # 情绪分布
        self.cursor.execute('''
            SELECT sentiment, COUNT(*) as count
            FROM news
            WHERE sentiment IS NOT NULL
            GROUP BY sentiment
        ''')
        stats['sentiment_distribution'] = {
            row['sentiment']: row['count']
            for row in self.cursor.fetchall()
        }

        # 重要性分布
        self.cursor.execute('''
            SELECT importance, COUNT(*) as count
            FROM news
            WHERE importance IS NOT NULL
            GROUP BY importance
        ''')
        stats['importance_distribution'] = {
            row['importance']: row['count']
            for row in self.cursor.fetchall()
        }

        # 重大新闻数
        self.cursor.execute('SELECT COUNT(*) FROM news WHERE is_major = 1')
        stats['major_news'] = self.cursor.fetchone()[0]

        # 来源分布
        self.cursor.execute('''
            SELECT source, COUNT(*) as count
            FROM news
            GROUP BY source
        ''')
        stats['source_distribution'] = {
            row['source']: row['count']
            for row in self.cursor.fetchall()
        }

        return stats

    def split_training_data(self, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15):
        """
        将已标注数据分割为训练/验证/测试集

        Args:
            train_ratio: 训练集比例
            val_ratio: 验证集比例
            test_ratio: 测试集比例
        """
        import random

        # 清空现有分割
        self.cursor.execute('DELETE FROM training_data')

        # 获取所有已标注新闻
        self.cursor.execute('''
            SELECT id FROM news WHERE sentiment IS NOT NULL
        ''')
        news_ids = [row['id'] for row in self.cursor.fetchall()]

        # 随机打乱
        random.shuffle(news_ids)

        # 分割
        total = len(news_ids)
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)

        train_ids = news_ids[:train_end]
        val_ids = news_ids[train_end:val_end]
        test_ids = news_ids[val_end:]

        # 插入分割数据
        for news_id in train_ids:
            self.cursor.execute(
                'INSERT INTO training_data (news_id, split) VALUES (?, ?)',
                (news_id, 'train')
            )

        for news_id in val_ids:
            self.cursor.execute(
                'INSERT INTO training_data (news_id, split) VALUES (?, ?)',
                (news_id, 'val')
            )

        for news_id in test_ids:
            self.cursor.execute(
                'INSERT INTO training_data (news_id, split) VALUES (?, ?)',
                (news_id, 'test')
            )

        self.conn.commit()

        return {
            'train': len(train_ids),
            'val': len(val_ids),
            'test': len(test_ids)
        }

    def export_training_data(self, output_dir, split=None):
        """
        导出训练数据为JSON格式

        Args:
            output_dir: 输出目录
            split: 数据集分割，None表示导出所有
        """
        from pathlib import Path

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        news_list = self.get_labeled_news(split=split)

        # 转换为训练格式
        training_data = []
        for news in news_list:
            training_data.append({
                'text': f"{news['title']}\n{news['content'] or ''}",
                'label': news['sentiment'],
                'importance': news['importance'],
                'metadata': {
                    'news_id': news['news_id'],
                    'source': news['source'],
                    'publish_time': news['publish_time'],
                    'affected_stocks': json.loads(news['affected_stocks']) if news['affected_stocks'] else [],
                    'tags': json.loads(news['tags']) if news['tags'] else []
                }
            })

        # 保存
        if split:
            output_file = output_dir / f'{split}.json'
        else:
            output_file = output_dir / 'all_data.json'

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)

        return str(output_file)

    def close(self):
        """关闭数据库连接"""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='新闻数据库管理')
    parser.add_argument('command', choices=['stats', 'export', 'split'],
                       help='命令：stats（统计）、export（导出）、split（分割数据集）')
    parser.add_argument('--output', help='导出目录')
    parser.add_argument('--split', choices=['train', 'val', 'test'],
                       help='数据集分割')

    args = parser.parse_args()

    with NewsDatabase() as db:
        if args.command == 'stats':
            stats = db.get_statistics()
            print("\n=== 数据库统计 ===\n")
            print(f"总新闻数: {stats['total_news']}")
            print(f"已标注数: {stats['labeled_news']}")
            print(f"重大新闻: {stats['major_news']}")

            print("\n情绪分布:")
            for sentiment, count in stats['sentiment_distribution'].items():
                print(f"  {sentiment}: {count}")

            print("\n重要性分布:")
            for importance, count in sorted(stats['importance_distribution'].items()):
                print(f"  {importance}: {count}")

            print("\n来源分布:")
            for source, count in stats['source_distribution'].items():
                print(f"  {source}: {count}")

        elif args.command == 'split':
            result = db.split_training_data()
            print("\n=== 数据集分割完成 ===\n")
            print(f"训练集: {result['train']}")
            print(f"验证集: {result['val']}")
            print(f"测试集: {result['test']}")

        elif args.command == 'export':
            if not args.output:
                print("错误：需要指定 --output 目录")
                return

            output_file = db.export_training_data(args.output, split=args.split)
            print(f"\n数据已导出到: {output_file}")


if __name__ == '__main__':
    main()
