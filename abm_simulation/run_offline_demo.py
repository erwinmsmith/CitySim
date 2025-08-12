"""
Offline demo script for ABM digital governance simulation
离线演示脚本 - 不需要API密钥
"""
import os
import sys
import json
from main import run_simulation, save_results


def mock_llm_response():
    """Mock LLM to avoid API calls"""
    from simulation.agent import Agent
    
    # Override the decide method to return default decisions
    original_decide = Agent.decide
    
    def mock_decide(self, context):
        """Mock decision without LLM call"""
        decision = self._get_default_decision()
        
        # Store interaction
        self.interaction_history.append({
            'context': context,
            'decision': decision,
            'timestamp': len(self.interaction_history),
            'mock': True
        })
        
        return decision
    
    Agent.decide = mock_decide
    return original_decide


def run_offline_demo():
    """运行离线演示（不调用LLM API）"""
    print("=== ABM数智化治理仿真系统 - 离线演示 ===\n")
    print("🚀 使用模拟决策模式运行（无需API密钥）")
    print("注意：此模式使用预设决策逻辑，不调用LLM\n")
    
    # Mock LLM to avoid API calls
    original_decide = mock_llm_response()
    
    try:
        # 快速演示：只运行5轮
        num_rounds = 5
        
        print(f"1. 运行北京仿真（{num_rounds}轮）...")
        beijing_results = run_simulation('beijing', num_rounds=num_rounds)
        print("✅ 北京仿真完成")
        print(f"   - 平均响应时间: {beijing_results['metrics']['efficiency']['avg_response_time']:.2f}")
        print(f"   - 服务公平性: {1-beijing_results['metrics']['fairness']['service_access_gini']:.2f}")
        
        print(f"\n2. 运行深圳仿真（{num_rounds}轮）...")
        shenzhen_results = run_simulation('shenzhen', num_rounds=num_rounds)
        print("✅ 深圳仿真完成")
        print(f"   - 平均响应时间: {shenzhen_results['metrics']['efficiency']['avg_response_time']:.2f}")
        print(f"   - 服务公平性: {1-shenzhen_results['metrics']['fairness']['service_access_gini']:.2f}")
        
        print(f"\n3. 运行政策干预仿真（{num_rounds}轮）...")
        policy_results = run_simulation(
            'shenzhen', 
            policy_interventions=['digital_literacy_training'],
            num_rounds=num_rounds
        )
        print("✅ 政策干预仿真完成")
        print(f"   - 数字鸿沟指数: {policy_results['metrics']['fairness']['digital_divide_index']:.3f}")
        
        # 保存结果
        print("\n4. 保存结果...")
        save_results(beijing_results, 'offline_beijing_results.json')
        save_results(shenzhen_results, 'offline_shenzhen_results.json')  
        save_results(policy_results, 'offline_policy_results.json')
        print("✅ 结果已保存到 output/")
        
        # 简单对比
        print("\n=== 对比分析（基于模拟决策） ===")
        print(f"效率对比（响应时间，越低越好）:")
        print(f"  北京: {beijing_results['metrics']['efficiency']['avg_response_time']:.2f}")
        print(f"  深圳: {shenzhen_results['metrics']['efficiency']['avg_response_time']:.2f}")
        
        print(f"\n公平性对比（服务公平性，越高越好）:")
        beijing_fairness = 1 - beijing_results['metrics']['fairness']['service_access_gini']
        shenzhen_fairness = 1 - shenzhen_results['metrics']['fairness']['service_access_gini']
        print(f"  北京: {beijing_fairness:.3f}")
        print(f"  深圳: {shenzhen_fairness:.3f}")
        
        print(f"\n政策效果（数字鸿沟，越低越好）:")
        baseline_divide = shenzhen_results['metrics']['fairness']['digital_divide_index']
        policy_divide = policy_results['metrics']['fairness']['digital_divide_index']
        print(f"  政策前: {baseline_divide:.3f}")
        print(f"  政策后: {policy_divide:.3f}")
        print(f"  改善程度: {baseline_divide - policy_divide:.3f}")
        
        print("\n✅ 离线演示完成！")
        print("💡 提示：设置API密钥后可运行完整LLM驱动仿真")
        print("   set ZAI_API_KEY=your-api-key && python main.py")
        
    except Exception as e:
        print(f"\n❌ 离线演示失败: {e}")
        print("请检查系统基础功能")
    
    finally:
        # Restore original method
        from simulation.agent import Agent
        Agent.decide = original_decide


def show_system_status():
    """显示系统状态"""
    print("=== 系统状态检查 ===\n")
    
    try:
        # 检查配置文件
        print("1. 配置文件检查:")
        config_files = ['agents.json', 'environments.json', 'rules.json', 'policies.json']
        for config_file in config_files:
            try:
                with open(f'config/{config_file}', 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"   ✅ {config_file}")
            except Exception as e:
                print(f"   ❌ {config_file}: {e}")
        
        # 检查提示词模板
        print("\n2. 提示词模板检查:")
        prompt_files = ['government_prompt.txt', 'enterprise_prompt.txt', 'resident_prompt.txt']
        for prompt_file in prompt_files:
            try:
                with open(f'prompts/{prompt_file}', 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"   ✅ {prompt_file} ({len(content)} chars)")
            except Exception as e:
                print(f"   ❌ {prompt_file}: {e}")
        
        # 检查模块导入
        print("\n3. 模块导入检查:")
        try:
            from simulation.agent import create_agents
            print("   ✅ Agent模块")
        except Exception as e:
            print(f"   ❌ Agent模块: {e}")
        
        try:
            from simulation.environment import Environment
            print("   ✅ Environment模块")
        except Exception as e:
            print(f"   ❌ Environment模块: {e}")
        
        try:
            from metrics import calculate_efficiency
            print("   ✅ Metrics模块")
        except Exception as e:
            print(f"   ❌ Metrics模块: {e}")
        
        # 检查API密钥
        print("\n4. API密钥检查:")
        api_key = os.getenv('ZAI_API_KEY')
        if api_key and api_key != 'your-zhipuai-api-key':
            print(f"   ✅ API密钥已设置 ({api_key[:10]}...)")
        else:
            print("   ⚠️  API密钥未设置（将使用离线模式）")
        
        print("\n✅ 系统状态检查完成")
        
    except Exception as e:
        print(f"\n❌ 系统状态检查失败: {e}")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        show_system_status()
    else:
        run_offline_demo()