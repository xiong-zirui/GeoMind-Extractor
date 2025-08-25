#!/usr/bin/env python3
"""
综合地质文档分析脚本
结合智能知识合成和传统数据提取，生成包含图片的综合HTML报告
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from debug import (
    IntelligentKnowledgePipeline, LibrarianAgent, MapAnalystAgent, 
    GeochemistAgent, DataAnalystAgent, SynthesizerAgent,
    extract_full_text_from_pdf, chunk_text_by_paragraph,
    configure_agent, extract_metadata, extract_tables, extract_knowledge_graph,
    DocumentMetadata, Document, load_config
)
import webbrowser

def comprehensive_analysis(pdf_file_name="2008_MATABANE_FE3.pdf"):
    """运行综合分析：智能分析 + 传统分析 + 图片提取"""
    print(f"🚀 开始综合分析处理: {pdf_file_name}")
    
    # 配置文件路径
    config = load_config()
    raw_dir = Path(config["data_paths"]["raw_dir"])
    pdf_path = raw_dir / "theses-WAXI" / pdf_file_name
    
    if not pdf_path.exists():
        print(f"❌ 文件不存在: {pdf_path}")
        return
    
    print(f"📄 正在处理: {pdf_file_name}")
    
    # 第一步：运行智能分析流水线
    print("\n" + "="*60)
    print("🧠 第一部分：智能知识合成分析")
    print("="*60)
    
    pipeline = IntelligentKnowledgePipeline(mock_mode=False)
    # 手动替换API密钥
    pipeline.config['google_api_key'] = "AIzaSyDOxXa1YFX1_sPHHXv85iK_XDoa0VpfYEM"
    
    # 重新初始化agents with correct API key
    pipeline.librarian = LibrarianAgent(pipeline.config)
    pipeline.map_analyst = MapAnalystAgent(pipeline.config)
    pipeline.geochemist = GeochemistAgent(pipeline.config)
    pipeline.data_analyst = DataAnalystAgent(pipeline.config)
    pipeline.synthesizer = SynthesizerAgent(pipeline.config)
    
    intelligent_results = pipeline.process_document(str(pdf_path))
    
    # 第二步：运行传统分析流程
    print("\n" + "="*60)
    print("📊 第二部分：传统地质数据提取")
    print("="*60)
    
    traditional_results = run_traditional_analysis(pdf_path, config)
    
    # 第三步：创建综合HTML报告
    print("\n" + "="*60)
    print("📋 第三部分：生成综合报告")
    print("="*60)
    
    create_comprehensive_report(intelligent_results, traditional_results, pdf_file_name)
    
    print("✨ 综合分析处理完成！")

def run_traditional_analysis(pdf_path, config):
    """运行传统地质数据提取分析"""
    try:
        if not pdf_path.is_file():
            logging.error(f"File not found: {pdf_path}")
            return None
        
        logging.info(f"Processing document: {pdf_path.name}")
        full_text = extract_full_text_from_pdf(pdf_path)
        chunks = chunk_text_by_paragraph(full_text)
        
        if not chunks:
            logging.warning(f"No content extracted from {pdf_path.name}. Skipping.")
            return None
        
        # Configure the agent
        agent = configure_agent(
            agent_type=config["agent_config"]["agent_type"],
            agent_name=config["agent_config"]["agent_name"],
            api_key=config["google_api_key"]
        )

        # 1. Extract Metadata from the first chunk
        logging.info("Extracting metadata...")
        metadata = extract_metadata(agent, chunks[0])
        if not metadata:
            metadata = DocumentMetadata(
                title="Unknown", 
                authors=[], 
                publication_year=None, 
                keywords=[],
                confidence_score=0.0,
                raw_text=chunks[0] if chunks else "No content available"
            )

        # 2. Extract Tables from the full text
        logging.info("Extracting tables...")
        tables = extract_tables(agent, full_text)
        if not tables:
            tables = []

        # 3. Extract Knowledge Graph from the first few chunks
        logging.info("Extracting knowledge graph...")
        kg_text = " ".join(chunks[:5])
        knowledge_graph = extract_knowledge_graph(agent, kg_text)

        # Consolidate all extracted data into the final Document object
        traditional_results = Document(
            metadata=metadata,
            extracted_tables=tables,
            knowledge_graph=knowledge_graph,
            source_file=pdf_path.name,
            processing_timestamp_utc=datetime.now(timezone.utc).isoformat(),
            full_text=full_text[:1000] + "..." if len(full_text) > 1000 else full_text
        )
        
        print(f"✅ 传统分析完成: {pdf_path.name}")
        return traditional_results
        
    except Exception as e:
        print(f"❌ 传统分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_comprehensive_report(intelligent_results, traditional_results, pdf_name):
    """创建包含智能分析和传统分析的综合HTML报告"""
    
    # 获取图片信息
    image_info = intelligent_results.get("phase_0_extraction", {}).get("images", {})
    image_summary = image_info.get("extraction_summary", {})
    
    # 获取传统分析结果
    metadata = traditional_results.metadata if traditional_results else None
    tables = traditional_results.extracted_tables if traditional_results else []
    knowledge_graph = traditional_results.knowledge_graph if traditional_results else None
    
    # 获取智能分析结果
    synthesis = intelligent_results.get("phase_3_synthesis", {})
    summary = synthesis.get("synthesis_summary", {})
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>综合地质文档分析报告 - {pdf_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .section {{
            background: white;
            margin: 20px 0;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #444;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .section h3 {{
            color: #666;
            margin-top: 25px;
        }}
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        .metadata-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .metadata-label {{
            font-weight: bold;
            color: #555;
            margin-bottom: 5px;
        }}
        .table-container {{
            overflow-x: auto;
            margin: 15px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            background: white;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #667eea;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .image-gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .image-item {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .image-item:hover {{
            transform: translateY(-5px);
        }}
        .image-item img {{
            width: 100%;
            height: 200px;
            object-fit: contain;
            background: #f8f9fa;
        }}
        .image-info {{
            padding: 15px;
        }}
        .image-title {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        .image-details {{
            font-size: 0.9em;
            color: #666;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-item {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            display: block;
        }}
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .knowledge-graph {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
        }}
        .entity-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 10px 0;
        }}
        .entity-tag {{
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        .relationship-item {{
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }}
        .analysis-section {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
            text-align: center;
            margin-top: 30px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔬 综合地质文档分析报告</h1>
        <h2>{pdf_name}</h2>
        <p>智能知识合成 + 传统数据提取 + 图片分析</p>
    </div>

    <!-- 统计概览 -->
    <div class="section">
        <h2>📊 分析统计概览</h2>
        <div class="stats-grid">
            <div class="stat-item">
                <span class="stat-number">{image_summary.get('total_images', 0)}</span>
                <span class="stat-label">提取图片</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{len(tables)}</span>
                <span class="stat-label">数据表格</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{len(knowledge_graph.entities) if knowledge_graph else 0}</span>
                <span class="stat-label">知识实体</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{len(knowledge_graph.relationships) if knowledge_graph else 0}</span>
                <span class="stat-label">实体关系</span>
            </div>
        </div>
    </div>

    <!-- 智能分析结果 -->
    <div class="section">
        <h2>🧠 智能知识合成分析</h2>
        <div class="analysis-section">
            <h3>📋 文档评估</h3>
            <div class="metadata-grid">
                <div class="metadata-item">
                    <div class="metadata-label">文档价值评估</div>
                    <div>{summary.get('document_value_assessment', '未知')}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">数据完整性</div>
                    <div>{summary.get('data_completeness', '未知')}</div>
                </div>
            </div>
            
            <h3>🔍 关键贡献</h3>
            <ul>
"""
    
    # 添加关键贡献列表
    contributions = summary.get('key_contributions', [])
    if contributions:
        for contribution in contributions:
            html_content += f"                <li>{contribution}</li>\n"
    else:
        html_content += "                <li>暂无关键贡献信息</li>\n"
    
    html_content += """
            </ul>
        </div>
    </div>
"""
    
    # 文档基本信息
    if metadata:
        html_content += f"""
    <!-- 文档基本信息 -->
    <div class="section">
        <h2>📄 文档基本信息</h2>
        <div class="metadata-grid">
            <div class="metadata-item">
                <div class="metadata-label">标题</div>
                <div>{metadata.title or '未知'}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">作者</div>
                <div>{', '.join(metadata.authors) if metadata.authors else '未知'}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">关键词</div>
                <div>{', '.join(metadata.keywords) if metadata.keywords else '无'}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">出版年份</div>
                <div>{metadata.publication_year or '未知'}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">置信度</div>
                <div>{metadata.confidence_score:.2f}%</div>
            </div>
        </div>
    </div>
"""
    
    # 图片展示
    html_content += """
    <!-- 提取的图片 -->
    <div class="section">
        <h2>🖼️ 文档图片提取</h2>
"""
    
    if image_summary.get('total_images', 0) > 0:
        html_content += f"""
        <p>成功从文档中提取了 <strong>{image_summary.get('total_images', 0)}</strong> 张图片，总大小 <strong>{image_summary.get('total_size_mb', 0):.2f} MB</strong></p>
        <div class="image-gallery">
"""
        
        # 根据图片元数据生成图片展示
        images_dir = f"data/processed/images/{pdf_name.replace('.pdf', '')}"
        images_path = Path(images_dir)
        
        if images_path.exists():
            # 读取图片文件列表
            image_files = list(images_path.glob("*.jpeg")) + list(images_path.glob("*.jpg")) + list(images_path.glob("*.png"))
            
            # 显示前20张有意义的图片（过滤掉太小的图片）
            meaningful_images = [img for img in sorted(image_files) if img.stat().st_size > 5000][:20]
            
            for img_file in meaningful_images:
                # 创建相对路径用于HTML - 使用绝对路径
                try:
                    rel_path = str(img_file.relative_to(Path.cwd()))
                except ValueError:
                    # 如果无法创建相对路径，使用绝对路径
                    rel_path = str(img_file.absolute())
                
                # 从文件名提取页码信息
                filename = img_file.name
                page_match = filename.split('_page')[1].split('_')[0] if '_page' in filename else '未知'
                
                html_content += f"""
            <div class="image-item">
                <img src="{rel_path}" alt="Page {page_match} Image" onerror="this.style.display='none'">
                <div class="image-info">
                    <div class="image-title">页面 {page_match}</div>
                    <div class="image-details">
                        文件: {img_file.name}<br>
                        大小: {img_file.stat().st_size / 1024:.1f} KB
                    </div>
                </div>
            </div>
"""
        
        html_content += """
        </div>
"""
    else:
        html_content += "        <p>未发现图片内容</p>\n"
    
    html_content += "    </div>\n"
    
    # 表格数据
    if tables:
        html_content += """
    <!-- 提取的表格数据 -->
    <div class="section">
        <h2>📊 提取的表格数据</h2>
"""
        
        for i, table in enumerate(tables, 1):
            html_content += f"""
        <h3>表格 {i}</h3>
        <div class="table-container">
            <table>
"""
            
            if hasattr(table, 'headers') and table.headers:
                html_content += "                <thead><tr>\n"
                for header in table.headers:
                    html_content += f"                    <th>{header}</th>\n"
                html_content += "                </tr></thead>\n"
            
            if hasattr(table, 'rows') and table.rows:
                html_content += "                <tbody>\n"
                for row in table.rows[:10]:  # 限制显示前10行
                    html_content += "                <tr>\n"
                    for cell in row:
                        html_content += f"                    <td>{cell}</td>\n"
                    html_content += "                </tr>\n"
                html_content += "                </tbody>\n"
            
            html_content += """
            </table>
        </div>
"""
        
        html_content += "    </div>\n"
    
    # 知识图谱
    if knowledge_graph and hasattr(knowledge_graph, 'entities'):
        html_content += """
    <!-- 知识图谱关系 -->
    <div class="section">
        <h2>🕸️ 知识图谱关系</h2>
        <div class="knowledge-graph">
            <h3>🏷️ 识别的实体</h3>
            <div class="entity-list">
"""
        
        for entity in knowledge_graph.entities[:20]:  # 限制显示前20个实体
            html_content += f'                <span class="entity-tag">{entity.name} ({entity.type})</span>\n'
        
        html_content += """
            </div>
            
            <h3>🔗 实体关系</h3>
"""
        
        if hasattr(knowledge_graph, 'relationships'):
            for relationship in knowledge_graph.relationships[:10]:  # 限制显示前10个关系
                html_content += f"""
            <div class="relationship-item">
                <strong>{relationship.source}</strong> 
                → <em>{relationship.type}</em> → 
                <strong>{relationship.target}</strong>
                {f'<br><small>置信度: {relationship.confidence}</small>' if hasattr(relationship, 'confidence') else ''}
            </div>
"""
        
        html_content += """
        </div>
    </div>
"""
    
    # 时间戳
    html_content += f"""
    <div class="timestamp">
        <p>报告生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
        <p>分析引擎: 智能知识合成流水线 v2.0 + 传统地质数据提取系统</p>
    </div>
</body>
</html>
"""
    
    # 保存综合报告
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = processed_dir / f"综合分析报告_{pdf_name.replace('.pdf', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📋 综合报告已生成: {report_path}")
    
    # 强制在浏览器中打开新报告
    try:
        webbrowser.open(f'file://{report_path.absolute()}')
        print(f"🌐 报告已在浏览器中打开: {report_path}")
    except Exception as e:
        print(f"⚠️ 无法自动打开浏览器: {e}")
    
    return report_path

if __name__ == "__main__":
    import sys
    
    # 检查命令行参数
    pdf_file = "2008_MATABANE_FE3.pdf"
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    
    print(f"🚀 启动综合分析模式...")
    comprehensive_analysis(pdf_file)
