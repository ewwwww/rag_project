# RAG技术应用

> RAG（Retrieval-Augmented Generation）检索增强生成技术的实践项目

## 📖 项目简介

本项目是 RAG（Retrieval-Augmented Generation）技术与应用的第2章内容，展示了如何使用 RAG 技术构建智能问答系统。

## ✨ 功能特性

- 🔍 文档检索与向量化
- 🤖 基于 LangChain 的 RAG 实现
- 📄 PDF 文档处理
- 💬 智能问答系统

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Conda（推荐）或 pip

### 安装步骤

#### 1. 克隆项目

```bash
git clone <项目地址>
cd chapter2
```

#### 2. 创建 Conda 环境

```bash
conda create -n jukeChapter2 python=3.10
conda activate jukeChapter2
```

#### 3. 安装依赖

**方式1：使用 requirements.txt（推荐）**

```bash
pip install -r requirements.txt
```

**方式2：手动安装**

```bash
pip install pypdf2
pip install dashscope
pip install langchain
pip install langchain-openai
pip install langchain-community
pip install langchain-text-splitters
pip install faiss-cpu
```

## 📝 使用方法

### 前置准备

#### 1. 配置 API Key

在使用前，需要设置 DashScope API Key（用于文本嵌入和大模型调用）：

**Windows PowerShell:**
```powershell
$env:DASHSCOPE_API_KEY="sk-你的实际API密钥"
```

**Windows CMD:**
```cmd
set DASHSCOPE_API_KEY=sk-你的实际API密钥
```

**Linux/Mac:**
```bash
export DASHSCOPE_API_KEY="sk-你的实际API密钥"
```

**或使用启动脚本：**
编辑 `run.ps1` 文件，填入你的 API Key，然后运行：
```powershell
.\run.ps1
```

#### 2. 获取 API Key

访问 [阿里云百炼平台](https://dashscope.console.aliyun.com/) 获取 API Key。

### 使用方式

#### 方式1：命令行模式（推荐）

**初始化知识库：**
```bash
python main.py --init
```
首次运行时会处理 PDF 文件并创建向量数据库。

**执行单次查询：**
```bash
python main.py --query "客户经理的考核标准是什么？"
```

**交互式查询模式：**
```bash
python main.py --interactive
```
进入交互式模式，可以连续提问，输入 `quit` 或 `exit` 退出。

**查看帮助信息：**
```bash
python main.py --help
```

#### 方式2：自定义路径

```bash
# 指定 PDF 文件路径
python main.py --init --pdf-path "./dataset/你的文档.pdf"

# 指定向量数据库路径
python main.py --init --vector-store "./custom_path"
```

### 使用示例

```bash
# 1. 初始化知识库（首次运行）
python main.py --init

# 2. 执行查询
python main.py --query "客户经理每年评聘申报时间是怎样的？"

# 3. 交互式查询
python main.py --interactive
# 然后输入问题，例如：
# 请输入您的问题: 投诉一次扣多少分？
# 请输入您的问题: quit
```

### 输出说明

查询结果包含：
- **答案内容**：基于文档内容生成的回答
- **来源页码**：答案来源的 PDF 页码，便于追溯和验证

示例输出：
```
查询已处理。
根据考核办法，客户经理的考核标准包括...

来源:
文本块页码: 5
文本块页码: 8
```

## 📁 项目结构

```
chapter2/
├── README.md              # 项目说明文档
├── requirements.txt       # 项目依赖列表
├── main.py               # 主入口文件
├── data_process.py       # 数据处理相关代码（PDF提取、向量化）
├── user_query.py         # 用户查询处理模块
├── run.ps1               # PowerShell 启动脚本
├── .gitignore           # Git 忽略规则
├── dataset/              # PDF 文档目录
│   └── *.pdf            # PDF 文档文件
└── vector_store/         # 向量数据库存储目录（自动生成）
    ├── index.faiss       # FAISS 向量索引
    ├── index.pkl        # FAISS 索引元数据
    └── page_info.pkl    # 页码信息文件
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `DASHSCOPE_API_KEY` | 阿里云 DashScope API Key | ✅ 是 |

### 默认配置

- **PDF 文件路径**：`./dataset/浦发上海浦东发展银行西安分行个金客户经理考核办法.pdf`
- **向量数据库路径**：`./vector_store`
- **嵌入模型**：`text-embedding-v2`（阿里云百炼）
- **大语言模型**：`deepseek-v3`（通过 Tongyi 调用）

### 自定义配置

可以通过命令行参数自定义：

```bash
# 自定义 PDF 路径
python main.py --init --pdf-path "./your_document.pdf"

# 自定义向量数据库路径
python main.py --init --vector-store "./custom_store"
```

## ❓ 常见问题

**Q: 如何激活 conda 环境？**  
A: 使用 `conda activate jukeChapter2` 命令激活环境。

**Q: 安装依赖时出现错误怎么办？**  
A: 请确保已激活正确的 conda 环境，并检查 Python 版本是否符合要求。

**Q: 如何设置 API Key？**  
A: 在 PowerShell 中运行 `$env:DASHSCOPE_API_KEY="sk-你的密钥"`，或编辑 `run.ps1` 脚本。

**Q: 向量数据库在哪里？**  
A: 默认保存在 `./vector_store` 目录，首次运行 `--init` 时自动创建。

**Q: 如何更换 PDF 文档？**  
A: 将新 PDF 放入 `dataset/` 目录，使用 `--pdf-path` 参数指定路径，或修改 `main.py` 中的默认路径。

**Q: 查询结果中的页码是什么意思？**  
A: 页码表示答案来源的 PDF 页面，便于追溯和验证答案的准确性。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

（待补充）

## 👤 作者

（待补充）

## 📧 联系方式

（待补充）

