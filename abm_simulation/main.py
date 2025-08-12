"""
Main simulation entry point for ABM digital governance framework
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional

# Import simulation components
from simulation.agent import create_agents
from simulation.environment import Environment
from simulation.interaction import InteractionEngine
from simulation.policy_engine import PolicyEngine
from simulation.logger import SimulationLogger, create_logger
from metrics import (
    calculate_efficiency,
    calculate_fairness,
    calculate_resilience, 
    calculate_agent_status,
    calculate_collaboration
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config() -> tuple:
    """
    Load configuration files
    
    Returns:
        Tuple of (agents_config, env_config, rules_config, policies_config)
    """
    try:
        with open('config/agents.json', 'r', encoding='utf-8') as f:
            agents_config = json.load(f)
        
        with open('config/environments.json', 'r', encoding='utf-8') as f:
            env_config = json.load(f)
        
        with open('config/rules.json', 'r', encoding='utf-8') as f:
            rules_config = json.load(f)
        
        with open('config/policies.json', 'r', encoding='utf-8') as f:
            policies_config = json.load(f)
        
        return agents_config, env_config, rules_config, policies_config
    
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON configuration: {e}")
        raise


def run_simulation(
    city: str, 
    policy_interventions: Optional[List[str]] = None,
    num_rounds: int = 100,
    num_enterprises: int = 10,
    num_residents: int = 100,
    enable_logging: bool = True,
    log_file: str = None
) -> Dict[str, Any]:
    """
    Run ABM simulation for specified city
    
    Args:
        city: City name (beijing/shenzhen)
        policy_interventions: List of policy interventions to apply
        num_rounds: Number of simulation rounds
        num_enterprises: Number of enterprise agents to create
        num_residents: Number of resident agents to create
        enable_logging: Whether to enable dynamic logging
        log_file: Custom log file name
        
    Returns:
        Dictionary containing simulation results and metrics
    """
    logger.info(f"Starting simulation for {city} with {num_rounds} rounds")
    
    # Load configuration
    agents_config, env_config, rules_config, policies_config = load_config()
    
    # Validate city configuration
    if city not in env_config:
        raise ValueError(f"Unknown city: {city}. Available cities: {list(env_config.keys())}")
    
    # Initialize environment
    env = Environment(env_config[city])
    logger.info(f"Environment initialized for {city}")
    
    # Initialize dynamic logger
    sim_logger = None
    if enable_logging:
        sim_logger = create_logger(city, log_file)

    # Create agents
    agents = create_agents(agents_config, city, num_enterprises, num_residents)
    government = agents['government']
    enterprises = agents['enterprises']
    residents = agents['residents']
    
    agent_counts = {
        'government': 1,
        'enterprises': len(enterprises),
        'residents': len(residents)
    }
    
    logger.info(f"Created agents: 1 government, {len(enterprises)} enterprises, {len(residents)} residents")
    
    if sim_logger:
        sim_logger.log_round_start(-1, agent_counts)  # -1 表示初始化阶段
    
    # Apply policy interventions if specified
    if policy_interventions:
        policy_engine = PolicyEngine(policies_config)
        policy_engine.apply(government, enterprises, residents, env, policy_interventions)
        logger.info(f"Applied policy interventions: {policy_interventions}")
    
    # Initialize interaction engine
    interaction_engine = InteractionEngine(rules_config)
    
    # Simulation records storage
    simulation_records = []
    
    # Run simulation rounds
    for round_num in range(num_rounds):
        logger.debug(f"Running round {round_num + 1}/{num_rounds}")
        
        if sim_logger:
            sim_logger.log_round_start(round_num, agent_counts)
        
        try:
            # Get environment context
            env_context = env.get_context()
            
            # Agent decision making with error handling
            gov_decision = government.decide(env_context)
            if sim_logger:
                sim_logger.log_agent_decision(
                    round_num, 'government', 'gov_0', gov_decision,
                    is_fallback='fallback' in government.interaction_history[-1] if government.interaction_history else False
                )

            ent_decisions = []
            for i, enterprise in enumerate(enterprises):
                try:
                    decision = enterprise.decide(env_context)
                    ent_decisions.append(decision)
                    
                    if sim_logger:
                        is_fallback = ('fallback' in enterprise.interaction_history[-1] 
                                     if enterprise.interaction_history else False)
                        error_msg = (enterprise.interaction_history[-1].get('error') 
                                   if enterprise.interaction_history and is_fallback else None)
                        sim_logger.log_agent_decision(
                            round_num, 'enterprise', f'ent_{i}', decision,
                            is_fallback=is_fallback, error=error_msg
                        )
                except Exception as e:
                    logger.error(f"Enterprise {i} decision failed: {e}")
                    if sim_logger:
                        sim_logger.log_error(round_num, str(e), "enterprise_decision")
                    # Use default decision
                    default_decision = enterprise._get_default_decision()
                    ent_decisions.append(default_decision)

            res_decisions = []
            for i, resident in enumerate(residents):
                try:
                    decision = resident.decide(env_context)
                    res_decisions.append(decision)
                    
                    # 只记录前10个居民的决策（避免日志过大）
                    if sim_logger and i < 10:
                        is_fallback = ('fallback' in resident.interaction_history[-1] 
                                     if resident.interaction_history else False)
                        error_msg = (resident.interaction_history[-1].get('error') 
                                   if resident.interaction_history and is_fallback else None)
                        sim_logger.log_agent_decision(
                            round_num, 'resident', f'res_{i}', decision,
                            is_fallback=is_fallback, error=error_msg
                        )
                except Exception as e:
                    logger.error(f"Resident {i} decision failed: {e}")
                    if sim_logger and i == 0:  # 只记录第一个错误
                        sim_logger.log_error(round_num, str(e), "resident_decision")
                    # Use default decision
                    default_decision = resident._get_default_decision()
                    res_decisions.append(default_decision)
            
            # Process interactions
            interactions = interaction_engine.process(
                government, enterprises, residents,
                gov_decision, ent_decisions, res_decisions
            )
            
            if sim_logger:
                sim_logger.log_interactions(round_num, interactions)
            
            # Update environment
            env.update(interactions)
            
            if sim_logger:
                sim_logger.log_environment_update(round_num, env.get_state())
            
            # Record round data
            round_record = {
                'round': round_num,
                'interactions': interactions,
                'environment': env.get_state(),
                'agents': {
                    'government': government.state,
                    'enterprises': [e.state for e in enterprises],
                    'residents': [r.state for r in residents]
                },
                'decisions_sample': { # Store sample of decisions for quick review
                    'government': gov_decision,
                    'enterprises': ent_decisions[:5],  # Store sample for performance
                    'residents': res_decisions[:10]   # Store sample for performance
                }
            }
            
            simulation_records.append(round_record)
            
            if sim_logger:
                sim_logger.log_round_complete(round_num)
            
            # Log progress every 10 rounds
            if (round_num + 1) % 10 == 0:
                logger.info(f"Completed round {round_num + 1}/{num_rounds}")
                if sim_logger:
                    status = sim_logger.get_current_status()
                    logger.info(f"当前状态: {status['summary']}")
        
        except KeyboardInterrupt:
            logger.info("模拟被用户中断")
            if sim_logger:
                sim_logger.interrupt_simulation("用户键盘中断")
            break
        except Exception as e:
            logger.error(f"Error in simulation round {round_num + 1}: {e}")
            if sim_logger:
                sim_logger.log_error(round_num, str(e), "simulation_round")
            continue
    
    logger.info("Simulation rounds completed, calculating metrics...")
    
    # Calculate evaluation metrics
    try:
        metrics = calculate_metrics(simulation_records, government, enterprises, residents)
        logger.info("Metrics calculation completed")
        
        if sim_logger:
            sim_logger.log_simulation_complete(metrics)
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        metrics = {}
        if sim_logger:
            sim_logger.log_error(-1, str(e), "metrics_calculation")
    
    # Compile results
    results = {
        'city': city,
        'num_rounds': num_rounds,
        'policy_interventions': policy_interventions or [],
        'metrics': metrics,
        'raw_records': simulation_records # Keep raw records for detailed analysis
    }
    
    logger.info(f"Simulation completed for {city}")
    if sim_logger:
        logger.info(f"✅ 模拟完成，日志已保存: {sim_logger.log_filepath}")
    return results


def calculate_metrics(
    simulation_records: List[Dict[str, Any]],
    government: Any,
    enterprises: List[Any],
    residents: List[Any]
) -> Dict[str, Any]:
    """
    Calculate all evaluation metrics
    
    Args:
        simulation_records: List of simulation records
        government: Government agent
        enterprises: List of enterprise agents
        residents: List of resident agents
        
    Returns:
        Dictionary containing all calculated metrics
    """
    # Extract interaction records for efficiency calculation
    all_interactions = []
    for record in simulation_records:
        all_interactions.extend(record.get('interactions', []))
    
    # Extract resident data for fairness calculation
    resident_data = []
    for resident in residents:
        resident_state = resident.get_state()
        resident_data.append({
            'area': getattr(resident, 'area', 'core_area'),
            'digital_access': resident_state['state'].get('digital_access', True),
            'service_usage_frequency': resident_state['state'].get('service_usage_frequency', 5),
            'satisfaction': resident_state['state'].get('satisfaction', 3.0),
            'income_level': resident_state['attributes'].get('income_level', 5000)
        })
    
    # Calculate individual metric categories
    efficiency_metrics = calculate_efficiency(all_interactions)
    fairness_metrics = calculate_fairness(resident_data)
    resilience_metrics = calculate_resilience(simulation_records)
    agent_status_metrics = calculate_agent_status(
        government.get_state(), 
        [e.get_state() for e in enterprises],
        [r.get_state() for r in residents]
    )
    collaboration_metrics = calculate_collaboration(simulation_records)
    
    return {
        'efficiency': efficiency_metrics,
        'fairness': fairness_metrics,
        'resilience': resilience_metrics,
        'agent_status': agent_status_metrics,
        'collaboration': collaboration_metrics
    }


def compare_cities(policy_interventions: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Compare simulation results between Beijing and Shenzhen
    
    Args:
        policy_interventions: Policy interventions to apply to both cities
        
    Returns:
        Comparison results
    """
    logger.info("Starting city comparison simulation")
    
    # Run simulations for both cities
    beijing_results = run_simulation('beijing', policy_interventions)
    shenzhen_results = run_simulation('shenzhen', policy_interventions)
    
    # Calculate comparison metrics
    comparison = {
        'beijing': beijing_results,
        'shenzhen': shenzhen_results,
        'comparison_summary': {
            'efficiency_comparison': {
                'beijing_avg_response_time': beijing_results['metrics']['efficiency']['avg_response_time'],
                'shenzhen_avg_response_time': shenzhen_results['metrics']['efficiency']['avg_response_time'],
                'efficiency_winner': 'beijing' if beijing_results['metrics']['efficiency']['avg_response_time'] < shenzhen_results['metrics']['efficiency']['avg_response_time'] else 'shenzhen'
            },
            'fairness_comparison': {
                'beijing_gini': beijing_results['metrics']['fairness']['service_access_gini'],
                'shenzhen_gini': shenzhen_results['metrics']['fairness']['service_access_gini'],
                'fairness_winner': 'beijing' if beijing_results['metrics']['fairness']['service_access_gini'] < shenzhen_results['metrics']['fairness']['service_access_gini'] else 'shenzhen'
            }
        }
    }
    
    logger.info("City comparison completed")
    return comparison


def save_results(results: Dict[str, Any], filename: str):
    """
    Save simulation results to JSON file
    
    Args:
        results: Simulation results dictionary
        filename: Output filename
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        
        # Save results (excluding raw records for file size)
        output_results = results.copy()
        if 'raw_records' in output_results:
            output_results['raw_records'] = f"Excluded {len(output_results['raw_records'])} records for file size"
        
        filepath = f'output/{filename}'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {filepath}")
    except Exception as e:
        logger.error(f"Error saving results: {e}")


def interactive_city_selection():
    """交互式城市选择和模拟配置"""
    print("=== ABM数智化治理仿真系统 ===\n")
    
    while True:
        print("请选择运行模式:")
        print("1. 北京模拟")
        print("2. 深圳模拟") 
        print("3. 城市对比分析")
        print("4. 政策干预模拟")
        print("5. 全自动模拟 (所有城市)")
        print("6. 退出")
        
        try:
            choice = input("\n请选择 (1-6): ").strip()
            
            if choice == '1':
                run_single_city_simulation('beijing')
            elif choice == '2':
                run_single_city_simulation('shenzhen')
            elif choice == '3':
                run_city_comparison_interactive()
            elif choice == '4':
                run_policy_intervention_interactive()
            elif choice == '5':
                run_all_simulations()
            elif choice == '6':
                print("退出系统")
                break
            else:
                print("无效选择，请重新输入")
                continue
                
            # 询问是否继续
            if input("\n是否继续使用系统? (y/N): ").strip().lower() != 'y':
                break
                
        except KeyboardInterrupt:
            print("\n\n系统已退出")
            break
        except Exception as e:
            print(f"运行出错: {e}")
            continue


def run_single_city_simulation(city: str):
    """运行单个城市模拟"""
    city_name = "北京" if city == 'beijing' else "深圳"
    print(f"\n🚀 开始运行{city_name}模拟...")
    
    # 配置选项
    rounds = int(input("请输入模拟轮次 (默认20): ") or "20")
    enterprises = int(input("请输入企业数量 (默认5): ") or "5")
    residents = int(input("请输入居民数量 (默认50): ") or "50")
    
    print(f"\n📋 配置确认:")
    print(f"- 城市: {city_name}")
    print(f"- 模拟轮次: {rounds}")
    print(f"- 企业数量: {enterprises}")
    print(f"- 居民数量: {residents}")
    print(f"- 实时日志: 启用")
    
    try:
        results = run_simulation(
            city, 
            num_rounds=rounds,
            num_enterprises=enterprises,
            num_residents=residents,
            enable_logging=True,
            log_file=f"{city}_interactive_{rounds}rounds"
        )
        
        print(f"✅ {city_name}模拟完成")
        print(f"\n📊 {city_name}模拟结果:")
        print(f"- 平均响应时间: {results['metrics']['efficiency']['avg_response_time']:.2f}")
        print(f"- 服务公平性: {1-results['metrics']['fairness']['service_access_gini']:.3f}")
        print(f"- 系统韧性: {results['metrics']['resilience']['stability_index']:.3f}")
        
        # 保存结果
        save_results(results, f'{city}_simulation_{rounds}rounds.json')
        print(f"📁 结果已保存到 output/{city}_simulation_{rounds}rounds.json")
        print(f"📝 实时日志已保存到 output/{city}_interactive_{rounds}rounds.json")
        
    except Exception as e:
        print(f"❌ {city_name}模拟失败: {e}")


def run_city_comparison_interactive():
    """运行交互式城市对比分析"""
    print("\n🚀 开始运行城市对比分析...")
    
    # 配置选项
    rounds = int(input("请输入模拟轮次 (默认20): ") or "20")
    
    try:
        print("正在运行北京模拟...")
        beijing_results = run_simulation('beijing', num_rounds=rounds)
        
        print("正在运行深圳模拟...")
        shenzhen_results = run_simulation('shenzhen', num_rounds=rounds)
        
        # 对比分析
        comparison = {
            'beijing': beijing_results,
            'shenzhen': shenzhen_results,
            'comparison_summary': {
                'efficiency_comparison': {
                    'beijing_avg_response_time': beijing_results['metrics']['efficiency']['avg_response_time'],
                    'shenzhen_avg_response_time': shenzhen_results['metrics']['efficiency']['avg_response_time'],
                    'efficiency_winner': 'beijing' if beijing_results['metrics']['efficiency']['avg_response_time'] < shenzhen_results['metrics']['efficiency']['avg_response_time'] else 'shenzhen'
                },
                'fairness_comparison': {
                    'beijing_gini': beijing_results['metrics']['fairness']['service_access_gini'],
                    'shenzhen_gini': shenzhen_results['metrics']['fairness']['service_access_gini'],
                    'fairness_winner': 'beijing' if beijing_results['metrics']['fairness']['service_access_gini'] < shenzhen_results['metrics']['fairness']['service_access_gini'] else 'shenzhen'
                }
            }
        }
        
        print("✅ 城市对比分析完成")
        print(f"\n📊 对比结果:")
        print(f"🏃‍♂️ 效率对比:")
        print(f"  - 北京响应时间: {beijing_results['metrics']['efficiency']['avg_response_time']:.2f}")
        print(f"  - 深圳响应时间: {shenzhen_results['metrics']['efficiency']['avg_response_time']:.2f}")
        print(f"  - 效率优势: {comparison['comparison_summary']['efficiency_comparison']['efficiency_winner']}")
        
        print(f"⚖️ 公平性对比:")
        print(f"  - 北京服务公平性: {1-beijing_results['metrics']['fairness']['service_access_gini']:.3f}")
        print(f"  - 深圳服务公平性: {1-shenzhen_results['metrics']['fairness']['service_access_gini']:.3f}")
        print(f"  - 公平优势: {comparison['comparison_summary']['fairness_comparison']['fairness_winner']}")
        
        # 保存结果
        save_results(comparison, f'city_comparison_{rounds}rounds.json')
        print(f"📁 对比结果已保存到 output/city_comparison_{rounds}rounds.json")
        
    except Exception as e:
        print(f"❌ 城市对比分析失败: {e}")


def run_policy_intervention_interactive():
    """运行交互式政策干预模拟"""
    print("\n🚀 开始运行政策干预模拟...")
    
    # 选择城市
    print("选择目标城市:")
    print("1. 北京")
    print("2. 深圳")
    city_choice = input("请选择 (1-2): ").strip()
    city = 'beijing' if city_choice == '1' else 'shenzhen'
    city_name = "北京" if city == 'beijing' else "深圳"
    
    # 选择政策干预
    print("\n可用的政策干预:")
    print("1. digital_literacy_training - 数字素养培训")
    print("2. data_open_sharing - 数据开放共享")
    print("3. algorithm_regulation - 算法规制")
    print("4. inclusive_infrastructure - 包容性基础设施")
    
    policy_choice = input("请选择政策编号 (1-4): ").strip()
    policy_map = {
        '1': 'digital_literacy_training',
        '2': 'data_open_sharing', 
        '3': 'algorithm_regulation',
        '4': 'inclusive_infrastructure'
    }
    
    policy = policy_map.get(policy_choice, 'digital_literacy_training')
    rounds = int(input("请输入模拟轮次 (默认20): ") or "20")
    
    try:
        # 运行基线模拟
        print(f"正在运行{city_name}基线模拟...")
        baseline_results = run_simulation(city, num_rounds=rounds)
        
        # 运行政策干预模拟
        print(f"正在运行{city_name}政策干预模拟...")
        intervention_results = run_simulation(city, policy_interventions=[policy], num_rounds=rounds)
        
        print("✅ 政策干预模拟完成")
        print(f"\n📊 政策干预效果分析:")
        print(f"📈 基线结果:")
        print(f"  - 响应时间: {baseline_results['metrics']['efficiency']['avg_response_time']:.2f}")
        print(f"  - 服务公平性: {1-baseline_results['metrics']['fairness']['service_access_gini']:.3f}")
        
        print(f"🎯 干预后结果:")
        print(f"  - 响应时间: {intervention_results['metrics']['efficiency']['avg_response_time']:.2f}")
        print(f"  - 服务公平性: {1-intervention_results['metrics']['fairness']['service_access_gini']:.3f}")
        
        # 计算改进
        efficiency_change = baseline_results['metrics']['efficiency']['avg_response_time'] - intervention_results['metrics']['efficiency']['avg_response_time']
        fairness_change = (1-intervention_results['metrics']['fairness']['service_access_gini']) - (1-baseline_results['metrics']['fairness']['service_access_gini'])
        
        print(f"📊 改进效果:")
        print(f"  - 效率改进: {efficiency_change:+.2f} (负值表示改善)")
        print(f"  - 公平性改进: {fairness_change:+.3f}")
        
        # 保存结果
        policy_results = {
            'city': city,
            'policy': policy,
            'baseline': baseline_results,
            'intervention': intervention_results,
            'improvement': {
                'efficiency_change': efficiency_change,
                'fairness_change': fairness_change
            }
        }
        
        save_results(policy_results, f'{city}_{policy}_intervention_{rounds}rounds.json')
        print(f"📁 政策干预结果已保存到 output/{city}_{policy}_intervention_{rounds}rounds.json")
        
    except Exception as e:
        print(f"❌ 政策干预模拟失败: {e}")


def run_all_simulations():
    """运行所有城市的完整模拟"""
    print("\n🚀 开始运行全自动模拟...")
    
    try:
        # Run Beijing simulation
        print("\n=== 运行北京模拟 ===")
        beijing_metrics = run_simulation('beijing')
        print("北京模拟结果:")
        print(f"- 治理效率: {beijing_metrics['metrics']['efficiency']}")
        print(f"- 治理公平: {beijing_metrics['metrics']['fairness']}")
        save_results(beijing_metrics, 'beijing_simulation_results.json')
        
        # Run Shenzhen simulation
        print("\n=== 运行深圳模拟 ===")
        shenzhen_metrics = run_simulation('shenzhen')
        print("深圳模拟结果:")
        print(f"- 治理效率: {shenzhen_metrics['metrics']['efficiency']}")
        print(f"- 治理公平: {shenzhen_metrics['metrics']['fairness']}")
        save_results(shenzhen_metrics, 'shenzhen_simulation_results.json')
        
        # Run policy intervention simulation (Shenzhen + digital literacy training)
        print("\n=== 运行政策干预模拟 ===")
        shenzhen_policy_metrics = run_simulation(
            'shenzhen',
            policy_interventions=['digital_literacy_training']
        )
        print("深圳政策干预结果:")
        print(f"- 治理效率: {shenzhen_policy_metrics['metrics']['efficiency']}")
        print(f"- 治理公平: {shenzhen_policy_metrics['metrics']['fairness']}")
        save_results(shenzhen_policy_metrics, 'shenzhen_policy_intervention_results.json')
        
        # City comparison
        print("\n=== 城市对比分析 ===")
        comparison_results = compare_cities()
        print("对比结果:")
        print(f"- 效率优势: {comparison_results['comparison_summary']['efficiency_comparison']['efficiency_winner']}")
        print(f"- 公平优势: {comparison_results['comparison_summary']['fairness_comparison']['fairness_winner']}")
        save_results(comparison_results, 'city_comparison_results.json')
        
        print("\n=== 模拟完成 ===")
        print("结果已保存到 abm_simulation/output/ 目录")
        
    except Exception as e:
        print(f"❌ 全自动模拟失败: {e}")


if __name__ == '__main__':
    import sys
    
    # Set API key from environment variable
    api_key = os.getenv('ZAI_API_KEY')
    if not api_key:
        logger.warning("ZAI_API_KEY environment variable not set. Using placeholder.")
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        # 自动运行所有模拟（原有功能）
        run_all_simulations()
    else:
        # 默认运行交互式城市选择
        interactive_city_selection()