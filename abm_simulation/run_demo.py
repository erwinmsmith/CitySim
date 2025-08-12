"""
Demo script for ABM digital governance simulation
快速演示脚本
"""
import os
import sys
from main import run_simulation, compare_cities, save_results


def check_api_key():
    """检查API密钥（从env文件或环境变量）"""
    # 首先尝试从env文件读取
    try:
        env_path = os.path.join('..', 'env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('api_key='):
                        api_key = line.split('=', 1)[1].strip('"\'')
                        return api_key
    except Exception:
        pass
    
    # 回退到环境变量
    return os.getenv('ZAI_API_KEY')


def run_quick_demo():
    """运行快速演示（较少轮次）"""
    print("=== ABM数智化治理仿真系统演示 ===\n")
    
    # 检查API密钥（从env文件或环境变量）
    api_key = check_api_key()
    if not api_key or api_key == 'your-zhipuai-api-key':
        print("⚠️  警告：未设置有效的智谱AI API密钥")
        print("请检查env文件或设置环境变量：set ZAI_API_KEY=your-actual-api-key")
        print("或在agent.py中直接修改API密钥")
        print("系统将使用默认决策模式运行（不调用LLM）\n")
    else:
        print(f"✅ 检测到有效API密钥: {api_key[:10]}...") 
        print("系统将使用LLM驱动的智能决策\n")
    
    try:
        # 快速演示：只运行10轮
        num_rounds = 10
        
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
        save_results(beijing_results, 'demo_beijing_results.json')
        save_results(shenzhen_results, 'demo_shenzhen_results.json')  
        save_results(policy_results, 'demo_policy_results.json')
        print("✅ 结果已保存到 abm_simulation/output/")
        
        # 简单对比
        print("\n=== 对比分析 ===")
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
        
        print("\n✅ 演示完成！")
        print("💡 提示：要运行完整仿真（100轮），请使用 python main.py")
        
    except Exception as e:
        print(f"\n❌ 演示运行失败: {e}")
        print("请检查:")
        print("1. 是否正确安装了所有依赖：pip install -r requirements.txt")
        print("2. 是否设置了API密钥：set ZAI_API_KEY=your-api-key")
        print("3. 配置文件是否完整")


def run_simple_test():
    """运行简单功能测试"""
    print("=== 系统功能测试 ===\n")
    
    try:
        from simulation.agent import create_agents
        from simulation.environment import Environment
        from metrics import calculate_efficiency, calculate_fairness
        import json
        
        # 测试配置加载
        print("1. 测试配置加载...")
        with open('config/agents.json', 'r', encoding='utf-8') as f:
            agents_config = json.load(f)
        with open('config/environments.json', 'r', encoding='utf-8') as f:
            env_config = json.load(f)
        print("✅ 配置文件加载成功")
        
        # 测试环境创建
        print("2. 测试环境创建...")
        env = Environment(env_config['beijing'])
        print("✅ 环境创建成功")
        
        # 测试Agent创建
        print("3. 测试Agent创建...")
        agents = create_agents(agents_config, 'beijing')
        print(f"✅ Agent创建成功: {len(agents['enterprises'])}企业, {len(agents['residents'])}居民")
        
        # 测试指标计算
        print("4. 测试指标计算...")
        dummy_interactions = [{'type': 'service_request', 'outcome': 'success', 'response_time': 1.0}]
        efficiency = calculate_efficiency(dummy_interactions)
        print(f"✅ 效率指标计算成功: {efficiency}")
        
        print("\n✅ 所有功能测试通过！")
        print("系统已准备就绪，可以运行完整仿真。")
        
    except Exception as e:
        print(f"\n❌ 功能测试失败: {e}")
        print("请检查项目文件完整性")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        run_simple_test()
    else:
        run_quick_demo()