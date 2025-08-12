"""
Test LLM response to see actual decision output
测试LLM响应以查看实际决策输出
"""
import os
import json
from simulation.agent import create_agents
from simulation.environment import Environment

def test_single_agent_decision():
    """测试单个Agent的决策过程"""
    print("=== 测试LLM Agent决策过程 ===\n")
    
    # 加载配置
    with open('config/agents.json', 'r', encoding='utf-8') as f:
        agents_config = json.load(f)
    with open('config/environments.json', 'r', encoding='utf-8') as f:
        env_config = json.load(f)
    
    # 创建环境和Agent
    env = Environment(env_config['beijing'])
    agents = create_agents(agents_config, 'beijing')
    
    # 获取环境上下文
    env_context = env.get_context()
    
    print("1. 测试政府Agent决策:")
    gov_decision = agents['government'].decide(env_context)
    print(f"政府决策: {json.dumps(gov_decision, indent=2, ensure_ascii=False)}\n")
    
    print("2. 测试企业Agent决策:")
    ent_decision = agents['enterprises'][0].decide(env_context)
    print(f"企业决策: {json.dumps(ent_decision, indent=2, ensure_ascii=False)}\n")
    
    print("3. 测试居民Agent决策:")
    res_decision = agents['residents'][0].decide(env_context)
    print(f"居民决策: {json.dumps(res_decision, indent=2, ensure_ascii=False)}\n")
    
    print("✅ LLM决策测试完成！")

if __name__ == '__main__':
    test_single_agent_decision()