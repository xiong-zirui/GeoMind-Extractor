"""
Librarian Agent - 智能分诊与任务规划
负责扫描整个文档，生成内容索引，并制定后续分析计划
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from pydantic import BaseModel, Field

from .base import BaseAgent
from ..models import DocumentContentIndex, AnalysisTask, TaskType


class ContentUnit(BaseModel):
    """文档内容单元"""
    page_number: int
    content_type: str  # 'text', 'figure', 'table', 'map'
    title: Optional[str] = None
    description: str
    keywords: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    content_preview: str = ""  # 内容预览


class DocumentContentIndex(BaseModel):
    """文档内容索引"""
    document_name: str
    total_pages: int
    content_units: List[ContentUnit]
    processing_timestamp: str
    confidence_score: float = Field(ge=0.0, le=1.0)


class AnalysisTask(BaseModel):
    """分析任务"""
    task_id: str
    task_type: TaskType
    agent_type: str  # 'map_analyst', 'geochemist', 'data_analyst'
    priority: int = Field(ge=1, le=10)  # 1最高优先级，10最低
    input_pages: List[int]
    input_content_units: List[str]  # content unit ids
    expected_output_type: str
    processing_instructions: str


class TaskType(str):
    MAP_ANALYSIS = "map_analysis"
    GEOCHEMICAL_ANALYSIS = "geochemical_analysis"  
    DATA_EXTRACTION = "data_extraction"
    TEXT_SYNTHESIS = "text_synthesis"


class LibrarianAgent(BaseAgent):
    """图书管理员Agent - 智能分诊与任务规划"""
    
    def __init__(self, name: str = "Librarian", **kwargs):
        super().__init__(name, **kwargs)
        self.agent_manager = kwargs.get('agent_manager')
        
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        处理PDF文档，生成内容索引和任务计划
        
        Args:
            input_data: 包含PDF路径和提取的文本的字典
            
        Returns:
            包含内容索引和任务计划的字典
        """
        pdf_path = input_data.get('pdf_path')
        full_text = input_data.get('full_text')
        chunks = input_data.get('chunks', [])
        
        logging.info(f"Librarian Agent 开始分析文档: {pdf_path}")
        
        # 1. 生成文档内容索引
        content_index = self._generate_content_index(full_text, chunks, pdf_path)
        
        # 2. 制定分析任务计划
        task_plan = self._create_task_plan(content_index)
        
        # 3. 返回结果
        return {
            'content_index': content_index,
            'task_plan': task_plan,
            'status': 'success'
        }
    
    def _generate_content_index(self, full_text: str, chunks: List[str], pdf_path: str) -> DocumentContentIndex:
        """生成文档内容索引"""
        
        # 使用LLM分析文档结构
        prompt = self._get_content_analysis_prompt()
        
        # 准备分析用的文本样本（前几个chunks）
        analysis_text = "\n\n".join(chunks[:10])  # 使用前10个chunks
        
        try:
            # 调用LLM进行内容分析
            result = self.agent_manager.generate_content(
                prompt + "\n\n文档内容:\n" + analysis_text
            )
            
            # 解析LLM返回的结果
            content_units = self._parse_content_analysis_result(result, chunks)
            
            # 创建内容索引
            content_index = DocumentContentIndex(
                document_name=Path(pdf_path).stem,
                total_pages=len(chunks),  # 简化处理，用chunks数量代替页数
                content_units=content_units,
                processing_timestamp=str(Path().cwd()),
                confidence_score=0.8  # 默认置信度
            )
            
            logging.info(f"生成内容索引完成，发现 {len(content_units)} 个内容单元")
            return content_index
            
        except Exception as e:
            logging.error(f"生成内容索引失败: {e}")
            # 返回基础索引
            return self._create_basic_index(pdf_path, chunks)
    
    def _get_content_analysis_prompt(self) -> str:
        """获取内容分析的prompt"""
        return """
你是一位经验丰富的地质文献分析专家。请分析以下地质学文档，识别并分类其中的关键内容单元。

请按以下格式输出JSON结果：
{
    "content_units": [
        {
            "page_number": 页码或章节号,
            "content_type": "类型(text/figure/table/map)",
            "title": "标题或名称",
            "description": "内容描述",
            "keywords": ["关键词1", "关键词2"],
            "confidence_score": 置信度(0.0-1.0),
            "content_preview": "内容预览"
        }
    ]
}

重点识别以下类型的内容：
1. 地质图 (geological maps) - 包含地质构造、岩性分布等空间信息
2. 数据表格 (data tables) - 包含钻孔数据、地球化学分析数据等
3. 地球化学分析文本 - 包含岩石类型、化学成分分析等
4. 矿区描述 - 包含矿点位置、矿物成分等信息

请确保输出有效的JSON格式。
"""
    
    def _parse_content_analysis_result(self, result: str, chunks: List[str]) -> List[ContentUnit]:
        """解析LLM内容分析结果"""
        try:
            # 尝试解析JSON结果
            parsed_result = json.loads(result)
            content_units = []
            
            for unit_data in parsed_result.get('content_units', []):
                content_unit = ContentUnit(
                    page_number=unit_data.get('page_number', 1),
                    content_type=unit_data.get('content_type', 'text'),
                    title=unit_data.get('title'),
                    description=unit_data.get('description', ''),
                    keywords=unit_data.get('keywords', []),
                    confidence_score=unit_data.get('confidence_score', 0.5),
                    content_preview=unit_data.get('content_preview', '')
                )
                content_units.append(content_unit)
            
            return content_units
            
        except (json.JSONDecodeError, KeyError) as e:
            logging.warning(f"解析LLM结果失败: {e}，使用默认分析")
            return self._create_default_content_units(chunks)
    
    def _create_default_content_units(self, chunks: List[str]) -> List[ContentUnit]:
        """创建默认的内容单元（当LLM解析失败时）"""
        content_units = []
        
        for i, chunk in enumerate(chunks[:20]):  # 限制在前20个chunks
            # 简单的关键词检测
            content_type = "text"
            keywords = []
            
            chunk_lower = chunk.lower()
            
            # 检测地质图
            if any(word in chunk_lower for word in ['figure', 'fig', 'carte', 'map', 'géologique']):
                content_type = "figure"
                keywords.append("geological_map")
            
            # 检测表格
            elif any(word in chunk_lower for word in ['table', 'tableau', 'data', 'analysis']):
                content_type = "table"
                keywords.append("data_table")
            
            # 检测地球化学内容
            elif any(word in chunk_lower for word in ['geochemical', 'géochimique', 'chemical', 'composition']):
                content_type = "text"
                keywords.append("geochemistry")
            
            content_unit = ContentUnit(
                page_number=i + 1,
                content_type=content_type,
                title=f"内容单元 {i+1}",
                description=chunk[:200] + "..." if len(chunk) > 200 else chunk,
                keywords=keywords,
                confidence_score=0.6,
                content_preview=chunk[:100] + "..." if len(chunk) > 100 else chunk
            )
            content_units.append(content_unit)
        
        return content_units
    
    def _create_basic_index(self, pdf_path: str, chunks: List[str]) -> DocumentContentIndex:
        """创建基础内容索引（错误处理）"""
        content_units = self._create_default_content_units(chunks)
        
        return DocumentContentIndex(
            document_name=Path(pdf_path).stem,
            total_pages=len(chunks),
            content_units=content_units,
            processing_timestamp="error_fallback",
            confidence_score=0.3
        )
    
    def _create_task_plan(self, content_index: DocumentContentIndex) -> List[AnalysisTask]:
        """根据内容索引创建分析任务计划"""
        tasks = []
        task_counter = 1
        
        # 1. 创建地图分析任务
        map_units = [unit for unit in content_index.content_units 
                    if unit.content_type == "figure" or "geological_map" in unit.keywords]
        
        if map_units:
            map_task = AnalysisTask(
                task_id=f"task_{task_counter:03d}",
                task_type=TaskType.MAP_ANALYSIS,
                agent_type="map_analyst",
                priority=1,  # 最高优先级
                input_pages=[unit.page_number for unit in map_units],
                input_content_units=[f"unit_{i}" for i in range(len(map_units))],
                expected_output_type="geojson",
                processing_instructions="提取地质图中的空间要素，包括矿点、断层、岩性单元等，转换为GeoJSON格式"
            )
            tasks.append(map_task)
            task_counter += 1
        
        # 2. 创建数据提取任务
        table_units = [unit for unit in content_index.content_units 
                      if unit.content_type == "table" or "data_table" in unit.keywords]
        
        if table_units:
            data_task = AnalysisTask(
                task_id=f"task_{task_counter:03d}",
                task_type=TaskType.DATA_EXTRACTION,
                agent_type="data_analyst",
                priority=2,
                input_pages=[unit.page_number for unit in table_units],
                input_content_units=[f"unit_{i}" for i in range(len(table_units))],
                expected_output_type="csv",
                processing_instructions="精确提取数据表格，转换为标准化的CSV或JSON格式"
            )
            tasks.append(data_task)
            task_counter += 1
        
        # 3. 创建地球化学分析任务
        geochem_units = [unit for unit in content_index.content_units 
                        if "geochemistry" in unit.keywords or 
                        any(keyword in unit.description.lower() for keyword in 
                            ['geochemical', 'chemical', 'composition', 'analysis'])]
        
        if geochem_units:
            geochem_task = AnalysisTask(
                task_id=f"task_{task_counter:03d}",
                task_type=TaskType.GEOCHEMICAL_ANALYSIS,
                agent_type="geochemist",
                priority=3,
                input_pages=[unit.page_number for unit in geochem_units],
                input_content_units=[f"unit_{i}" for i in range(len(geochem_units))],
                expected_output_type="structured_knowledge",
                processing_instructions="提炼地球化学分析结论，结合定量数据，形成结构化知识"
            )
            tasks.append(geochem_task)
            task_counter += 1
        
        # 4. 创建文本合成任务（处理剩余的重要文本内容）
        text_units = [unit for unit in content_index.content_units 
                     if unit.content_type == "text" and len(unit.keywords) > 0]
        
        if text_units:
            text_task = AnalysisTask(
                task_id=f"task_{task_counter:03d}",
                task_type=TaskType.TEXT_SYNTHESIS,
                agent_type="text_synthesizer",
                priority=4,
                input_pages=[unit.page_number for unit in text_units],
                input_content_units=[f"unit_{i}" for i in range(len(text_units))],
                expected_output_type="knowledge_graph",
                processing_instructions="提取和合成文本中的地质知识，构建知识图谱节点和关系"
            )
            tasks.append(text_task)
        
        logging.info(f"创建任务计划完成，共生成 {len(tasks)} 个分析任务")
        return tasks
