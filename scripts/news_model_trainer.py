#!/usr/bin/env python3
"""
新闻分类模型训练
News Classification Model Trainer

使用标注数据训练BERT模型，用于自动分类新闻的情绪和重要性
"""
import sys
import os
import json
import torch
import numpy as np
from pathlib import Path
from datetime import datetime
from sklearn.metrics import classification_report, confusion_matrix

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from news_database import NewsDatabase


class NewsModelTrainer:
    """新闻分类模型训练器"""

    def __init__(self, model_name='hfl/chinese-roberta-wwm-ext', device=None):
        """
        初始化

        Args:
            model_name: 预训练模型名称
            device: 设备（cuda/cpu）
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.db = NewsDatabase()

        print(f"🔧 使用设备: {self.device}")
        print(f"🤖 使用模型: {model_name}")

    def check_requirements(self):
        """检查依赖库"""
        try:
            import transformers
            import sklearn
            import torch
            print("✅ 依赖库检查通过")
            return True
        except ImportError as e:
            print(f"❌ 缺少依赖库: {e}")
            print("\n请安装:")
            print("pip install transformers torch scikit-learn")
            return False

    def prepare_data(self):
        """准备训练数据"""
        print("\n📊 准备训练数据...")

        # 获取数据库统计
        stats = self.db.get_statistics()

        if stats['labeled_news'] < 50:
            print(f"❌ 标注数据不足: {stats['labeled_news']} 条")
            print("   建议至少标注 50-100 条新闻后再训练")
            return None

        print(f"✅ 已标注数据: {stats['labeled_news']} 条")

        # 分割数据集
        split_result = self.db.split_training_data()
        print(f"✅ 数据集分割:")
        print(f"   训练集: {split_result['train']} 条")
        print(f"   验证集: {split_result['val']} 条")
        print(f"   测试集: {split_result['test']} 条")

        # 获取训练数据
        train_data = self.db.get_labeled_news(split='train')
        val_data = self.db.get_labeled_news(split='val')
        test_data = self.db.get_labeled_news(split='test')

        return {
            'train': train_data,
            'val': val_data,
            'test': test_data,
            'stats': stats
        }

    def train_sentiment_classifier(self, data, epochs=3, batch_size=16):
        """
        训练情绪分类器

        Args:
            data: 训练数据（dict with train/val/test）
            epochs: 训练轮数
            batch_size: 批次大小

        Returns:
            训练好的模型
        """
        try:
            from transformers import (
                AutoTokenizer,
                AutoModelForSequenceClassification,
                Trainer,
                TrainingArguments
            )
            from torch.utils.data import Dataset
        except ImportError:
            print("❌ 需要安装 transformers 库")
            print("运行: pip install transformers")
            return None

        print("\n🎯 训练情绪分类器...")

        # 定义标签映射
        label_map = {'BULLISH': 0, 'BEARISH': 1, 'NEUTRAL': 2}
        id_to_label = {v: k for k, v in label_map.items()}

        # 准备数据集
        class NewsDataset(Dataset):
            def __init__(self, data, tokenizer, max_length=512):
                self.data = data
                self.tokenizer = tokenizer
                self.max_length = max_length

            def __len__(self):
                return len(self.data)

            def __getitem__(self, idx):
                news = self.data[idx]
                text = f"{news['title']}\n{news['content'] or ''}"

                encoding = self.tokenizer(
                    text,
                    max_length=self.max_length,
                    padding='max_length',
                    truncation=True,
                    return_tensors='pt'
                )

                return {
                    'input_ids': encoding['input_ids'].flatten(),
                    'attention_mask': encoding['attention_mask'].flatten(),
                    'labels': torch.tensor(label_map[news['sentiment']], dtype=torch.long)
                }

        # 加载tokenizer和模型
        print("📥 加载预训练模型...")
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=3
        )

        # 创建数据集
        train_dataset = NewsDataset(data['train'], tokenizer)
        val_dataset = NewsDataset(data['val'], tokenizer)

        # 训练参数
        output_dir = Path(__file__).parent.parent / 'models' / 'sentiment_classifier'
        output_dir.mkdir(parents=True, exist_ok=True)

        training_args = TrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir=str(output_dir / 'logs'),
            logging_steps=10,
            eval_strategy='epoch',
            save_strategy='epoch',
            load_best_model_at_end=True,
        )

        # 训练
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )

        print("🚀 开始训练...")
        trainer.train()

        # 保存模型
        model_path = output_dir / 'final_model'
        trainer.save_model(str(model_path))
        tokenizer.save_pretrained(str(model_path))

        print(f"✅ 模型已保存到: {model_path}")

        # 评估
        print("\n📊 在测试集上评估...")
        test_dataset = NewsDataset(data['test'], tokenizer)
        predictions = trainer.predict(test_dataset)

        pred_labels = np.argmax(predictions.predictions, axis=1)
        true_labels = predictions.label_ids

        print("\n分类报告:")
        print(classification_report(
            true_labels,
            pred_labels,
            target_names=['BULLISH', 'BEARISH', 'NEUTRAL']
        ))

        return model, tokenizer, label_map

    def train_importance_scorer(self, data, epochs=3, batch_size=16):
        """
        训练重要性评分模型（回归任务）

        Args:
            data: 训练数据
            epochs: 训练轮数
            batch_size: 批次大小

        Returns:
            训练好的模型
        """
        try:
            from transformers import (
                AutoTokenizer,
                AutoModelForSequenceClassification,
                Trainer,
                TrainingArguments
            )
            from torch.utils.data import Dataset
        except ImportError:
            print("❌ 需要安装 transformers 库")
            return None

        print("\n🎯 训练重要性评分器...")

        # 准备数据集（回归任务）
        class ImportanceDataset(Dataset):
            def __init__(self, data, tokenizer, max_length=512):
                self.data = data
                self.tokenizer = tokenizer
                self.max_length = max_length

            def __len__(self):
                return len(self.data)

            def __getitem__(self, idx):
                news = self.data[idx]
                text = f"{news['title']}\n{news['content'] or ''}"

                encoding = self.tokenizer(
                    text,
                    max_length=self.max_length,
                    padding='max_length',
                    truncation=True,
                    return_tensors='pt'
                )

                return {
                    'input_ids': encoding['input_ids'].flatten(),
                    'attention_mask': encoding['attention_mask'].flatten(),
                    'labels': torch.tensor(news['importance'], dtype=torch.float)
                }

        # 加载模型（用于回归，num_labels=1）
        print("📥 加载预训练模型...")
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=1,
            problem_type='regression'
        )

        # 创建数据集
        train_dataset = ImportanceDataset(data['train'], tokenizer)
        val_dataset = ImportanceDataset(data['val'], tokenizer)

        # 训练参数
        output_dir = Path(__file__).parent.parent / 'models' / 'importance_scorer'
        output_dir.mkdir(parents=True, exist_ok=True)

        training_args = TrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir=str(output_dir / 'logs'),
            logging_steps=10,
            eval_strategy='epoch',
            save_strategy='epoch',
            load_best_model_at_end=True,
        )

        # 训练
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )

        print("🚀 开始训练...")
        trainer.train()

        # 保存模型
        model_path = output_dir / 'final_model'
        trainer.save_model(str(model_path))
        tokenizer.save_pretrained(str(model_path))

        print(f"✅ 模型已保存到: {model_path}")

        return model, tokenizer

    def close(self):
        """关闭数据库连接"""
        self.db.close()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='新闻分类模型训练')
    parser.add_argument('task', choices=['sentiment', 'importance', 'both'],
                       help='训练任务：sentiment（情绪）、importance（重要性）、both（两者）')
    parser.add_argument('--model', default='hfl/chinese-roberta-wwm-ext',
                       help='预训练模型名称')
    parser.add_argument('--epochs', type=int, default=3,
                       help='训练轮数（默认3）')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='批次大小（默认16）')
    parser.add_argument('--device', choices=['cuda', 'cpu'],
                       help='训练设备')

    args = parser.parse_args()

    trainer = NewsModelTrainer(model_name=args.model, device=args.device)

    if not trainer.check_requirements():
        return

    try:
        # 准备数据
        data = trainer.prepare_data()
        if data is None:
            return

        # 训练模型
        if args.task in ['sentiment', 'both']:
            trainer.train_sentiment_classifier(
                data,
                epochs=args.epochs,
                batch_size=args.batch_size
            )

        if args.task in ['importance', 'both']:
            trainer.train_importance_scorer(
                data,
                epochs=args.epochs,
                batch_size=args.batch_size
            )

        print("\n✅ 训练完成！")
        print("\n下一步:")
        print("1. 使用 scripts/news_monitor.py 进行实时监控")
        print("2. 检查 models/ 目录查看训练好的模型")

    finally:
        trainer.close()


if __name__ == '__main__':
    main()
