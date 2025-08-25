#!/usr/bin/env python3
"""
真实API测试脚本 - 智能知识合成流水线
使用真实的Google Gemini API处理真实的地质论文
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import webbrowser
import json

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 导入智能流水线
from debug import IntelligentKnowledgePipeline, create_intelligent_html_report

def test_real_api():
    """
    使用真实API测试智能知识合成流水线
    """
    
    print("🚀 启动智能知识合成流水线 - 真实API模式")
    print("🔑 使用Google Gemini API处理真实地质论文")
    print("="*60)
    
    # 初始化流水线（真实API模式）
    try:
        pipeline = IntelligentKnowledgePipeline(mock_mode=False)
        print("✅ 流水线初始化成功，已配置Google Gemini API")
    except Exception as e:
        print(f"❌ 流水线初始化失败: {e}")
        return
    
    # 选择测试PDF
    test_pdf = "data/raw/theses-WAXI/2015_Fougerouse_Geometry and genesis of the giant Obuasi gold deposit, Ghana revised.pdf"
    
    if not Path(test_pdf).exists():
        print(f"❌ 找不到测试PDF: {test_pdf}")
        print("可用的PDF文件:")
        for pdf_file in Path("data/raw/theses-WAXI/").glob("*.pdf"):
            print(f"  - {pdf_file.name}")
        return
    
    print(f"📁 正在处理: {Path(test_pdf).name}")
    print(f"📄 文档路径: {test_pdf}")
    
    try:
        print("\n🔄 开始三阶段智能分析...")
        
        # 运行完整的智能流水线
        results = pipeline.process_document(test_pdf)
        
        if "error" in results:
            print(f"❌ 流水线处理失败: {results['error']}")
            return
        
        print("\n✅ 流水线处理完成！正在生成报告...")
        
        # 生成增强HTML报告
        pdf_name = Path(test_pdf).stem
        html_content = create_intelligent_html_report(results, pdf_name)
        
        # 保存报告
        report_path = f"真实API分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📊 HTML报告已生成: {report_path}")
        
        # 保存详细JSON结果
        json_path = f"真实API分析数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 详细数据已保存: {json_path}")
        
        # 在浏览器中打开报告
        full_path = Path(report_path).absolute()
        webbrowser.open(f'file://{full_path}')
        print(f"🌐 正在浏览器中打开报告...")
        
        # 显示智能分析摘要
        synthesis = results.get("phase_3_synthesis", {})
        summary = synthesis.get("synthesis_summary", {})
        
        print(f"\n📊 真实论文智能分析摘要:")
        print(f"  📋 文档价值评估: {summary.get('document_value_assessment', '未知')}")
        print(f"  📊 数据完整性: {summary.get('data_completeness', '未知')}")
        print(f"  🗺️  空间覆盖范围: {summary.get('spatial_coverage', '未知')}")
        print(f"  🔍 关键知识贡献数量: {len(summary.get('key_contributions', []))}")
        
        quality = synthesis.get("quality_metrics", {})
        print(f"  ✅ 交叉验证得分: {quality.get('cross_validation_score', 'N/A')}")
        print(f"  🔬 数据可靠性: {quality.get('data_reliability', 'N/A')}")
        print(f"  📈 完整性百分比: {quality.get('completeness_percentage', 'N/A')}%")
        
        # 显示关键知识贡献
        contributions = summary.get('key_contributions', [])
        if contributions:
            print(f"\n🎯 从论文中提取的关键知识贡献:")
            for i, contribution in enumerate(contributions, 1):
                print(f"     {i}. {contribution}")
        
        # 显示第一阶段分析结果
        phase1 = results.get("phase_1_triage", {})
        doc_overview = phase1.get("document_overview", {})
        content_index = phase1.get("content_index", {})
        
        print(f"\n📋 第一阶段 - 文档分析结果:")
        print(f"  📄 文档类型: {doc_overview.get('document_type', '未知')}")
        print(f"  🎯 主要焦点: {doc_overview.get('primary_focus', '未知')}")
        print(f"  🔬 地质领域: {doc_overview.get('geological_domain', '未知')}")
        print(f"  🌐 语言: {doc_overview.get('language', '未知')}")
        print(f"  🗺️  发现地质图: {len(content_index.get('geological_maps', []))}个")
        print(f"  📊 发现数据表: {len(content_index.get('data_tables', []))}个")
        print(f"  📝 分析性章节: {len(content_index.get('analytical_sections', []))}个")
        
        # 显示第二阶段分析结果
        phase2 = results.get("phase_2_expert_analysis", {})
        spatial_analysis = phase2.get("spatial_analysis", {})
        geochem_analysis = phase2.get("geochemical_analysis", {})
        data_analysis = phase2.get("data_analysis", {})
        
        print(f"\n🔬 第二阶段 - 专家分析结果:")
        print(f"  🗺️  空间分析师提取:")
        print(f"      📍 地点: {len(spatial_analysis.get('locations', []))}个")
        print(f"      🗿 地质单元: {len(spatial_analysis.get('geological_units', []))}个")
        print(f"      🔧 构造特征: {len(spatial_analysis.get('structural_features', []))}个")
        
        print(f"  ⚗️  地球化学家分析:")
        print(f"      🧪 地球化学解释: {len(geochem_analysis.get('geochemical_interpretations', []))}个")
        print(f"      🔬 分析方法: {len(geochem_analysis.get('analytical_methods', []))}个")
        print(f"      🎯 化学特征: {len(geochem_analysis.get('geochemical_signatures', []))}个")
        
        print(f"  📊 数据分析师提取:")
        print(f"      📋 数据表: {data_analysis.get('data_quality_assessment', {}).get('total_tables_found', 0)}个")
        print(f"      📍 坐标数据: {'✅' if data_analysis.get('data_quality_assessment', {}).get('coordinate_data_present', False) else '❌'}")
        print(f"      ⚗️  地球化学数据: {'✅' if data_analysis.get('data_quality_assessment', {}).get('geochemical_data_present', False) else '❌'}")
        
        # 显示数据库就绪记录
        db_records = synthesis.get("database_ready_records", {})
        print(f"\n💾 第三阶段 - 数据库就绪记录:")
        print(f"  📍 地点记录: {len(db_records.get('location_records', []))}条")
        print(f"  ⚗️  地球化学记录: {len(db_records.get('geochemistry_records', []))}条")
        print(f"  🗿 地质单元记录: {len(db_records.get('geological_units_records', []))}条")
        
        print(f"\n🎉 真实论文智能知识合成完成!")
        print(f"   🔍 这是从真实地质论文中提取的实际数据")
        print(f"   📊 所有结果都经过三阶段智能分析和交叉验证")
        print(f"   💾 数据已结构化，可直接导入地理数据库")
        
    except Exception as e:
        print(f"❌ 真实API处理失败: {e}")
        print(f"🔧 可能的原因:")
        print(f"   - API密钥无效或过期")
        print(f"   - 网络连接问题")
        print(f"   - API配额不足")
        print(f"   - 文档过大或格式问题")
        import traceback
        traceback.print_exc()

def quick_test_api():
    """
    快速测试API连接
    """
    print("🔑 快速测试Google Gemini API连接...")
    
    try:
        from config import load_config
        from entity_extraction.llm_extractor import configure_agent
        
        config = load_config()
        agent = configure_agent(
            config.get('agent_config', {}).get('agent_type', 'gemini'),
            config.get('agent_config', {}).get('agent_name', 'gemini-1.5-flash'),
            config.get('google_api_key', '')
        )
        
        # 简单测试请求
        test_response = agent.process("请简单回答：你好")
        print(f"✅ API连接成功！")
        print(f"📝 测试响应: {test_response}")
        return True
        
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

if __name__ == "__main__":
    # 首先测试API连接
    if quick_test_api():
        print("\n" + "="*60 + "\n")
        # 如果API连接成功，运行完整测试
        test_real_api()
    else:
        print("\n❌ 无法连接到API，请检查配置")
        print("🔧 请确认:")
        print("   1. Google API密钥是否正确")
        print("   2. API密钥是否有效且未过期")
        print("   3. 网络连接是否正常")
        print("   4. API配额是否充足")
