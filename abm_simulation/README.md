# ABM数智化治理仿真框架

基于LLM的Agent-Based Modeling (ABM) 数智化治理仿真系统，用于模拟分析北京和深圳两地数智化治理模式差异。

## 项目概述

本项目实现了一个完整的ABM仿真框架，通过LLM驱动的智能Agent模拟政府、企业、居民三类主体在数智化治理环境中的交互行为，评估不同城市治理模式的效率、公平性、韧性等关键指标。

## 核心特性

- **LLM驱动的Agent**: 使用智谱AI GLM-4模型驱动Agent决策
- **多主体建模**: 政府、企业、居民三类Agent，支持不同属性配置
- **环境模拟**: 数字基础设施、物理基础设施、政策环境动态建模
- **交互规则**: 基于概率的主体间交互规则引擎
- **政策干预**: 可插拔式政策干预机制
- **多维评估**: 效率、公平、韧性、主体状态、协同性五维评估体系
- **城市对比**: 北京vs深圳治理模式差异对比分析

## 项目结构

```
abm_simulation/
├── config/                  # 配置文件
│   ├── agents.json          # 主体定义
│   ├── environments.json    # 环境设定
│   ├── rules.json           # 交互规则
│   └── policies.json        # 政策干预
├── prompts/                 # LLM提示词模板
│   ├── government_prompt.txt
│   ├── enterprise_prompt.txt
│   └── resident_prompt.txt
├── metrics/                 # 评估指标模块
│   ├── efficiency.py        # 治理效率
│   ├── fairness.py          # 治理公平
│   ├── resilience.py        # 治理韧性
│   ├── agent_status.py      # 主体状态
│   └── collaboration.py     # 协同性
├── simulation/              # 核心仿真模块
│   ├── agent.py             # Agent基类和子类
│   ├── environment.py       # 环境类
│   ├── interaction.py       # 交互规则引擎
│   └── policy_engine.py     # 政策干预引擎
├── main.py                  # 主程序入口
└── requirements.txt         # 依赖库
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目（如果有Git仓库）
# git clone <repository-url>

# 进入项目目录
cd CitySim/abm_simulation

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

设置智谱AI API密钥环境变量：

```bash
# Windows
set ZAI_API_KEY=your-zhipuai-api-key

# Linux/Mac
export ZAI_API_KEY=your-zhipuai-api-key
```

或者直接在代码中修改API密钥（不推荐）：
```python
# 在 simulation/agent.py 中修改
openai_api_key="your-zhipuai-api-key"
```

### 3. 运行仿真

```bash
# 运行完整仿真（包括北京、深圳对比和政策干预）
python main.py

# 或者单独运行特定城市
python -c "
from main import run_simulation
results = run_simulation('beijing')
print(results['metrics'])
"
```

## 使用说明

### 基础仿真

```python
from main import run_simulation

# 运行北京仿真
beijing_results = run_simulation('beijing')

# 运行深圳仿真  
shenzhen_results = run_simulation('shenzhen')

# 查看结果
print(beijing_results['metrics']['efficiency'])
print(shenzhen_results['metrics']['fairness'])
```

### 政策干预仿真

```python
# 应用数字素养培训政策
policy_results = run_simulation(
    'shenzhen', 
    policy_interventions=['digital_literacy_training']
)

# 应用多项政策
multi_policy_results = run_simulation(
    'beijing',
    policy_interventions=[
        'digital_literacy_training',
        'inclusive_infrastructure',
        'algorithm_regulation'
    ]
)
```

### 自定义配置

通过修改JSON配置文件自定义仿真参数：

1. **主体属性** (`config/agents.json`): 修改政府、企业、居民的初始属性
2. **环境设定** (`config/environments.json`): 调整城市基础设施水平
3. **交互规则** (`config/rules.json`): 修改主体间交互概率和效果
4. **政策配置** (`config/policies.json`): 添加或修改政策干预参数

### 提示词自定义

修改`prompts/`目录下的英文提示词模板来调整Agent行为逻辑：

- `government_prompt.txt`: 政府Agent决策逻辑
- `enterprise_prompt.txt`: 企业Agent决策逻辑  
- `resident_prompt.txt`: 居民Agent决策逻辑

## 评估指标

系统提供五个维度的评估指标：

1. **治理效率**: 平均响应时间、问题解决率、资源利用率
2. **治理公平**: 服务可及性差异、数字鸿沟程度、满意度分布
3. **治理韧性**: 系统恢复速度、服务中断率、适应能力
4. **主体状态**: 居民满意度、企业市场份额、政府目标达成度
5. **协同性**: 跨部门协作频率、联合行动率、冲突发生率

## 输出结果

仿真结果保存在`abm_simulation/output/`目录下：

- `beijing_simulation_results.json`: 北京仿真结果
- `shenzhen_simulation_results.json`: 深圳仿真结果  
- `*_policy_intervention_results.json`: 政策干预仿真结果
- `city_comparison_results.json`: 城市对比分析结果

## 技术架构

- **Agent模型**: 基于LangChain + 智谱AI GLM-4的智能Agent
- **交互机制**: 概率驱动的多主体交互规则
- **环境建模**: 动态基础设施和政策环境模拟
- **评估体系**: 多维度量化评估指标
- **政策引擎**: 可插拔式政策干预机制

## 扩展开发

### 添加新Agent类型

1. 在`simulation/agent.py`中继承`Agent`基类
2. 在`config/agents.json`中添加配置
3. 在`prompts/`中添加对应提示词模板

### 添加新评估指标

1. 在`metrics/`目录下创建新指标模块
2. 在`metrics/__init__.py`中导入
3. 在`main.py`的`calculate_metrics`函数中调用

### 添加新政策干预

1. 在`config/policies.json`中定义政策配置
2. 在`simulation/policy_engine.py`中实现应用逻辑

## 注意事项

- 确保智谱AI API密钥有效且有充足余额
- 仿真过程中会产生大量API调用，注意成本控制
- 建议先用较少轮次（如10轮）测试配置正确性
- 大规模仿真建议使用批处理模式运行

## 依赖说明

- Python 3.8+
- LangChain 0.1.0+
- 智谱AI API访问权限
- 其他依赖见`requirements.txt`

## 许可证

[根据项目需要添加许可证信息]

## 联系方式

[根据项目需要添加联系方式]