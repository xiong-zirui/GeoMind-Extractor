"""
Synthesizer Agent - 知识合成专家
负责融合所有专家Agent的产出，构建统一的知识图谱，并映射到地理数据库
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

from .base import BaseAgent


class ValidationResult(BaseModel):
    """验证结果"""
    is_valid: bool
    confidence_score: float = Field(ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class DatabaseRecord(BaseModel):
    """数据库记录"""
    table_name: str
    record_id: str
    data: Dict[str, Any]
    relationships: List[Dict[str, str]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SynthesizedKnowledge(BaseModel):
    """合成知识"""
    knowledge_id: str
    document_source: str
    spatial_features: Dict[str, Any] = Field(default_factory=dict)
    geochemical_knowledge: Dict[str, Any] = Field(default_factory=dict)
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    knowledge_graph: Dict[str, Any] = Field(default_factory=dict)
    database_records: List[DatabaseRecord] = Field(default_factory=list)
    validation_results: Dict[str, ValidationResult] = Field(default_factory=dict)
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)


class SynthesizerAgent(BaseAgent):
    """知识合成专家Agent"""
    
    def __init__(self, name: str = "Synthesizer", **kwargs):
        super().__init__(name, **kwargs)
        self.agent_manager = kwargs.get('agent_manager')
        self.database_schema = self._load_database_schema()
        
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        融合所有专家Agent的产出，生成统一知识资产
        
        Args:
            input_data: 包含所有专家Agent结果的字典
            
        Returns:
            包含合成知识和数据库记录的字典
        """
        document_source = input_data.get('document_source', 'unknown')
        map_analyst_result = input_data.get('map_analyst_result', {})
        geochemist_result = input_data.get('geochemist_result', {})
        data_analyst_result = input_data.get('data_analyst_result', {})
        original_knowledge_graph = input_data.get('original_knowledge_graph', {})
        
        logging.info(f"Synthesizer Agent 开始融合知识，文档来源: {document_source}")
        
        try:
            # 1. 构建中间知识图谱
            intermediate_kg = self._build_intermediate_knowledge_graph(
                map_analyst_result, geochemist_result, data_analyst_result, original_knowledge_graph
            )
            
            # 2. 交叉验证与一致性检查
            validation_results = self._cross_validate_knowledge(
                map_analyst_result, geochemist_result, data_analyst_result, intermediate_kg
            )
            
            # 3. 知识融合
            synthesized_knowledge = self._synthesize_knowledge(
                document_source, map_analyst_result, geochemist_result, 
                data_analyst_result, intermediate_kg, validation_results
            )
            
            # 4. 映射到地理数据库
            database_records = self._map_to_database_schema(synthesized_knowledge)
            
            # 5. 更新合成知识
            synthesized_knowledge.database_records = database_records
            synthesized_knowledge.validation_results = validation_results
            
            return {
                'synthesized_knowledge': synthesized_knowledge,
                'database_records_count': len(database_records),
                'processing_status': 'success',
                'overall_confidence': self._calculate_overall_confidence(synthesized_knowledge)
            }
            
        except Exception as e:
            logging.error(f"Synthesizer Agent 处理失败: {e}")
            return {
                'synthesized_knowledge': None,
                'database_records_count': 0,
                'processing_status': 'failed',
                'error': str(e)
            }
    
    def _load_database_schema(self) -> Dict[str, Any]:
        """加载地理数据库模式"""
        # 定义目标地理数据库的表结构
        return {
            'locations': {
                'primary_key': 'location_id',
                'columns': {
                    'location_id': 'UUID',
                    'name': 'VARCHAR(255)',
                    'location_type': 'VARCHAR(100)',  # 'mine', 'prospect', 'outcrop', 'region'
                    'geometry': 'GEOMETRY',  # PostGIS几何类型
                    'coordinate_system': 'VARCHAR(50)',
                    'description': 'TEXT',
                    'confidence_score': 'FLOAT',
                    'created_at': 'TIMESTAMP',
                    'source_document': 'VARCHAR(255)'
                },
                'relationships': ['geochemistry', 'geology', 'drilling_data']
            },
            'geochemistry': {
                'primary_key': 'geochemistry_id',
                'columns': {
                    'geochemistry_id': 'UUID',
                    'location_id': 'UUID',  # 外键
                    'sample_id': 'VARCHAR(100)',
                    'rock_type': 'VARCHAR(100)',
                    'geochemical_affinity': 'VARCHAR(100)',
                    'analysis_method': 'VARCHAR(100)',
                    'confidence_score': 'FLOAT',
                    'created_at': 'TIMESTAMP',
                    'source_document': 'VARCHAR(255)'
                },
                'relationships': ['locations', 'geochemical_elements']
            },
            'geochemical_elements': {
                'primary_key': 'element_id',
                'columns': {
                    'element_id': 'UUID',
                    'geochemistry_id': 'UUID',  # 外键
                    'element_name': 'VARCHAR(50)',
                    'value': 'FLOAT',
                    'unit': 'VARCHAR(20)',
                    'detection_limit': 'FLOAT',
                    'measurement_method': 'VARCHAR(100)',
                    'confidence_score': 'FLOAT'
                },
                'relationships': ['geochemistry']
            },
            'geology': {
                'primary_key': 'geology_id',
                'columns': {
                    'geology_id': 'UUID',
                    'location_id': 'UUID',  # 外键
                    'geological_unit': 'VARCHAR(100)',
                    'rock_type': 'VARCHAR(100)',
                    'age': 'VARCHAR(100)',
                    'formation': 'VARCHAR(100)',
                    'structural_features': 'TEXT',
                    'mineral_assemblage': 'TEXT',
                    'confidence_score': 'FLOAT',
                    'created_at': 'TIMESTAMP',
                    'source_document': 'VARCHAR(255)'
                },
                'relationships': ['locations']
            },
            'drilling_data': {
                'primary_key': 'drill_hole_id',
                'columns': {
                    'drill_hole_id': 'UUID',
                    'location_id': 'UUID',  # 外键
                    'hole_name': 'VARCHAR(100)',
                    'depth_from': 'FLOAT',
                    'depth_to': 'FLOAT',
                    'lithology': 'VARCHAR(200)',
                    'alteration': 'VARCHAR(200)',
                    'mineralization': 'VARCHAR(200)',
                    'confidence_score': 'FLOAT',
                    'created_at': 'TIMESTAMP',
                    'source_document': 'VARCHAR(255)'
                },
                'relationships': ['locations']
            }
        }
    
    def _build_intermediate_knowledge_graph(self, map_result: Dict, geochem_result: Dict, 
                                          data_result: Dict, original_kg: Dict) -> Dict[str, Any]:
        """构建中间知识图谱"""
        intermediate_kg = {
            'nodes': [],
            'relationships': [],
            'metadata': {
                'creation_timestamp': datetime.now().isoformat(),
                'source_agents': ['map_analyst', 'geochemist', 'data_analyst'],
                'integration_method': 'synthesizer_agent'
            }
        }
        
        # 1. 从地图分析结果添加空间节点
        if map_result.get('geospatial_data'):
            spatial_nodes = self._extract_spatial_nodes(map_result['geospatial_data'])
            intermediate_kg['nodes'].extend(spatial_nodes)
        
        # 2. 从地球化学分析结果添加地球化学节点
        if geochem_result.get('geochemical_knowledge'):
            geochem_nodes = self._extract_geochemical_nodes(geochem_result['geochemical_knowledge'])
            intermediate_kg['nodes'].extend(geochem_nodes)
        
        # 3. 从数据分析结果添加数据节点
        if data_result.get('extraction_report'):
            data_nodes = self._extract_data_nodes(data_result['extraction_report'])
            intermediate_kg['nodes'].extend(data_nodes)
        
        # 4. 从原始知识图谱添加文本节点
        if original_kg:
            text_nodes = self._extract_text_nodes(original_kg)
            intermediate_kg['nodes'].extend(text_nodes)
        
        # 5. 建立节点之间的关系
        relationships = self._establish_node_relationships(intermediate_kg['nodes'])
        intermediate_kg['relationships'] = relationships
        
        logging.info(f"构建中间知识图谱完成: {len(intermediate_kg['nodes'])} 个节点, {len(relationships)} 个关系")
        return intermediate_kg
    
    def _extract_spatial_nodes(self, geospatial_data: Any) -> List[Dict[str, Any]]:
        """从空间数据提取节点"""
        nodes = []
        
        if hasattr(geospatial_data, 'features'):
            features = geospatial_data.features
        elif isinstance(geospatial_data, dict):
            features = geospatial_data.get('features', [])
        else:
            return nodes
        
        for feature in features:
            if isinstance(feature, dict):
                properties = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                
                node = {
                    'id': str(uuid.uuid4()),
                    'type': 'spatial_feature',
                    'subtype': properties.get('feature_type', 'unknown'),
                    'name': properties.get('name', 'Unnamed Location'),
                    'geometry': geometry,
                    'properties': properties,
                    'source_agent': 'map_analyst',
                    'confidence': properties.get('confidence_score', 0.5)
                }
                nodes.append(node)
        
        return nodes
    
    def _extract_geochemical_nodes(self, geochem_knowledge: Any) -> List[Dict[str, Any]]:
        """从地球化学知识提取节点"""
        nodes = []
        
        if hasattr(geochem_knowledge, 'conclusions'):
            conclusions = geochem_knowledge.conclusions
        elif isinstance(geochem_knowledge, dict):
            conclusions = geochem_knowledge.get('conclusions', [])
        else:
            return nodes
        
        for conclusion in conclusions:
            if hasattr(conclusion, 'conclusion_id'):
                node = {
                    'id': conclusion.conclusion_id,
                    'type': 'geochemical_conclusion',
                    'subtype': conclusion.rock_type,
                    'name': f"{conclusion.rock_type} - {conclusion.geochemical_affinity}",
                    'conclusion_text': conclusion.conclusion_text,
                    'evidence': [
                        {
                            'element': ev.element,
                            'value': ev.value,
                            'unit': ev.unit,
                            'confidence': ev.confidence_score
                        }
                        for ev in conclusion.supporting_evidence
                    ],
                    'source_agent': 'geochemist',
                    'confidence': conclusion.confidence_score
                }
                nodes.append(node)
        
        return nodes
    
    def _extract_data_nodes(self, extraction_report: Any) -> List[Dict[str, Any]]:
        """从数据报告提取节点"""
        nodes = []
        
        if hasattr(extraction_report, 'standardized_tables'):
            tables = extraction_report.standardized_tables
        elif isinstance(extraction_report, dict):
            tables = extraction_report.get('standardized_tables', [])
        else:
            return nodes
        
        for table in tables:
            if hasattr(table, 'table_id'):
                node = {
                    'id': table.table_id,
                    'type': 'data_table',
                    'subtype': 'structured_data',
                    'name': table.table_name,
                    'columns': table.columns,
                    'column_types': table.column_types,
                    'row_count': len(table.data_rows),
                    'quality_metrics': table.quality_metrics,
                    'source_agent': 'data_analyst',
                    'confidence': table.quality_metrics.get('overall_quality', 0.5)
                }
                nodes.append(node)
        
        return nodes
    
    def _extract_text_nodes(self, original_kg: Dict) -> List[Dict[str, Any]]:
        """从原始知识图谱提取文本节点"""
        nodes = []
        
        # 处理实体
        entities = original_kg.get('entities', [])
        for entity in entities:
            node = {
                'id': str(uuid.uuid4()),
                'type': 'text_entity',
                'subtype': entity.get('type', 'unknown'),
                'name': entity.get('name', 'Unknown Entity'),
                'description': entity.get('description', ''),
                'properties': entity.get('properties', {}),
                'source_agent': 'text_extraction',
                'confidence': entity.get('confidence_score', 0.5)
            }
            nodes.append(node)
        
        return nodes
    
    def _establish_node_relationships(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """建立节点之间的关系"""
        relationships = []
        
        # 基于地理位置建立关系
        spatial_nodes = [n for n in nodes if n['type'] == 'spatial_feature']
        geochem_nodes = [n for n in nodes if n['type'] == 'geochemical_conclusion']
        
        for spatial_node in spatial_nodes:
            for geochem_node in geochem_nodes:
                # 简化的关系建立逻辑：基于名称匹配
                if self._nodes_are_related(spatial_node, geochem_node):
                    relationship = {
                        'id': str(uuid.uuid4()),
                        'source_node': spatial_node['id'],
                        'target_node': geochem_node['id'],
                        'relationship_type': 'spatial_geochemical_association',
                        'confidence': min(spatial_node['confidence'], geochem_node['confidence']),
                        'properties': {
                            'association_basis': 'location_name_match',
                            'strength': 'moderate'
                        }
                    }
                    relationships.append(relationship)
        
        return relationships
    
    def _nodes_are_related(self, node1: Dict, node2: Dict) -> bool:
        """判断两个节点是否相关"""
        # 简化的关系判断逻辑
        name1 = node1.get('name', '').lower()
        name2 = node2.get('name', '').lower()
        
        # 检查名称是否有共同词汇
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        return len(words1.intersection(words2)) > 0
    
    def _cross_validate_knowledge(self, map_result: Dict, geochem_result: Dict, 
                                data_result: Dict, intermediate_kg: Dict) -> Dict[str, ValidationResult]:
        """交叉验证与一致性检查"""
        validation_results = {}
        
        # 1. 空间数据一致性验证
        spatial_validation = self._validate_spatial_consistency(map_result, intermediate_kg)
        validation_results['spatial_consistency'] = spatial_validation
        
        # 2. 地球化学数据一致性验证
        geochem_validation = self._validate_geochemical_consistency(geochem_result, data_result)
        validation_results['geochemical_consistency'] = geochem_validation
        
        # 3. 数据完整性验证
        completeness_validation = self._validate_data_completeness(
            map_result, geochem_result, data_result
        )
        validation_results['data_completeness'] = completeness_validation
        
        return validation_results
    
    def _validate_spatial_consistency(self, map_result: Dict, intermediate_kg: Dict) -> ValidationResult:
        """验证空间数据一致性"""
        issues = []
        suggestions = []
        confidence = 1.0
        
        # 检查空间要素数量
        if map_result.get('feature_count', 0) < 1:
            issues.append("No spatial features extracted")
            confidence -= 0.3
            suggestions.append("Consider improving map analysis or using alternative extraction methods")
        
        # 检查坐标有效性
        geospatial_data = map_result.get('geospatial_data')
        if geospatial_data:
            invalid_coords = 0
            total_features = 0
            
            features = geospatial_data.get('features', [])
            for feature in features:
                total_features += 1
                geometry = feature.get('geometry', {})
                coords = geometry.get('coordinates', [])
                
                if not coords or coords == [0.0, 0.0]:
                    invalid_coords += 1
            
            if invalid_coords > 0:
                issues.append(f"{invalid_coords}/{total_features} features have invalid coordinates")
                confidence -= (invalid_coords / total_features) * 0.4
                suggestions.append("Review coordinate extraction logic and source data quality")
        
        confidence = max(0.0, confidence)
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence_score=confidence,
            issues=issues,
            suggestions=suggestions
        )
    
    def _validate_geochemical_consistency(self, geochem_result: Dict, data_result: Dict) -> ValidationResult:
        """验证地球化学数据一致性"""
        issues = []
        suggestions = []
        confidence = 1.0
        
        # 检查地球化学结论数量
        conclusions_count = geochem_result.get('conclusions_count', 0)
        if conclusions_count < 1:
            issues.append("No geochemical conclusions extracted")
            confidence -= 0.4
            suggestions.append("Ensure geochemical analysis texts are properly identified")
        
        # 检查数据表格与地球化学结论的一致性
        tables_count = data_result.get('standardized_tables_count', 0)
        if conclusions_count > 0 and tables_count == 0:
            issues.append("Geochemical conclusions found but no supporting data tables")
            confidence -= 0.3
            suggestions.append("Improve table extraction to support geochemical conclusions")
        
        confidence = max(0.0, confidence)
        
        return ValidationResult(
            is_valid=len(issues) < 2,
            confidence_score=confidence,
            issues=issues,
            suggestions=suggestions
        )
    
    def _validate_data_completeness(self, map_result: Dict, geochem_result: Dict, 
                                  data_result: Dict) -> ValidationResult:
        """验证数据完整性"""
        issues = []
        suggestions = []
        confidence = 1.0
        
        # 检查各类数据的存在性
        has_spatial = map_result.get('feature_count', 0) > 0
        has_geochem = geochem_result.get('conclusions_count', 0) > 0
        has_tables = data_result.get('standardized_tables_count', 0) > 0
        
        data_completeness = sum([has_spatial, has_geochem, has_tables]) / 3
        
        if data_completeness < 0.67:
            issues.append(f"Low data completeness: {data_completeness:.1%}")
            confidence = data_completeness
            suggestions.append("Ensure all types of geological data are properly extracted")
        
        return ValidationResult(
            is_valid=data_completeness >= 0.67,
            confidence_score=confidence,
            issues=issues,
            suggestions=suggestions
        )
    
    def _synthesize_knowledge(self, document_source: str, map_result: Dict, 
                            geochem_result: Dict, data_result: Dict, 
                            intermediate_kg: Dict, validation_results: Dict) -> SynthesizedKnowledge:
        """合成所有知识"""
        knowledge_id = str(uuid.uuid4())
        
        return SynthesizedKnowledge(
            knowledge_id=knowledge_id,
            document_source=document_source,
            spatial_features=map_result,
            geochemical_knowledge=geochem_result,
            structured_data=data_result,
            knowledge_graph=intermediate_kg,
            processing_metadata={
                'synthesis_timestamp': datetime.now().isoformat(),
                'validation_passed': all(vr.is_valid for vr in validation_results.values()),
                'overall_confidence': sum(vr.confidence_score for vr in validation_results.values()) / len(validation_results) if validation_results else 0.0
            }
        )
    
    def _map_to_database_schema(self, synthesized_knowledge: SynthesizedKnowledge) -> List[DatabaseRecord]:
        """映射到地理数据库模式"""
        database_records = []
        
        # 1. 处理空间要素 -> locations表
        spatial_records = self._create_location_records(synthesized_knowledge)
        database_records.extend(spatial_records)
        
        # 2. 处理地球化学数据 -> geochemistry表
        geochem_records = self._create_geochemistry_records(synthesized_knowledge, spatial_records)
        database_records.extend(geochem_records)
        
        # 3. 处理结构化数据 -> drilling_data表
        drilling_records = self._create_drilling_records(synthesized_knowledge, spatial_records)
        database_records.extend(drilling_records)
        
        return database_records
    
    def _create_location_records(self, synthesized_knowledge: SynthesizedKnowledge) -> List[DatabaseRecord]:
        """创建位置记录"""
        records = []
        
        geospatial_data = synthesized_knowledge.spatial_features.get('geospatial_data')
        if not geospatial_data:
            return records
        
        features = geospatial_data.get('features', [])
        for feature in features:
            if isinstance(feature, dict):
                properties = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                
                location_id = str(uuid.uuid4())
                record_data = {
                    'location_id': location_id,
                    'name': properties.get('name', 'Unnamed Location'),
                    'location_type': properties.get('feature_class', 'unknown'),
                    'geometry': json.dumps(geometry),  # 存储为JSON字符串
                    'coordinate_system': 'WGS84',  # 默认坐标系
                    'description': properties.get('description', ''),
                    'confidence_score': properties.get('confidence_score', 0.5),
                    'created_at': datetime.now().isoformat(),
                    'source_document': synthesized_knowledge.document_source
                }
                
                record = DatabaseRecord(
                    table_name='locations',
                    record_id=location_id,
                    data=record_data,
                    metadata={'source_agent': 'map_analyst', 'feature_type': properties.get('feature_type')}
                )
                records.append(record)
        
        return records
    
    def _create_geochemistry_records(self, synthesized_knowledge: SynthesizedKnowledge, 
                                   location_records: List[DatabaseRecord]) -> List[DatabaseRecord]:
        """创建地球化学记录"""
        records = []
        
        geochem_knowledge = synthesized_knowledge.geochemical_knowledge.get('geochemical_knowledge')
        if not geochem_knowledge:
            return records
        
        conclusions = geochem_knowledge.get('conclusions', [])
        
        for conclusion in conclusions:
            if hasattr(conclusion, 'conclusion_id'):
                # 尝试关联到位置记录（简化逻辑）
                associated_location_id = None
                if location_records:
                    associated_location_id = location_records[0].record_id  # 简化：关联到第一个位置
                
                geochemistry_id = str(uuid.uuid4())
                record_data = {
                    'geochemistry_id': geochemistry_id,
                    'location_id': associated_location_id,
                    'sample_id': f"sample_{conclusion.conclusion_id}",
                    'rock_type': conclusion.rock_type,
                    'geochemical_affinity': conclusion.geochemical_affinity,
                    'analysis_method': 'literature_extraction',
                    'confidence_score': conclusion.confidence_score,
                    'created_at': datetime.now().isoformat(),
                    'source_document': synthesized_knowledge.document_source
                }
                
                record = DatabaseRecord(
                    table_name='geochemistry',
                    record_id=geochemistry_id,
                    data=record_data,
                    relationships=[{
                        'table': 'locations',
                        'foreign_key': 'location_id',
                        'referenced_id': associated_location_id
                    }] if associated_location_id else [],
                    metadata={'source_agent': 'geochemist', 'conclusion_id': conclusion.conclusion_id}
                )
                records.append(record)
                
                # 创建相关的元素记录
                element_records = self._create_element_records(conclusion, geochemistry_id)
                records.extend(element_records)
        
        return records
    
    def _create_element_records(self, conclusion: Any, geochemistry_id: str) -> List[DatabaseRecord]:
        """创建元素记录"""
        records = []
        
        if hasattr(conclusion, 'supporting_evidence'):
            for evidence in conclusion.supporting_evidence:
                element_id = str(uuid.uuid4())
                record_data = {
                    'element_id': element_id,
                    'geochemistry_id': geochemistry_id,
                    'element_name': evidence.element,
                    'value': evidence.value if isinstance(evidence.value, (int, float)) else None,
                    'unit': evidence.unit,
                    'detection_limit': None,
                    'measurement_method': evidence.measurement_method,
                    'confidence_score': evidence.confidence_score
                }
                
                record = DatabaseRecord(
                    table_name='geochemical_elements',
                    record_id=element_id,
                    data=record_data,
                    relationships=[{
                        'table': 'geochemistry',
                        'foreign_key': 'geochemistry_id',
                        'referenced_id': geochemistry_id
                    }],
                    metadata={'source_agent': 'geochemist'}
                )
                records.append(record)
        
        return records
    
    def _create_drilling_records(self, synthesized_knowledge: SynthesizedKnowledge, 
                               location_records: List[DatabaseRecord]) -> List[DatabaseRecord]:
        """创建钻孔记录"""
        records = []
        
        extraction_report = synthesized_knowledge.structured_data.get('extraction_report')
        if not extraction_report:
            return records
        
        tables = extraction_report.get('standardized_tables', [])
        
        for table in tables:
            if hasattr(table, 'data_rows'):
                # 检查是否为钻孔数据表
                columns = table.columns if hasattr(table, 'columns') else []
                is_drilling_table = any(col.lower() in ['depth', 'hole', 'drill', 'lithology'] 
                                      for col in columns)
                
                if is_drilling_table and location_records:
                    associated_location_id = location_records[0].record_id  # 简化关联
                    
                    for row in table.data_rows:
                        drill_hole_id = str(uuid.uuid4())
                        row_data = row.data if hasattr(row, 'data') else {}
                        
                        record_data = {
                            'drill_hole_id': drill_hole_id,
                            'location_id': associated_location_id,
                            'hole_name': row_data.get('Hole', row_data.get('ID', f"hole_{drill_hole_id[:8]}")),
                            'depth_from': row_data.get('Depth_From', 0.0),
                            'depth_to': row_data.get('Depth_To', 0.0),
                            'lithology': row_data.get('Lithology', ''),
                            'alteration': row_data.get('Alteration', ''),
                            'mineralization': row_data.get('Mineralization', ''),
                            'confidence_score': row.data_quality_score if hasattr(row, 'data_quality_score') else 0.5,
                            'created_at': datetime.now().isoformat(),
                            'source_document': synthesized_knowledge.document_source
                        }
                        
                        record = DatabaseRecord(
                            table_name='drilling_data',
                            record_id=drill_hole_id,
                            data=record_data,
                            relationships=[{
                                'table': 'locations',
                                'foreign_key': 'location_id',
                                'referenced_id': associated_location_id
                            }],
                            metadata={'source_agent': 'data_analyst', 'source_table': table.table_id if hasattr(table, 'table_id') else 'unknown'}
                        )
                        records.append(record)
        
        return records
    
    def _calculate_overall_confidence(self, synthesized_knowledge: SynthesizedKnowledge) -> float:
        """计算整体置信度"""
        validation_results = synthesized_knowledge.validation_results
        if not validation_results:
            return 0.5
        
        total_confidence = sum(vr.confidence_score for vr in validation_results.values())
        return total_confidence / len(validation_results)
