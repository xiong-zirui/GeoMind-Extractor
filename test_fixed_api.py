#!/usr/bin/env python3
"""
修复版真实API测试脚本
直接使用正确的API密钥，绕过配置文件问题
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import webbrowser
import json

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_with_fixed_api():
    """
    使用修复的API配置测试智能流水线
    """
    
    print("🚀 启动智能知识合成流水线 - 修复版API测试")
    print("🔑 使用正确的Google Gemini API密钥")
    print("="*60)
    
    # 直接导入并修改配置
    try:
        from config import load_config
        config = load_config()
        
        # 强制使用正确的API密钥
        config['google_api_key'] = "AIzaSyDOxXa1YFX1_sPHHXv85iK_XDoa0VpfYEM"
        
        print(f"✅ 配置加载成功，API密钥已修正")
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return
    
    # 测试API连接
    print("🔑 测试API连接...")
    try:
        from entity_extraction.llm_extractor import configure_agent
        
        agent = configure_agent(
            config.get('agent_config', {}).get('agent_type', 'gemini'),
            config.get('agent_config', {}).get('agent_name', 'gemini-1.5-flash'),
            config.get('google_api_key', '')
        )
        
        # 简单测试
        test_response = agent.process("请回答：测试成功")
        print(f"✅ API连接测试成功！")
        print(f"📝 测试响应: {test_response}")
        
    except Exception as e:
        print(f"❌ API连接仍然失败: {e}")
        return
    
    # 运行智能流水线
    print("\n🔄 开始运行智能知识合成流水线...")
    
    try:
        # 创建修正版的流水线类
        class FixedIntelligentKnowledgePipeline:
            def __init__(self):
                self.config = config  # 使用修正的配置
                
                # 重新导入agent classes
                from debug import LibrarianAgent, MapAnalystAgent, GeochemistAgent, DataAnalystAgent, SynthesizerAgent
                
                # 用修正的配置初始化所有agents
                self.librarian = LibrarianAgent(self.config)
                self.map_analyst = MapAnalystAgent(self.config)
                self.geochemist = GeochemistAgent(self.config)
                self.data_analyst = DataAnalystAgent(self.config)
                self.synthesizer = SynthesizerAgent(self.config)
            
            def process_document(self, pdf_path: str):
                # 从debug.py导入处理逻辑
                from debug import IntelligentKnowledgePipeline
                original_pipeline = IntelligentKnowledgePipeline(mock_mode=False)
                
                # 替换agents
                original_pipeline.librarian = self.librarian
                original_pipeline.map_analyst = self.map_analyst
                original_pipeline.geochemist = self.geochemist
                original_pipeline.data_analyst = self.data_analyst
                original_pipeline.synthesizer = self.synthesizer
                
                return original_pipeline.process_document(pdf_path)
        
        # 初始化修正版流水线
        pipeline = FixedIntelligentKnowledgePipeline()
        
        # 测试文档
        test_pdf = "data/raw/theses-WAXI/2015_Fougerouse_Geometry and genesis of the giant Obuasi gold deposit, Ghana revised.pdf"
        
        if not Path(test_pdf).exists():
            print(f"❌ 找不到测试PDF: {test_pdf}")
            return
        
        print(f"📁 正在处理: {Path(test_pdf).name}")
        
        # 运行流水线
        results = pipeline.process_document(test_pdf)
        
        if "error" in results:
            print(f"❌ 流水线处理失败: {results['error']}")
            return
        
        print("\n✅ 真实API流水线处理完成！")
        
        # 生成报告
        from debug import create_intelligent_html_report
        
        pdf_name = Path(test_pdf).stem
        html_content = create_intelligent_html_report(results, pdf_name)
        
        # 保存报告
        report_path = f"真实API智能分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📊 HTML报告已生成: {report_path}")
        
        # 保存JSON数据
        json_path = f"真实API智能分析数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 详细数据已保存: {json_path}")
        
        # 打开报告
        full_path = Path(report_path).absolute()
        webbrowser.open(f'file://{full_path}')
        print(f"🌐 正在浏览器中打开报告...")
        
        # 显示真实分析结果摘要
        synthesis = results.get("phase_3_synthesis", {})
        summary = synthesis.get("synthesis_summary", {})
        
        print(f"\n📊 真实论文智能分析结果摘要:")
        print(f"  📋 文档价值评估: {summary.get('document_value_assessment', '未知')}")
        print(f"  📊 数据完整性: {summary.get('data_completeness', '未知')}")
        print(f"  🗺️  空间覆盖范围: {summary.get('spatial_coverage', '未知')}")
        
        # 显示从真实论文提取的关键知识
        contributions = summary.get('key_contributions', [])
        if contributions:
            print(f"\n🎯 从真实论文中提取的关键知识:")
            for i, contribution in enumerate(contributions, 1):
                print(f"     {i}. {contribution}")
        
        # 显示真实提取的数据统计
        phase1 = results.get("phase_1_triage", {})
        content_index = phase1.get("content_index", {})
        
        print(f"\n📋 真实文档分析统计:")
        print(f"  🗺️  地质图识别: {len(content_index.get('geological_maps', []))}个")
        print(f"  📊 数据表识别: {len(content_index.get('data_tables', []))}个")
        print(f"  📝 分析章节: {len(content_index.get('analytical_sections', []))}个")
        
        print(f"\n🎉 真实API智能知识合成成功完成!")
        print(f"   ✨ 这是从真实地质论文中提取的实际数据")
        print(f"   🔍 所有结果都通过Google Gemini API智能分析得出")
        print(f"   💾 数据已结构化，可直接用于地理数据库")
        
    except Exception as e:
        print(f"❌ 智能流水线处理失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_fixed_api()
