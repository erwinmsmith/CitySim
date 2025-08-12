#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试新功能：可配置agent数量和实时保存
"""

from main import run_simulation, save_results

def test_configurable_simulation():
    """测试可配置的模拟功能"""
    print("🚀 测试可配置agent数量和实时保存功能...")
    
    # 测试北京模拟 - 小规模配置
    print("\n1. 测试北京模拟 (小规模配置)")
    beijing_results = run_simulation(
        city='beijing',
        num_rounds=3,
        num_enterprises=2,
        num_residents=10,
        enable_logging=True,
        log_file="test_beijing_small"
    )
    
    print("✅ 北京模拟完成")
    print(f"- 企业数量: {len(beijing_results['raw_records'][0]['agents']['enterprises'])}")
    print(f"- 居民数量: {len(beijing_results['raw_records'][0]['agents']['residents'])}")
    
    # 测试深圳模拟 - 中等规模配置
    print("\n2. 测试深圳模拟 (中等规模配置)")
    shenzhen_results = run_simulation(
        city='shenzhen',
        num_rounds=3,
        num_enterprises=3,
        num_residents=15,
        enable_logging=True,
        log_file="test_shenzhen_medium"
    )
    
    print("✅ 深圳模拟完成")
    print(f"- 企业数量: {len(shenzhen_results['raw_records'][0]['agents']['enterprises'])}")
    print(f"- 居民数量: {len(shenzhen_results['raw_records'][0]['agents']['residents'])}")
    
    # 保存测试结果
    save_results(beijing_results, 'test_beijing_results.json')
    save_results(shenzhen_results, 'test_shenzhen_results.json')
    
    print("\n✅ 所有测试完成!")
    print("📁 结果文件:")
    print("  - output/test_beijing_results.json")
    print("  - output/test_shenzhen_results.json")
    print("📝 实时日志文件:")
    print("  - output/test_beijing_small.json")
    print("  - output/test_shenzhen_medium.json")

if __name__ == '__main__':
    test_configurable_simulation()
