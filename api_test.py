#!/usr/bin/env python3
"""
简单API测试脚本
用于排查API密钥问题
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_api_step_by_step():
    """
    逐步测试API配置
    """
    print("🔍 逐步诊断API配置问题...")
    
    # 步骤1: 检查配置文件
    print("\n1️⃣ 检查配置文件...")
    try:
        from config import load_config
        config = load_config()
        api_key = config.get('google_api_key', '')
        print(f"✅ 配置文件加载成功")
        print(f"🔑 API密钥存在: {'是' if api_key else '否'}")
        print(f"🔑 密钥长度: {len(api_key)} 字符")
        print(f"🔑 密钥前缀: {api_key[:20]}...")
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return
    
    # 步骤2: 检查agent配置
    print("\n2️⃣ 检查Agent配置...")
    try:
        agent_config = config.get('agent_config', {})
        print(f"✅ Agent类型: {agent_config.get('agent_type', '未配置')}")
        print(f"✅ Agent名称: {agent_config.get('agent_name', '未配置')}")
    except Exception as e:
        print(f"❌ Agent配置检查失败: {e}")
        return
    
    # 步骤3: 尝试创建agent
    print("\n3️⃣ 尝试创建Agent...")
    try:
        from entity_extraction.llm_extractor import configure_agent
        agent = configure_agent(
            agent_config.get('agent_type', 'gemini'),
            agent_config.get('agent_name', 'gemini-1.5-flash'),
            api_key
        )
        print(f"✅ Agent创建成功: {type(agent)}")
    except Exception as e:
        print(f"❌ Agent创建失败: {e}")
        return
    
    # 步骤4: 检查agent内部结构
    print("\n4️⃣ 检查Agent内部结构...")
    try:
        print(f"Agent对象: {agent}")
        print(f"Agent类型: {type(agent.agent) if hasattr(agent, 'agent') else 'no agent attr'}")
        if hasattr(agent, 'agent') and hasattr(agent.agent, 'name'):
            print(f"Agent名称: {agent.agent.name}")
    except Exception as e:
        print(f"❌ Agent结构检查失败: {e}")
    
    # 步骤5: 尝试简单调用
    print("\n5️⃣ 尝试简单API调用...")
    try:
        response = agent.process("测试")
        print(f"✅ API调用成功!")
        print(f"📝 响应类型: {type(response)}")
        print(f"📝 响应内容: {str(response)[:100]}...")
        return True
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        print(f"🔍 错误类型: {type(e)}")
        
        # 检查是否是API密钥问题
        if "API_KEY_INVALID" in str(e) or "API key not valid" in str(e):
            print(f"🔑 确认是API密钥问题")
            print(f"💡 建议检查:")
            print(f"   - 密钥是否正确复制（没有多余空格）")
            print(f"   - 密钥是否启用了Generative AI API")
            print(f"   - 密钥是否有使用限制")
        
        return False

def test_with_direct_api():
    """
    使用直接HTTP请求测试API
    """
    print("\n🌐 尝试直接HTTP API调用...")
    
    import requests
    import json
    
    api_key = "AIzaSyDOxXa1YFX1_sPHHXv85iK_XDoa0VpfYEM"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": "请简单回答：你好"
            }]
        }]
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"📊 HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 直接API调用成功!")
            print(f"📝 响应: {result}")
            return True
        else:
            print(f"❌ HTTP请求失败")
            print(f"📝 错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 直接API调用失败: {e}")
        return False

if __name__ == "__main__":
    print("🔧 API问题诊断工具")
    print("="*50)
    
    # 逐步测试
    success = test_api_step_by_step()
    
    if not success:
        print("\n" + "="*50)
        # 如果逐步测试失败，尝试直接HTTP调用
        test_with_direct_api()
    
    print("\n🔧 诊断完成")
