"""
Data Analyst Agent - 数据分析专家
专门负责精确提取和清洗数据表格，转换为标准化格式
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from pydantic import BaseModel, Field

from .base import BaseAgent


class CleanedDataRow(BaseModel):
    """清洗后的数据行"""
    row_id: str
    data: Dict[str, Union[str, float, int]]
    data_quality_score: float = Field(ge=0.0, le=1.0)
    processing_notes: List[str] = Field(default_factory=list)


class StandardizedTable(BaseModel):
    """标准化表格"""
    table_id: str
    table_name: str
    original_source: str
    columns: List[str]
    column_types: Dict[str, str]  # 列名 -> 数据类型
    data_rows: List[CleanedDataRow]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    quality_metrics: Dict[str, float] = Field(default_factory=dict)


class DataExtractionReport(BaseModel):
    """数据提取报告"""
    standardized_tables: List[StandardizedTable]
    processing_summary: Dict[str, Any] = Field(default_factory=dict)
    quality_assessment: Dict[str, float] = Field(default_factory=dict)


class DataAnalystAgent(BaseAgent):
    """数据分析专家Agent"""
    
    def __init__(self, name: str = "DataAnalyst", **kwargs):
        super().__init__(name, **kwargs)
        self.agent_manager = kwargs.get('agent_manager')
        
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        分析和清洗数据表格
        
        Args:
            input_data: 包含表格数据的字典
            
        Returns:
            包含标准化表格的字典
        """
        raw_tables = input_data.get('raw_tables', [])
        content_units = input_data.get('content_units', [])
        full_text = input_data.get('full_text', '')
        
        logging.info(f"Data Analyst Agent 开始处理 {len(raw_tables)} 个原始表格")
        
        try:
            # 1. 增强表格提取（如果原始表格不足）
            if len(raw_tables) < 2:  # 如果表格数量较少，尝试增强提取
                enhanced_tables = self._enhanced_table_extraction(full_text)
                raw_tables.extend(enhanced_tables)
            
            # 2. 清洗和标准化每个表格
            standardized_tables = []
            for i, table in enumerate(raw_tables):
                try:
                    standardized_table = self._standardize_table(table, f"table_{i+1}")
                    if standardized_table:
                        standardized_tables.append(standardized_table)
                except Exception as e:
                    logging.warning(f"标准化表格 {i+1} 失败: {e}")
                    continue
            
            # 3. 质量评估
            quality_assessment = self._assess_data_quality(standardized_tables)
            
            # 4. 生成报告
            extraction_report = DataExtractionReport(
                standardized_tables=standardized_tables,
                processing_summary={
                    "original_tables_count": len(raw_tables),
                    "standardized_tables_count": len(standardized_tables),
                    "processing_agent": "DataAnalystAgent"
                },
                quality_assessment=quality_assessment
            )
            
            return {
                'extraction_report': extraction_report,
                'standardized_tables_count': len(standardized_tables),
                'processing_status': 'success',
                'overall_quality_score': quality_assessment.get('overall_score', 0.0)
            }
            
        except Exception as e:
            logging.error(f"Data Analyst Agent 处理失败: {e}")
            return {
                'extraction_report': None,
                'standardized_tables_count': 0,
                'processing_status': 'failed',
                'error': str(e)
            }
    
    def _enhanced_table_extraction(self, full_text: str) -> List[Dict[str, Any]]:
        """增强的表格提取"""
        enhanced_tables = []
        
        prompt = self._get_enhanced_table_extraction_prompt()
        
        # 将文本分成更小的片段进行处理
        text_chunks = self._split_text_for_table_extraction(full_text)
        
        for chunk in text_chunks:
            try:
                result = self.agent_manager.generate_content(
                    prompt + f"\n\n文档片段:\n{chunk}"
                )
                
                tables = self._parse_enhanced_table_result(result)
                enhanced_tables.extend(tables)
                
            except Exception as e:
                logging.warning(f"增强表格提取失败: {e}")
                continue
        
        logging.info(f"增强提取到 {len(enhanced_tables)} 个额外表格")
        return enhanced_tables
    
    def _get_enhanced_table_extraction_prompt(self) -> str:
        """获取增强表格提取的prompt"""
        return """
你是一位数据提取专家。请仔细分析以下文档片段，识别并提取其中的所有数据表格。

重点寻找以下类型的表格：
1. 钻孔数据表 (坐标、深度、岩性等)
2. 地球化学分析表 (元素含量、样品编号等)
3. 矿物成分表 (矿物类型、含量等)
4. 坐标定位表 (经纬度、UTM坐标等)

请按以下JSON格式输出所有找到的表格：
{
    "extracted_tables": [
        {
            "table_name": "表格名称或描述",
            "columns": ["列名1", "列名2", "列名3"],
            "data": [
                {
                    "row_data": {
                        "列名1": "值1",
                        "列名2": "值2",
                        "列名3": "值3"
                    }
                }
            ],
            "confidence_score": 置信度(0.0-1.0),
            "raw_text": "表格的原始文本"
        }
    ]
}

注意：
- 仔细识别列标题和行数据
- 保持数据的原始格式和精度
- 如果数据跨越多行，请正确合并
- 确保输出有效的JSON格式
"""
    
    def _split_text_for_table_extraction(self, full_text: str, chunk_size: int = 3000) -> List[str]:
        """将文本分割为适合表格提取的片段"""
        # 按段落分割
        paragraphs = full_text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # 如果当前段落包含表格关键词，优先处理
            if any(keyword in paragraph.lower() for keyword in 
                  ['table', 'tableau', 'data', 'sample', 'analysis', 'coordinate']):
                
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                
                # 表格段落可能比较长，单独处理
                if len(paragraph) > chunk_size:
                    # 进一步分割
                    lines = paragraph.split('\n')
                    temp_chunk = ""
                    for line in lines:
                        if len(temp_chunk + line) < chunk_size:
                            temp_chunk += line + '\n'
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk)
                            temp_chunk = line + '\n'
                    if temp_chunk:
                        chunks.append(temp_chunk)
                else:
                    chunks.append(paragraph)
            else:
                # 普通段落
                if len(current_chunk + paragraph) < chunk_size:
                    current_chunk += paragraph + '\n\n'
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = paragraph + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks[:10]  # 限制处理的片段数量
    
    def _parse_enhanced_table_result(self, result: str) -> List[Dict[str, Any]]:
        """解析增强表格提取结果"""
        try:
            parsed_result = json.loads(result)
            return parsed_result.get('extracted_tables', [])
        except (json.JSONDecodeError, KeyError) as e:
            logging.warning(f"解析增强表格结果失败: {e}")
            return []
    
    def _standardize_table(self, raw_table: Dict[str, Any], table_id: str) -> Optional[StandardizedTable]:
        """标准化单个表格"""
        try:
            # 提取基本信息
            table_name = raw_table.get('table_name', f'Table_{table_id}')
            columns = raw_table.get('columns', [])
            raw_data = raw_table.get('data', [])
            
            if not columns or not raw_data:
                logging.warning(f"表格 {table_id} 缺少列或数据")
                return None
            
            # 清洗列名
            cleaned_columns = self._clean_column_names(columns)
            
            # 推断列类型
            column_types = self._infer_column_types(raw_data, cleaned_columns)
            
            # 清洗数据行
            cleaned_rows = self._clean_data_rows(raw_data, cleaned_columns, column_types)
            
            # 计算质量指标
            quality_metrics = self._calculate_table_quality_metrics(cleaned_rows, cleaned_columns)
            
            # 创建标准化表格
            standardized_table = StandardizedTable(
                table_id=table_id,
                table_name=table_name,
                original_source=raw_table.get('raw_text', ''),
                columns=cleaned_columns,
                column_types=column_types,
                data_rows=cleaned_rows,
                metadata={
                    "original_columns": columns,
                    "original_row_count": len(raw_data),
                    "cleaning_applied": True
                },
                quality_metrics=quality_metrics
            )
            
            return standardized_table
            
        except Exception as e:
            logging.error(f"标准化表格 {table_id} 失败: {e}")
            return None
    
    def _clean_column_names(self, columns: List[str]) -> List[str]:
        """清洗列名"""
        cleaned_columns = []
        
        for col in columns:
            if not col or not isinstance(col, str):
                cleaned_columns.append(f"Column_{len(cleaned_columns)+1}")
                continue
            
            # 移除特殊字符，保留字母数字和下划线
            cleaned_col = re.sub(r'[^\w\s\-\.]', '', str(col))
            
            # 替换空格为下划线
            cleaned_col = re.sub(r'\s+', '_', cleaned_col.strip())
            
            # 确保不为空
            if not cleaned_col:
                cleaned_col = f"Column_{len(cleaned_columns)+1}"
            
            cleaned_columns.append(cleaned_col)
        
        return cleaned_columns
    
    def _infer_column_types(self, raw_data: List[Dict], columns: List[str]) -> Dict[str, str]:
        """推断列的数据类型"""
        column_types = {}
        
        for col in columns:
            # 收集该列的样本值
            sample_values = []
            for row in raw_data[:10]:  # 使用前10行进行类型推断
                if isinstance(row, dict) and 'row_data' in row:
                    row_data = row['row_data']
                    if col in row_data and row_data[col] is not None:
                        sample_values.append(str(row_data[col]).strip())
            
            # 推断类型
            if not sample_values:
                column_types[col] = 'string'
                continue
            
            # 检查是否为数值型
            numeric_count = 0
            for value in sample_values:
                if self._is_numeric(value):
                    numeric_count += 1
            
            if numeric_count / len(sample_values) > 0.7:  # 70%以上为数值
                # 检查是否为整数
                if all(self._is_integer(v) for v in sample_values if self._is_numeric(v)):
                    column_types[col] = 'integer'
                else:
                    column_types[col] = 'float'
            else:
                column_types[col] = 'string'
        
        return column_types
    
    def _is_numeric(self, value: str) -> bool:
        """检查字符串是否为数值"""
        if not value or value.lower() in ['n/a', 'na', 'null', '', '-']:
            return False
        
        try:
            # 移除逗号和空格
            clean_value = value.replace(',', '').replace(' ', '')
            float(clean_value)
            return True
        except ValueError:
            return False
    
    def _is_integer(self, value: str) -> bool:
        """检查数值是否为整数"""
        if not self._is_numeric(value):
            return False
        
        try:
            clean_value = value.replace(',', '').replace(' ', '')
            float_val = float(clean_value)
            return float_val.is_integer()
        except ValueError:
            return False
    
    def _clean_data_rows(self, raw_data: List[Dict], columns: List[str], 
                        column_types: Dict[str, str]) -> List[CleanedDataRow]:
        """清洗数据行"""
        cleaned_rows = []
        
        for i, raw_row in enumerate(raw_data):
            try:
                if not isinstance(raw_row, dict) or 'row_data' not in raw_row:
                    continue
                
                row_data = raw_row['row_data']
                cleaned_data = {}
                processing_notes = []
                data_quality_score = 1.0
                
                for col in columns:
                    original_value = row_data.get(col, '')
                    
                    # 清洗单个值
                    cleaned_value, quality_penalty, notes = self._clean_single_value(
                        original_value, column_types.get(col, 'string')
                    )
                    
                    cleaned_data[col] = cleaned_value
                    data_quality_score -= quality_penalty
                    processing_notes.extend(notes)
                
                # 确保质量分数在合理范围内
                data_quality_score = max(0.0, min(1.0, data_quality_score))
                
                cleaned_row = CleanedDataRow(
                    row_id=f"row_{i+1}",
                    data=cleaned_data,
                    data_quality_score=data_quality_score,
                    processing_notes=processing_notes
                )
                cleaned_rows.append(cleaned_row)
                
            except Exception as e:
                logging.warning(f"清洗行 {i+1} 失败: {e}")
                continue
        
        return cleaned_rows
    
    def _clean_single_value(self, value: Any, expected_type: str) -> tuple:
        """清洗单个值"""
        if value is None:
            return None, 0.1, []
        
        str_value = str(value).strip()
        notes = []
        quality_penalty = 0.0
        
        # 处理空值
        if not str_value or str_value.lower() in ['n/a', 'na', 'null', '-', '']:
            return None, 0.1, ['empty_value']
        
        # 根据期望类型进行清洗
        if expected_type == 'float':
            try:
                # 移除逗号、空格等
                clean_str = str_value.replace(',', '').replace(' ', '')
                cleaned_value = float(clean_str)
                return cleaned_value, 0.0, []
            except ValueError:
                notes.append('numeric_conversion_failed')
                quality_penalty = 0.3
                return str_value, quality_penalty, notes
        
        elif expected_type == 'integer':
            try:
                clean_str = str_value.replace(',', '').replace(' ', '')
                cleaned_value = int(float(clean_str))  # 先转float再转int，处理"3.0"这种情况
                return cleaned_value, 0.0, []
            except ValueError:
                notes.append('integer_conversion_failed')
                quality_penalty = 0.3
                return str_value, quality_penalty, notes
        
        else:  # string type
            # 基本的字符串清理
            cleaned_value = str_value.strip()
            if len(cleaned_value) != len(str_value):
                notes.append('whitespace_trimmed')
                quality_penalty = 0.05
            
            return cleaned_value, quality_penalty, notes
    
    def _calculate_table_quality_metrics(self, cleaned_rows: List[CleanedDataRow], 
                                       columns: List[str]) -> Dict[str, float]:
        """计算表格质量指标"""
        if not cleaned_rows:
            return {'overall_quality': 0.0, 'completeness': 0.0, 'consistency': 0.0}
        
        total_cells = len(cleaned_rows) * len(columns)
        non_null_cells = 0
        total_quality_score = 0.0
        
        for row in cleaned_rows:
            total_quality_score += row.data_quality_score
            for col in columns:
                if row.data.get(col) is not None:
                    non_null_cells += 1
        
        completeness = non_null_cells / total_cells if total_cells > 0 else 0.0
        avg_quality = total_quality_score / len(cleaned_rows) if cleaned_rows else 0.0
        
        # 一致性检查（简化版）
        consistency = min(1.0, avg_quality + 0.1)
        
        overall_quality = (completeness + avg_quality + consistency) / 3
        
        return {
            'overall_quality': overall_quality,
            'completeness': completeness,
            'average_row_quality': avg_quality,
            'consistency': consistency,
            'total_rows': len(cleaned_rows),
            'total_columns': len(columns)
        }
    
    def _assess_data_quality(self, standardized_tables: List[StandardizedTable]) -> Dict[str, float]:
        """评估整体数据质量"""
        if not standardized_tables:
            return {'overall_score': 0.0}
        
        total_quality = 0.0
        total_tables = len(standardized_tables)
        
        for table in standardized_tables:
            table_quality = table.quality_metrics.get('overall_quality', 0.0)
            total_quality += table_quality
        
        overall_score = total_quality / total_tables
        
        return {
            'overall_score': overall_score,
            'tables_processed': total_tables,
            'high_quality_tables': sum(1 for t in standardized_tables 
                                     if t.quality_metrics.get('overall_quality', 0) > 0.8),
            'average_completeness': sum(t.quality_metrics.get('completeness', 0) 
                                      for t in standardized_tables) / total_tables
        }
