# MindVerse - 抑郁症患者模拟系统

一个简洁、高效的抑郁症患者行为模拟系统，基于大语言模型(LLM)生成符合不同抑郁程度特征的文本内容。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
# 设置环境变量（推荐使用代理提高稳定性）
source set_model.sh
```

### 3. 快速测试

```bash
python quick_test.py
```

### 4. 运行完整示例

```bash
python example_usage_llm.py
```

## 📁 项目结构

```
MindVerse/
├── 🔧 配置文件
│   ├── set_model.sh           # 环境变量快速设置
│   ├── requirements.txt       # Python依赖
│   └── .gitignore            # Git忽略文件
│
├── 📚 核心模块
│   ├── config/               # 配置管理
│   ├── core/                 # 核心模型（患者代理）
│   ├── interactions/         # 交互模块
│   └── utils/                # 工具模块
│       ├── clients/          # LLM客户端 ⭐
│       ├── generators/       # 提示词生成器
│       ├── config/          # 配置工具
│       └── logging/         # 日志工具
│
├── 🧪 示例和测试
│   ├── quick_test.py         # 快速连接测试
│   ├── example_usage_llm.py  # 完整LLM集成示例
│   └── example_usage.py     # 基础使用示例
│
├── 📊 分析和日志
│   ├── stability_analysis/   # 稳定性分析工具
│   ├── stability_results/    # 分析结果
│   └── logs/                # 生成的日志文件
│
└── 📖 文档
    └── LLM_INTEGRATION.md    # LLM集成说明
```

## 🔑 核心特性

### 🤖 统一的LLM客户端 (`utils.clients.TextGenerator`)

- **自动检测代理配置**：优先使用代理，提高API稳定性
- **多模型支持**：OpenAI GPT、DeepSeek、Gemini
- **简洁API**：统一的 `.generate()` 接口
- **错误处理**：完善的异常处理和重试机制

```python
from utils.clients import TextGenerator

# 自动从环境变量创建
generator = TextGenerator.create_from_env("gpt-3.5-turbo")

# 简单生成
response = generator.generate("你好", max_tokens=50)

# 带元数据生成
result = generator.generate_with_metadata("你好", max_tokens=50)
```

### 👥 患者代理模拟

- **多维度配置**：年龄、性别、教育、职业、抑郁程度
- **个性化输出**：基于配置生成符合特征的文本
- **完整日志**：自动记录所有生成内容

### 🔧 代理配置

系统自动检测并优先使用代理配置，提高国内用户的API访问稳定性：

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_PROXY_BASE_URL="your-proxy-url"  # 可选，但推荐
```

## 📖 使用指南

### 基础使用

```python
from utils.clients import TextGenerator
from core.models import PatientAgent

# 1. 创建LLM客户端
llm = TextGenerator.create_from_env("gpt-3.5-turbo")

# 2. 创建患者代理
patient = PatientAgent(
    age=25, 
    gender="女", 
    depression_level="中度"
)

# 3. 生成内容
prompt = patient.generate_self_description_prompt()
response = llm.generate(prompt)
print(response)
```

### 高级使用

查看 `example_usage_llm.py` 了解完整的功能演示。

## 🛠️ 故障排除

1. **API连接问题**：运行 `python quick_test.py` 诊断
2. **代理配置**：确保 `OPENAI_PROXY_BASE_URL` 正确设置
3. **依赖问题**：确保运行了 `pip install -r requirements.txt`

## 📝 更新日志

- **v2.0** (2025-08-01): 重构LLM客户端架构，简化代理配置，统一接口
- **v1.0**: 初始版本

---

💡 **提示**：首次使用时建议运行 `source set_model.sh && python quick_test.py` 验证配置。
