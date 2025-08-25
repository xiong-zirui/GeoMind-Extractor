"""
Geochemist Agent - 地球化学专家
专门负责提炼地球化学分析结论，结合定量数据形成结构化知识
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from pydantic import BaseModel, Field

from .base import BaseAgent


class GeochemicalEvidence(BaseModel):
    """地球化学证据"""
    element: str
    value: Union[float, str]
    unit: str
    measurement_method: Optional[str] = None
    sample_id: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=1.0)


class GeochemicalConclusion(BaseModel):
    """地球化学结论"""
    conclusion_id: str
    rock_type: str
    geochemical_affinity: str  # 如 "tholeiitic", "calc-alkaline"
    conclusion_text: str
    supporting_evidence: List[GeochemicalEvidence]
    confidence_score: float = Field(ge=0.0, le=1.0)
    source_location: Optional[str] = None


class GeochemicalKnowledge(BaseModel):
    """地球化学知识"""
    conclusions: List[GeochemicalConclusion]
    raw_data_tables: List[Dict[str, Any]] = Field(default_factory=list)
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)


class GeochemistAgent(BaseAgent):
    """地球化学专家Agent"""
    
    def __init__(self, name: str = "Geochemist", **kwargs):
        super().__init__(name, **kwargs)
        self.agent_manager = kwargs.get('agent_manager')
        
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        分析地球化学内容，提炼知识
        
        Args:
            input_data: 包含地球化学相关内容的字典
            
        Returns:
            包含结构化地球化学知识的字典
        """
        content_units = input_data.get('content_units', [])
        full_text = input_data.get('full_text', '')
        data_tables = input_data.get('data_tables', [])
        
        logging.info(f"Geochemist Agent 开始分析 {len(content_units)} 个地球化学内容单元")
        
        try:
            # 1. 识别地球化学分析文本
            geochem_texts = self._extract_geochemical_texts(content_units, full_text)
            
            # 2. 提取地球化学结论
            conclusions = self._extract_geochemical_conclusions(geochem_texts)
            
            # 3. 关联定量数据
            enriched_conclusions = self._enrich_with_quantitative_data(conclusions, data_tables)
            
            # 4. 构建知识结构
            geochem_knowledge = self._build_geochemical_knowledge(enriched_conclusions, data_tables)
            
            return {
                'geochemical_knowledge': geochem_knowledge,
                'conclusions_count': len(enriched_conclusions),
                'processing_status': 'success',
                'confidence_score': self._calculate_overall_confidence(geochem_knowledge)
            }
            
        except Exception as e:
            logging.error(f"Geochemist Agent 处理失败: {e}")
            return {
                'geochemical_knowledge': None,
                'conclusions_count': 0,
                'processing_status': 'failed',
                'error': str(e)
            }
    
    def _extract_geochemical_texts(self, content_units: List[Any], full_text: str) -> List[str]:
        """提取地球化学相关文本"""
        geochem_texts = []
        
        # 从内容单元中提取
        for unit in content_units:
            if hasattr(unit, 'keywords') and any('geochem' in kw.lower() for kw in unit.keywords):
                geochem_texts.append(unit.description)
                if hasattr(unit, 'content_preview'):
                    geochem_texts.append(unit.content_preview)
        
        # 从全文中搜索地球化学段落
        geochem_keywords = [
            'geochemical', 'géochimique', 'chemical composition', 'element',
            'oxide', 'trace element', 'major element', 'REE', 'rare earth',
            'tholeiitic', 'calc-alkaline', 'alkaline', 'basalt', 'granite',
            'SiO2', 'Al2O3', 'Fe2O3', 'MgO', 'CaO', 'Na2O', 'K2O',
            'Cr', 'Ni', 'V', 'Ti', 'Zr', 'Y', 'Nb', 'La', 'Ce', 'Nd'
        ]
        
        # 段落分割和关键词匹配
        paragraphs = full_text.split('\n\n')
        for paragraph in paragraphs:
            if any(keyword.lower() in paragraph.lower() for keyword in geochem_keywords):
                if len(paragraph) > 100:  # 过滤太短的段落
                    geochem_texts.append(paragraph)
        
        logging.info(f"提取到 {len(geochem_texts)} 个地球化学文本段落")
        return geochem_texts
    
    def _extract_geochemical_conclusions(self, geochem_texts: List[str]) -> List[GeochemicalConclusion]:
        """使用LLM提取地球化学结论"""
        conclusions = []
        
        prompt = self._get_geochemical_analysis_prompt()
        
        for i, text in enumerate(geochem_texts):
            try:
                # 调用LLM分析地球化学文本
                result = self.agent_manager.generate_content(
                    prompt + f"\n\n地球化学文本:\n{text}"
                )
                
                # 解析LLM结果
                text_conclusions = self._parse_geochemical_conclusions(result, f"text_{i}")
                conclusions.extend(text_conclusions)
                
            except Exception as e:
                logging.warning(f"处理地球化学文本失败: {e}")
                continue
        
        logging.info(f"提取到 {len(conclusions)} 个地球化学结论")
        return conclusions
    
    def _get_geochemical_analysis_prompt(self) -> str:
        """获取地球化学分析的prompt"""
        return """
你是一位地球化学专家。请分析以下地球化学文本，提取其中的科学结论和论据。

请识别以下信息：
1. 岩石类型和地球化学亲和性
2. 具体的地球化学结论
3. 支持这些结论的定量数据

请按以下JSON格式输出：
{
    "geochemical_conclusions": [
        {
            "rock_type": "岩石类型",
            "geochemical_affinity": "地球化学亲和性",
            "conclusion_text": "结论的完整描述",
            "supporting_evidence": [
                {
                    "element": "元素或氧化物名称",
                    "value": "数值或范围",
                    "unit": "单位",
                    "measurement_method": "测量方法(如果提及)",
                    "sample_id": "样品编号(如果有)",
                    "confidence_score": 置信度(0.0-1.0)
                }
            ],
            "confidence_score": 整体置信度(0.0-1.0)
        }
    ]
}

注意：
- 尽可能从文本中提取具体的数值数据作为证据
- 如果没有明确的数值，用"unknown"表示
- 确保结论和证据之间的逻辑关系清晰
- 输出有效的JSON格式
"""
    
    def _parse_geochemical_conclusions(self, result: str, source_id: str) -> List[GeochemicalConclusion]:
        """解析LLM地球化学结论提取结果"""
        try:
            parsed_result = json.loads(result)
            conclusions = []
            
            for i, conclusion_data in enumerate(parsed_result.get('geochemical_conclusions', [])):
                # 处理支持证据
                evidence_list = []
                for evidence_data in conclusion_data.get('supporting_evidence', []):
                    evidence = GeochemicalEvidence(
                        element=evidence_data.get('element', 'unknown'),
                        value=evidence_data.get('value', 'unknown'),
                        unit=evidence_data.get('unit', ''),
                        measurement_method=evidence_data.get('measurement_method'),
                        sample_id=evidence_data.get('sample_id'),
                        confidence_score=evidence_data.get('confidence_score', 0.5)
                    )
                    evidence_list.append(evidence)
                
                conclusion = GeochemicalConclusion(
                    conclusion_id=f"{source_id}_conclusion_{i+1}",
                    rock_type=conclusion_data.get('rock_type', 'unknown'),
                    geochemical_affinity=conclusion_data.get('geochemical_affinity', 'unknown'),
                    conclusion_text=conclusion_data.get('conclusion_text', ''),
                    supporting_evidence=evidence_list,
                    confidence_score=conclusion_data.get('confidence_score', 0.5),
                    source_location=source_id
                )
                conclusions.append(conclusion)
            
            return conclusions
            
        except (json.JSONDecodeError, KeyError) as e:
            logging.warning(f"解析地球化学结论失败: {e}")
            return []
    
    def _enrich_with_quantitative_data(self, conclusions: List[GeochemicalConclusion], 
                                     data_tables: List[Dict[str, Any]]) -> List[GeochemicalConclusion]:
        """用定量数据丰富地球化学结论"""
        if not data_tables:
            return conclusions
        
        enriched_conclusions = []
        
        for conclusion in conclusions:
            # 为每个结论寻找相关的定量数据
            additional_evidence = self._find_related_data(conclusion, data_tables)
            
            # 添加新发现的证据
            enriched_evidence = conclusion.supporting_evidence + additional_evidence
            
            # 创建丰富后的结论
            enriched_conclusion = GeochemicalConclusion(
                conclusion_id=conclusion.conclusion_id,
                rock_type=conclusion.rock_type,
                geochemical_affinity=conclusion.geochemical_affinity,
                conclusion_text=conclusion.conclusion_text,
                supporting_evidence=enriched_evidence,
                confidence_score=min(conclusion.confidence_score + 0.1, 1.0),  # 略微提高置信度
                source_location=conclusion.source_location
            )
            enriched_conclusions.append(enriched_conclusion)
        
        return enriched_conclusions
    
    def _find_related_data(self, conclusion: GeochemicalConclusion, 
                          data_tables: List[Dict[str, Any]]) -> List[GeochemicalEvidence]:
        """在数据表中寻找与结论相关的定量数据"""
        additional_evidence = []
        
        # 定义常见的地球化学元素和氧化物
        common_elements = [
            'SiO2', 'Al2O3', 'Fe2O3', 'FeO', 'MgO', 'CaO', 'Na2O', 'K2O', 'TiO2', 'P2O5',
            'Cr', 'Ni', 'V', 'Sc', 'Co', 'Cu', 'Zn', 'Ga', 'Rb', 'Sr', 'Y', 'Zr', 'Nb',
            'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu'
        ]
        
        for table in data_tables:
            if not isinstance(table, dict) or 'data' not in table:
                continue
            
            table_data = table.get('data', [])
            columns = table.get('columns', [])
            
            # 寻找包含地球化学数据的列
            geochem_columns = []
            for col in columns:
                if any(element.lower() in col.lower() for element in common_elements):
                    geochem_columns.append(col)
            
            # 从相关列中提取数据
            for col in geochem_columns:
                for row in table_data[:5]:  # 限制处理前5行
                    if isinstance(row, dict) and 'row_data' in row:
                        row_data = row['row_data']
                        if col in row_data:
                            value = row_data[col]
                            
                            # 尝试转换为数值
                            try:
                                if isinstance(value, str):
                                    # 清理数值字符串
                                    clean_value = value.replace(',', '').strip()
                                    if clean_value and clean_value != 'N/A':
                                        float_value = float(clean_value)
                                        
                                        evidence = GeochemicalEvidence(
                                            element=col,
                                            value=float_value,
                                            unit=self._infer_unit(col),
                                            measurement_method="table_data",
                                            sample_id=row_data.get('Sample', row_data.get('ID', 'unknown')),
                                            confidence_score=0.8
                                        )
                                        additional_evidence.append(evidence)
                                        
                            except (ValueError, TypeError):
                                # 如果不能转换为数值，仍然保存为字符串
                                if value and str(value).strip() and str(value).strip() != 'N/A':
                                    evidence = GeochemicalEvidence(
                                        element=col,
                                        value=str(value),
                                        unit=self._infer_unit(col),
                                        measurement_method="table_data",
                                        sample_id=row_data.get('Sample', row_data.get('ID', 'unknown')),
                                        confidence_score=0.6
                                    )
                                    additional_evidence.append(evidence)
        
        return additional_evidence[:10]  # 限制返回的证据数量
    
    def _infer_unit(self, element_name: str) -> str:
        """推断元素的单位"""
        element_lower = element_name.lower()
        
        # 主要氧化物通常用 wt% 表示
        major_oxides = ['sio2', 'al2o3', 'fe2o3', 'feo', 'mgo', 'cao', 'na2o', 'k2o', 'tio2', 'p2o5']
        if any(oxide in element_lower for oxide in major_oxides):
            return 'wt%'
        
        # 微量元素通常用 ppm 表示
        return 'ppm'
    
    def _build_geochemical_knowledge(self, conclusions: List[GeochemicalConclusion], 
                                   data_tables: List[Dict[str, Any]]) -> GeochemicalKnowledge:
        """构建地球化学知识结构"""
        return GeochemicalKnowledge(
            conclusions=conclusions,
            raw_data_tables=data_tables,
            processing_metadata={
                "processing_agent": "GeochemistAgent",
                "conclusions_count": len(conclusions),
                "total_evidence_count": sum(len(c.supporting_evidence) for c in conclusions),
                "data_tables_processed": len(data_tables)
            }
        )
    
    def _calculate_overall_confidence(self, geochem_knowledge: GeochemicalKnowledge) -> float:
        """计算整体置信度"""
        if not geochem_knowledge.conclusions:
            return 0.0
        
        total_confidence = sum(c.confidence_score for c in geochem_knowledge.conclusions)
        return total_confidence / len(geochem_knowledge.conclusions)
