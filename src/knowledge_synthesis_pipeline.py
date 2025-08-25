"""
知识合成流水线 (Knowledge Synthesis Pipeline)
协调三阶段的智能地质数据提取和知识合成流程
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from config import load_config
from document_processing.pdf_processor import extract_full_text_from_pdf, chunk_text_by_paragraph
from entity_extraction.llm_extractor import extract_metadata, extract_tables, extract_knowledge_graph, configure_agent

# 导入新的Agent
from agents.librarian_agent import LibrarianAgent
from agents.map_analyst_agent import MapAnalystAgent
from agents.geochemist_agent import GeochemistAgent
from agents.data_analyst_agent import DataAnalystAgent
from agents.synthesizer_agent import SynthesizerAgent

from models import Document


class KnowledgeSynthesisPipeline:
    """知识合成流水线主类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent_manager = configure_agent(
            agent_type=config["agent_config"]["agent_type"],
            agent_name=config["agent_config"]["agent_name"],
            api_key=config["google_api_key"]
        )
        
        # 初始化各个Agent
        self.librarian_agent = LibrarianAgent(agent_manager=self.agent_manager)
        self.map_analyst_agent = MapAnalystAgent(agent_manager=self.agent_manager)
        self.geochemist_agent = GeochemistAgent(agent_manager=self.agent_manager)
        self.data_analyst_agent = DataAnalystAgent(agent_manager=self.agent_manager)
        self.synthesizer_agent = SynthesizerAgent(agent_manager=self.agent_manager)
        
        # 设置日志
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
    def process_document(self, pdf_path: Path) -> Dict[str, Any]:
        """
        处理单个PDF文档的完整流水线
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            包含所有处理结果的字典
        """
        self.logger.info(f"🚀 开始处理文档: {pdf_path.name}")
        
        try:
            # === 预处理阶段 ===
            preprocessing_result = self._preprocess_document(pdf_path)
            if not preprocessing_result:
                return {'status': 'failed', 'stage': 'preprocessing'}
            
            # === 第一阶段：智能分诊与任务规划 ===
            self.logger.info("📋 阶段 1: 智能分诊与任务规划")
            triage_result = self._stage1_intelligent_triage(preprocessing_result)
            
            # === 第二阶段：领域专家深度分析 ===
            self.logger.info("🔬 阶段 2: 领域专家深度分析")
            expert_analysis_result = self._stage2_expert_analysis(preprocessing_result, triage_result)
            
            # === 第三阶段：知识融合与数据库映射 ===
            self.logger.info("🧠 阶段 3: 知识融合与数据库映射")
            synthesis_result = self._stage3_knowledge_synthesis(
                preprocessing_result, triage_result, expert_analysis_result
            )
            
            # === 整合最终结果 ===
            final_result = self._compile_final_result(
                pdf_path, preprocessing_result, triage_result, 
                expert_analysis_result, synthesis_result
            )
            
            self.logger.info(f"✅ 文档处理完成: {pdf_path.name}")
            return final_result
            
        except Exception as e:
            self.logger.error(f"❌ 文档处理失败: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'document': pdf_path.name
            }
    
    def _preprocess_document(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """预处理文档"""
        try:
            self.logger.info("📄 提取PDF文本...")
            full_text = extract_full_text_from_pdf(pdf_path)
            
            if not full_text or len(full_text.strip()) < 100:
                self.logger.warning("PDF文本提取失败或内容过少")
                return None
            
            self.logger.info("📝 分段处理文本...")
            chunks = chunk_text_by_paragraph(full_text)
            
            if not chunks:
                self.logger.warning("文本分段失败")
                return None
            
            self.logger.info(f"✅ 预处理完成: {len(full_text)} 字符, {len(chunks)} 段落")
            
            return {
                'pdf_path': str(pdf_path),
                'full_text': full_text,
                'chunks': chunks,
                'preprocessing_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"预处理失败: {e}")
            return None
    
    def _stage1_intelligent_triage(self, preprocessing_result: Dict[str, Any]) -> Dict[str, Any]:
        """第一阶段：智能分诊与任务规划"""
        try:
            # 调用Librarian Agent
            librarian_input = {
                'pdf_path': preprocessing_result['pdf_path'],
                'full_text': preprocessing_result['full_text'],
                'chunks': preprocessing_result['chunks']
            }
            
            librarian_result = self.librarian_agent.process(librarian_input)
            
            self.logger.info(f"📋 任务规划完成: {len(librarian_result.get('task_plan', []))} 个任务")
            
            return {
                'content_index': librarian_result.get('content_index'),
                'task_plan': librarian_result.get('task_plan', []),
                'status': librarian_result.get('status', 'unknown'),
                'stage1_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"第一阶段失败: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _stage2_expert_analysis(self, preprocessing_result: Dict[str, Any], 
                              triage_result: Dict[str, Any]) -> Dict[str, Any]:
        """第二阶段：领域专家深度分析"""
        try:
            # 首先提取基础表格数据（用于后续分析）
            base_tables = self._extract_base_tables(preprocessing_result)
            
            # 根据任务计划并行执行专家分析
            task_plan = triage_result.get('task_plan', [])
            content_index = triage_result.get('content_index')
            
            # 准备专家分析的输入数据
            analysis_input = {
                'content_units': content_index.content_units if content_index else [],
                'full_text': preprocessing_result['full_text'],
                'chunks': preprocessing_result['chunks'],
                'data_tables': base_tables
            }
            
            # 并行执行专家分析
            expert_results = self._run_expert_agents_parallel(analysis_input, task_plan)
            
            return {
                'map_analyst_result': expert_results.get('map_analyst', {}),
                'geochemist_result': expert_results.get('geochemist', {}),
                'data_analyst_result': expert_results.get('data_analyst', {}),
                'base_tables': base_tables,
                'stage2_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"第二阶段失败: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _extract_base_tables(self, preprocessing_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取基础表格数据"""
        try:
            self.logger.info("📊 提取基础表格数据...")
            tables = extract_tables(self.agent_manager, preprocessing_result['full_text'])
            
            # 转换为字典格式
            base_tables = []
            for table in tables:
                if hasattr(table, 'model_dump'):
                    base_tables.append(table.model_dump())
                elif isinstance(table, dict):
                    base_tables.append(table)
            
            self.logger.info(f"📊 提取到 {len(base_tables)} 个基础表格")
            return base_tables
            
        except Exception as e:
            self.logger.warning(f"基础表格提取失败: {e}")
            return []
    
    def _run_expert_agents_parallel(self, analysis_input: Dict[str, Any], 
                                  task_plan: List[Any]) -> Dict[str, Any]:
        """并行运行专家Agent"""
        expert_results = {}
        
        # 确定需要运行的专家Agent
        agents_to_run = set()
        for task in task_plan:
            if hasattr(task, 'agent_type'):
                agents_to_run.add(task.agent_type)
            elif isinstance(task, dict):
                agents_to_run.add(task.get('agent_type', ''))
        
        # 使用线程池并行执行
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            
            if 'map_analyst' in agents_to_run:
                futures['map_analyst'] = executor.submit(
                    self.map_analyst_agent.process, analysis_input
                )
            
            if 'geochemist' in agents_to_run:
                futures['geochemist'] = executor.submit(
                    self.geochemist_agent.process, analysis_input
                )
            
            if 'data_analyst' in agents_to_run:
                # Data Analyst需要原始表格数据
                data_input = {**analysis_input, 'raw_tables': analysis_input['data_tables']}
                futures['data_analyst'] = executor.submit(
                    self.data_analyst_agent.process, data_input
                )
            
            # 收集结果
            for agent_name, future in futures.items():
                try:
                    result = future.result(timeout=300)  # 5分钟超时
                    expert_results[agent_name] = result
                    self.logger.info(f"✅ {agent_name} 分析完成")
                except Exception as e:
                    self.logger.error(f"❌ {agent_name} 分析失败: {e}")
                    expert_results[agent_name] = {'status': 'failed', 'error': str(e)}
        
        return expert_results
    
    def _stage3_knowledge_synthesis(self, preprocessing_result: Dict[str, Any],
                                  triage_result: Dict[str, Any], 
                                  expert_analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """第三阶段：知识融合与数据库映射"""
        try:
            # 提取原始知识图谱（如果需要）
            original_kg = self._extract_original_knowledge_graph(preprocessing_result)
            
            # 准备Synthesizer输入
            synthesis_input = {
                'document_source': Path(preprocessing_result['pdf_path']).name,
                'map_analyst_result': expert_analysis_result.get('map_analyst_result', {}),
                'geochemist_result': expert_analysis_result.get('geochemist_result', {}),
                'data_analyst_result': expert_analysis_result.get('data_analyst_result', {}),
                'original_knowledge_graph': original_kg
            }
            
            # 调用Synthesizer Agent
            synthesis_result = self.synthesizer_agent.process(synthesis_input)
            
            self.logger.info(f"🧠 知识合成完成: {synthesis_result.get('database_records_count', 0)} 条数据库记录")
            
            return {
                'synthesized_knowledge': synthesis_result.get('synthesized_knowledge'),
                'database_records_count': synthesis_result.get('database_records_count', 0),
                'overall_confidence': synthesis_result.get('overall_confidence', 0.0),
                'processing_status': synthesis_result.get('processing_status', 'unknown'),
                'stage3_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"第三阶段失败: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _extract_original_knowledge_graph(self, preprocessing_result: Dict[str, Any]) -> Dict[str, Any]:
        """提取原始知识图谱"""
        try:
            # 使用前几个chunks提取知识图谱
            kg_text = " ".join(preprocessing_result['chunks'][:5])
            kg = extract_knowledge_graph(self.agent_manager, kg_text)
            
            if kg and hasattr(kg, 'model_dump'):
                return kg.model_dump()
            elif isinstance(kg, dict):
                return kg
            else:
                return {}
                
        except Exception as e:
            self.logger.warning(f"原始知识图谱提取失败: {e}")
            return {}
    
    def _compile_final_result(self, pdf_path: Path, preprocessing_result: Dict[str, Any],
                            triage_result: Dict[str, Any], expert_analysis_result: Dict[str, Any],
                            synthesis_result: Dict[str, Any]) -> Dict[str, Any]:
        """编译最终结果"""
        
        # 创建传统Document对象（向后兼容）
        try:
            # 提取基础元数据
            metadata = extract_metadata(self.agent_manager, preprocessing_result['chunks'][0])
            
            document = Document(
                metadata=metadata,
                extracted_tables=expert_analysis_result.get('base_tables', []),
                knowledge_graph=synthesis_result.get('synthesized_knowledge', {}).get('knowledge_graph', {}),
                source_file=pdf_path.name,
                processing_timestamp_utc=datetime.now().isoformat(),
                full_text=preprocessing_result['full_text'][:1000] + "..."
            )
        except Exception as e:
            self.logger.warning(f"创建Document对象失败: {e}")
            document = None
        
        # 编译完整结果
        final_result = {
            'status': 'success',
            'document': document,
            'pipeline_results': {
                'stage1_triage': triage_result,
                'stage2_expert_analysis': expert_analysis_result,
                'stage3_synthesis': synthesis_result
            },
            'summary': {
                'document_name': pdf_path.name,
                'processing_timestamp': datetime.now().isoformat(),
                'total_tasks_planned': len(triage_result.get('task_plan', [])),
                'spatial_features_count': expert_analysis_result.get('map_analyst_result', {}).get('feature_count', 0),
                'geochemical_conclusions_count': expert_analysis_result.get('geochemist_result', {}).get('conclusions_count', 0),
                'standardized_tables_count': expert_analysis_result.get('data_analyst_result', {}).get('standardized_tables_count', 0),
                'database_records_count': synthesis_result.get('database_records_count', 0),
                'overall_confidence': synthesis_result.get('overall_confidence', 0.0)
            }
        }
        
        return final_result
    
    def save_results(self, final_result: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        """保存处理结果"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        document_name = final_result['summary']['document_name']
        base_name = Path(document_name).stem
        
        saved_files = {}
        
        try:
            # 1. 保存完整的流水线结果
            pipeline_file = output_dir / f"{base_name}_pipeline_result.json"
            with open(pipeline_file, 'w', encoding='utf-8') as f:
                # 使用自定义编码器处理复杂对象
                json.dump(final_result, f, indent=2, default=self._json_serializer, ensure_ascii=False)
            saved_files['pipeline_result'] = str(pipeline_file)
            
            # 2. 保存数据库记录（如果有）
            synthesis_result = final_result.get('pipeline_results', {}).get('stage3_synthesis', {})
            synthesized_knowledge = synthesis_result.get('synthesized_knowledge')
            
            if synthesized_knowledge and hasattr(synthesized_knowledge, 'database_records'):
                db_records_file = output_dir / f"{base_name}_database_records.json"
                records_data = [
                    record.model_dump() if hasattr(record, 'model_dump') else record
                    for record in synthesized_knowledge.database_records
                ]
                with open(db_records_file, 'w', encoding='utf-8') as f:
                    json.dump(records_data, f, indent=2, ensure_ascii=False)
                saved_files['database_records'] = str(db_records_file)
            
            # 3. 保存传统格式（向后兼容）
            if final_result.get('document'):
                traditional_file = output_dir / f"{base_name}_traditional.json"
                with open(traditional_file, 'w', encoding='utf-8') as f:
                    document_data = final_result['document']
                    if hasattr(document_data, 'model_dump_json'):
                        f.write(document_data.model_dump_json(indent=2))
                    else:
                        json.dump(document_data, f, indent=2, default=self._json_serializer, ensure_ascii=False)
                saved_files['traditional_format'] = str(traditional_file)
            
            self.logger.info(f"💾 结果已保存到: {output_dir}")
            
        except Exception as e:
            self.logger.error(f"保存结果失败: {e}")
            saved_files['error'] = str(e)
        
        return saved_files
    
    def _json_serializer(self, obj):
        """JSON序列化器"""
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
