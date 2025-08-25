"""
Map Analyst Agent - 地图分析专家
专门负责从地质图中提取空间数据，转换为GeoJSON格式
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from pydantic import BaseModel, Field

from .base import BaseAgent


class SpatialFeature(BaseModel):
    """空间要素"""
    feature_type: str  # 'point', 'line', 'polygon'
    geometry_type: str  # 'Point', 'LineString', 'Polygon'
    coordinates: List[Any]  # GeoJSON坐标格式
    properties: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = Field(ge=0.0, le=1.0)


class GeospatialData(BaseModel):
    """地理空间数据"""
    type: str = "FeatureCollection"
    features: List[SpatialFeature]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_info: Dict[str, Any] = Field(default_factory=dict)


class MapAnalystAgent(BaseAgent):
    """地图分析专家Agent"""
    
    def __init__(self, name: str = "MapAnalyst", **kwargs):
        super().__init__(name, **kwargs)
        self.agent_manager = kwargs.get('agent_manager')
        
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        分析地质图，提取空间数据
        
        Args:
            input_data: 包含地图相关内容的字典
            
        Returns:
            包含GeoJSON格式空间数据的字典
        """
        content_units = input_data.get('content_units', [])
        full_text = input_data.get('full_text', '')
        
        logging.info(f"Map Analyst Agent 开始分析 {len(content_units)} 个地图内容单元")
        
        try:
            # 1. 识别地图描述文本
            map_descriptions = self._extract_map_descriptions(content_units, full_text)
            
            # 2. 提取空间要素
            spatial_features = self._extract_spatial_features(map_descriptions)
            
            # 3. 构建GeoJSON
            geospatial_data = self._build_geojson(spatial_features)
            
            # 4. 验证和优化结果
            validated_data = self._validate_spatial_data(geospatial_data)
            
            return {
                'geospatial_data': validated_data,
                'feature_count': len(validated_data.features),
                'processing_status': 'success',
                'confidence_score': self._calculate_overall_confidence(validated_data)
            }
            
        except Exception as e:
            logging.error(f"Map Analyst Agent 处理失败: {e}")
            return {
                'geospatial_data': None,
                'feature_count': 0,
                'processing_status': 'failed',
                'error': str(e)
            }
    
    def _extract_map_descriptions(self, content_units: List[Any], full_text: str) -> List[str]:
        """提取地图相关的描述文本"""
        map_descriptions = []
        
        # 从内容单元中提取地图描述
        for unit in content_units:
            if hasattr(unit, 'content_type') and unit.content_type == 'figure':
                map_descriptions.append(unit.description)
                if hasattr(unit, 'content_preview'):
                    map_descriptions.append(unit.content_preview)
        
        # 从全文中搜索地图相关段落
        map_keywords = [
            'figure', 'fig', 'carte', 'map', 'geological', 'géologique',
            'location', 'coordinate', 'latitude', 'longitude', 'zone',
            'outcrop', 'deposit', 'mine', 'prospect', 'fault', 'formation'
        ]
        
        # 简单的段落分割和关键词匹配
        paragraphs = full_text.split('\n\n')
        for paragraph in paragraphs:
            if any(keyword.lower() in paragraph.lower() for keyword in map_keywords):
                if len(paragraph) > 50:  # 过滤太短的段落
                    map_descriptions.append(paragraph)
        
        logging.info(f"提取到 {len(map_descriptions)} 个地图描述段落")
        return map_descriptions
    
    def _extract_spatial_features(self, map_descriptions: List[str]) -> List[SpatialFeature]:
        """使用LLM从地图描述中提取空间要素"""
        spatial_features = []
        
        prompt = self._get_spatial_extraction_prompt()
        
        # 处理每个地图描述
        for description in map_descriptions:
            try:
                # 调用LLM提取空间信息
                result = self.agent_manager.generate_content(
                    prompt + f"\n\n地图描述文本:\n{description}"
                )
                
                # 解析LLM结果
                features = self._parse_spatial_features_result(result)
                spatial_features.extend(features)
                
            except Exception as e:
                logging.warning(f"处理地图描述失败: {e}")
                continue
        
        logging.info(f"提取到 {len(spatial_features)} 个空间要素")
        return spatial_features
    
    def _get_spatial_extraction_prompt(self) -> str:
        """获取空间要素提取的prompt"""
        return """
你是一位地理信息系统(GIS)专家。请从以下地质图描述文本中提取空间要素信息。

请识别以下类型的空间要素：
1. 点要素 (Points): 矿点、钻孔、采样点、城镇等
2. 线要素 (Lines): 断层、道路、河流、地质界线等  
3. 面要素 (Polygons): 岩性单元、矿区范围、行政边界等

请按以下JSON格式输出：
{
    "spatial_features": [
        {
            "feature_type": "point|line|polygon",
            "geometry_type": "Point|LineString|Polygon",
            "name": "要素名称",
            "description": "要素描述",
            "coordinates": "坐标信息(如果有)",
            "properties": {
                "feature_class": "要素类别",
                "geological_unit": "地质单元",
                "rock_type": "岩石类型",
                "mineral_type": "矿物类型",
                "other_attributes": "其他属性"
            },
            "confidence_score": 置信度(0.0-1.0)
        }
    ]
}

注意：
- 如果文本中没有明确的坐标信息，在coordinates字段中填入"unknown"
- 尽可能从文本中推断要素的地质属性
- 确保输出有效的JSON格式
"""
    
    def _parse_spatial_features_result(self, result: str) -> List[SpatialFeature]:
        """解析LLM空间要素提取结果"""
        try:
            parsed_result = json.loads(result)
            features = []
            
            for feature_data in parsed_result.get('spatial_features', []):
                # 处理坐标信息
                coordinates = self._process_coordinates(
                    feature_data.get('coordinates', 'unknown'),
                    feature_data.get('geometry_type', 'Point')
                )
                
                # 构建属性字典
                properties = feature_data.get('properties', {})
                properties['name'] = feature_data.get('name', 'Unknown')
                properties['description'] = feature_data.get('description', '')
                
                feature = SpatialFeature(
                    feature_type=feature_data.get('feature_type', 'point'),
                    geometry_type=feature_data.get('geometry_type', 'Point'),
                    coordinates=coordinates,
                    properties=properties,
                    confidence_score=feature_data.get('confidence_score', 0.5)
                )
                features.append(feature)
            
            return features
            
        except (json.JSONDecodeError, KeyError) as e:
            logging.warning(f"解析空间要素结果失败: {e}")
            return []
    
    def _process_coordinates(self, coord_text: str, geometry_type: str) -> List[Any]:
        """处理坐标信息"""
        if coord_text == 'unknown' or not coord_text:
            # 返回默认坐标 (示例坐标)
            if geometry_type == 'Point':
                return [0.0, 0.0]
            elif geometry_type == 'LineString':
                return [[0.0, 0.0], [1.0, 1.0]]
            elif geometry_type == 'Polygon':
                return [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]]
        
        # 尝试解析坐标文本
        try:
            # 简单的坐标解析 (可以扩展更复杂的解析逻辑)
            import re
            
            # 查找经纬度格式的坐标
            coord_pattern = r'(-?\d+\.?\d*)[°,\s]+(-?\d+\.?\d*)'
            matches = re.findall(coord_pattern, coord_text)
            
            if matches:
                if geometry_type == 'Point':
                    lon, lat = float(matches[0][0]), float(matches[0][1])
                    return [lon, lat]
                elif geometry_type == 'LineString':
                    coords = []
                    for match in matches[:2]:  # 最多取两个点
                        lon, lat = float(match[0]), float(match[1])
                        coords.append([lon, lat])
                    return coords if len(coords) >= 2 else [[0.0, 0.0], [1.0, 1.0]]
            
            return [0.0, 0.0]  # 默认返回
            
        except Exception:
            return [0.0, 0.0]
    
    def _build_geojson(self, spatial_features: List[SpatialFeature]) -> GeospatialData:
        """构建GeoJSON格式的地理空间数据"""
        geojson_features = []
        
        for feature in spatial_features:
            geojson_feature = {
                "type": "Feature",
                "geometry": {
                    "type": feature.geometry_type,
                    "coordinates": feature.coordinates
                },
                "properties": {
                    **feature.properties,
                    "confidence_score": feature.confidence_score,
                    "feature_type": feature.feature_type
                }
            }
            geojson_features.append(geojson_feature)
        
        geospatial_data = GeospatialData(
            features=geojson_features,
            metadata={
                "processing_agent": "MapAnalystAgent",
                "feature_count": len(geojson_features),
                "extraction_method": "llm_based"
            },
            processing_info={
                "total_features_extracted": len(spatial_features),
                "successful_features": len(geojson_features)
            }
        )
        
        return geospatial_data
    
    def _validate_spatial_data(self, geospatial_data: GeospatialData) -> GeospatialData:
        """验证和优化空间数据"""
        # 基本验证：检查坐标有效性
        valid_features = []
        
        for feature in geospatial_data.features:
            try:
                coords = feature.get('geometry', {}).get('coordinates', [])
                if self._validate_coordinates(coords):
                    valid_features.append(feature)
                else:
                    logging.warning(f"无效的坐标: {coords}")
            except Exception as e:
                logging.warning(f"验证要素失败: {e}")
                continue
        
        geospatial_data.features = valid_features
        geospatial_data.metadata['validated_features'] = len(valid_features)
        
        return geospatial_data
    
    def _validate_coordinates(self, coordinates: List[Any]) -> bool:
        """验证坐标的有效性"""
        try:
            if not coordinates:
                return False
            
            # 检查是否为有效的数值
            def is_valid_coord(coord):
                if isinstance(coord, (int, float)):
                    return -180 <= coord <= 180
                return False
            
            # 根据坐标结构进行验证
            if isinstance(coordinates[0], (int, float)):
                # Point coordinates
                return len(coordinates) >= 2 and all(is_valid_coord(c) for c in coordinates[:2])
            elif isinstance(coordinates[0], list):
                # LineString or Polygon coordinates
                return all(
                    len(coord) >= 2 and all(is_valid_coord(c) for c in coord[:2])
                    for coord in coordinates
                )
            
            return False
            
        except Exception:
            return False
    
    def _calculate_overall_confidence(self, geospatial_data: GeospatialData) -> float:
        """计算整体置信度"""
        if not geospatial_data.features:
            return 0.0
        
        total_confidence = 0.0
        valid_count = 0
        
        for feature in geospatial_data.features:
            confidence = feature.get('properties', {}).get('confidence_score', 0.0)
            if isinstance(confidence, (int, float)):
                total_confidence += confidence
                valid_count += 1
        
        return total_confidence / valid_count if valid_count > 0 else 0.0
