import webbrowser
from pathlib import Path
import time

def verify_dashboard():
    """验证仪表板是否正确生成并打开"""
    
    dashboard_path = Path("data/processed/2008_MATABANE_FE3_dashboard.html")
    
    if not dashboard_path.exists():
        print("❌ Dashboard file not found!")
        return False
    
    print(f"✅ Dashboard file found: {dashboard_path}")
    print(f"📏 File size: {dashboard_path.stat().st_size} bytes")
    
    # Check if file contains data
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verify key data elements
    checks = [
        ('"total_entities": 14', "实体总数"),
        ('"total_relationships": 15', "关系总数"), 
        ('Geological Formations', "地质构造分类"),
        ('Sadiola goldfield', "地理位置数据"),
        ('Gold', "矿物数据"),
        ('ANALYSIS_DATA', "数据嵌入")
    ]
    
    print("\n🔍 Data verification:")
    all_passed = True
    
    for check_text, description in checks:
        if check_text in content:
            print(f"  ✅ {description}: 找到")
        else:
            print(f"  ❌ {description}: 未找到")
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有数据验证通过！")
        print(f"🌐 打开仪表板: file://{dashboard_path.absolute()}")
        webbrowser.open(f'file://{dashboard_path.absolute()}')
        return True
    else:
        print("\n⚠️ 数据验证失败，需要重新生成仪表板")
        return False

if __name__ == "__main__":
    verify_dashboard()
