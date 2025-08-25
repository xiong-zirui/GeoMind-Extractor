#!/usr/bin/env python3
"""
智能地质数据提取系统 - 主入口程序
使用三阶段知识合成流水线处理地质文献
"""

import argparse
import logging
from pathlib import Path
import json
from datetime import datetime

from config import load_config
from knowledge_synthesis_pipeline import KnowledgeSynthesisPipeline


def setup_logging(log_level: str = "INFO") -> None:
    """设置日志配置"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def process_single_document(pdf_path: Path, config: dict, output_dir: Path) -> dict:
    """处理单个PDF文档"""
    logger = logging.getLogger(__name__)
    
    logger.info(f"🚀 开始处理文档: {pdf_path.name}")
    
    # 初始化流水线
    pipeline = KnowledgeSynthesisPipeline(config)
    
    # 处理文档
    result = pipeline.process_document(pdf_path)
    
    if result.get('status') == 'success':
        # 保存结果
        saved_files = pipeline.save_results(result, output_dir)
        
        # 打印处理摘要
        summary = result.get('summary', {})
        print(f"\n✅ 文档 '{pdf_path.name}' 处理完成!")
        print(f"📊 处理摘要:")
        print(f"   • 计划任务数: {summary.get('total_tasks_planned', 0)}")
        print(f"   • 空间要素数: {summary.get('spatial_features_count', 0)}")
        print(f"   • 地球化学结论数: {summary.get('geochemical_conclusions_count', 0)}")
        print(f"   • 标准化表格数: {summary.get('standardized_tables_count', 0)}")
        print(f"   • 数据库记录数: {summary.get('database_records_count', 0)}")
        print(f"   • 总体置信度: {summary.get('overall_confidence', 0.0):.2%}")
        
        print(f"💾 结果文件:")
        for file_type, file_path in saved_files.items():
            print(f"   • {file_type}: {file_path}")
        
        return {'status': 'success', 'saved_files': saved_files, 'summary': summary}
    
    else:
        error_msg = result.get('error', 'Unknown error')
        logger.error(f"❌ 文档处理失败: {error_msg}")
        return {'status': 'failed', 'error': error_msg}


def process_batch_documents(input_dir: Path, config: dict, output_dir: Path) -> dict:
    """批量处理PDF文档"""
    logger = logging.getLogger(__name__)
    
    # 查找所有PDF文件
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"在目录 {input_dir} 中未找到PDF文件")
        return {'status': 'no_files', 'processed': 0, 'failed': 0}
    
    logger.info(f"找到 {len(pdf_files)} 个PDF文件，开始批量处理...")
    
    # 批量处理统计
    processed_count = 0
    failed_count = 0
    results = []
    
    for pdf_path in pdf_files:
        try:
            result = process_single_document(pdf_path, config, output_dir)
            results.append({
                'file': pdf_path.name,
                'result': result
            })
            
            if result['status'] == 'success':
                processed_count += 1
            else:
                failed_count += 1
                
        except Exception as e:
            logger.error(f"处理文件 {pdf_path.name} 时发生异常: {e}")
            failed_count += 1
            results.append({
                'file': pdf_path.name,
                'result': {'status': 'exception', 'error': str(e)}
            })
    
    # 保存批量处理报告
    batch_report = {
        'processing_timestamp': datetime.now().isoformat(),
        'total_files': len(pdf_files),
        'processed_successfully': processed_count,
        'failed': failed_count,
        'success_rate': processed_count / len(pdf_files) if pdf_files else 0,
        'detailed_results': results
    }
    
    report_file = output_dir / "batch_processing_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(batch_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📈 批量处理完成!")
    print(f"   • 总文件数: {len(pdf_files)}")
    print(f"   • 成功处理: {processed_count}")
    print(f"   • 处理失败: {failed_count}")
    print(f"   • 成功率: {batch_report['success_rate']:.1%}")
    print(f"   • 详细报告: {report_file}")
    
    return batch_report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="智能地质数据提取系统 - 三阶段知识合成流水线",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 处理单个PDF文件
  python main_intelligent.py --input data/raw/theses-WAXI/2008_MATABANE_FE3.pdf
  
  # 批量处理目录中的所有PDF文件
  python main_intelligent.py --input data/raw/theses-WAXI/ --batch
  
  # 指定输出目录和日志级别
  python main_intelligent.py --input file.pdf --output results/ --log-level DEBUG
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="输入PDF文件路径或包含PDF文件的目录路径"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="data/processed/",
        help="输出目录路径 (默认: data/processed/)"
    )
    
    parser.add_argument(
        "--batch", "-b",
        action="store_true",
        help="批量处理模式：处理输入目录中的所有PDF文件"
    )
    
    parser.add_argument(
        "--log-level", "-l",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别 (默认: INFO)"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="配置文件路径 (默认: config.yml)"
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # 加载配置
    try:
        if args.config:
            config = load_config(args.config)
        else:
            config = load_config()
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        return 1
    
    # 验证输入路径
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"输入路径不存在: {input_path}")
        return 1
    
    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 处理逻辑
    try:
        if args.batch:
            # 批量处理模式
            if not input_path.is_dir():
                logger.error("批量处理模式需要输入目录路径")
                return 1
            
            result = process_batch_documents(input_path, config, output_dir)
            
        else:
            # 单文件处理模式
            if input_path.is_dir():
                logger.error("单文件处理模式需要输入PDF文件路径")
                return 1
            
            if not input_path.suffix.lower() == '.pdf':
                logger.error("输入文件必须是PDF格式")
                return 1
            
            result = process_single_document(input_path, config, output_dir)
        
        # 根据处理结果返回适当的退出码
        if result['status'] == 'success':
            return 0
        elif result['status'] == 'no_files':
            return 0  # 没有文件可处理不算错误
        else:
            return 1
            
    except KeyboardInterrupt:
        logger.info("用户中断处理")
        return 130
    except Exception as e:
        logger.error(f"程序执行过程中发生未预期的错误: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
