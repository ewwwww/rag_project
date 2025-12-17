# RAG技术应用

> RAG（Retrieval-Augmented Generation）检索增强生成技术的实践项目

## 📖 项目简介

本项目是 RAG（Retrieval-Augmented Generation）技术与应用的第2章内容，展示了如何使用 RAG 技术构建智能问答系统。

## ✨ 功能特性

- 🔍 **文档检索与向量化**：使用 FAISS 向量数据库实现高效的相似度检索
- 🤖 **基于 LangChain 的 RAG 实现**：集成 LangChain 框架，简化 RAG 流程开发
- 📄 **PDF 文档处理**：支持批量处理目录下所有PDF文件，自动提取文本和页码信息
- 💬 **智能问答系统**：基于检索到的文档内容生成准确答案
- 🔄 **增量更新**：自动检测新PDF文件并添加到向量数据库，无需重新处理所有文件
- 📚 **答案溯源**：显示答案来源的PDF名称和页码，便于验证和追溯
- 🎯 **交互式查询**：支持连续提问模式，提升用户体验
- ⚡ **高效检索**：使用文本嵌入模型将文档转换为向量，实现语义相似度搜索

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
pip install -r readme/requirements.txt
```

或者如果当前目录在 `readme/` 目录下：

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
编辑 `readme/run.ps1` 文件，填入你的 API Key，然后运行：
```powershell
.\readme\run.ps1
```

或者如果当前目录在 `readme/` 目录下：

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
首次运行时会处理 `dataset/` 目录下所有 PDF 文件并创建向量数据库。

**增量更新（添加新PDF文件后）：**
```bash
python main.py --init
```
系统会自动检测新文件并添加到现有向量数据库，无需重新处理所有文件。

**强制重新构建：**
```bash
python main.py --init --force
```
删除旧数据库，重新处理所有PDF文件。

**执行单次查询：**
```bash
python main.py --query "客户经理的考核标准是什么？"
```

**交互式查询模式：**
```bash
python main.py --interactive
```
进入交互式模式，可以连续提问，输入 `quit`、`exit` 或 `退出` 退出。

**查看帮助信息：**
```bash
python main.py --help
```

#### 方式2：自定义路径

```bash
# 指定数据集目录路径
python main.py --init --dataset "./your_dataset_folder"

# 指定向量数据库路径
python main.py --init --vector-store "./custom_path"
```

### 使用示例

```bash
# 1. 初始化知识库（首次运行）
python main.py --init
# 输出示例：
# ==================================================
# 初始化知识库...
# ==================================================
# 开始处理PDF文件并创建向量数据库...
# 正在处理: 浦发上海浦东发展银行西安分行个金客户经理考核办法.pdf
#   - 提取了 12345 个字符
# 正在处理: 中华人民共和国劳动法.pdf
#   - 提取了 67890 个字符
# 文本被分割成 150 个块。
# 已从文本块创建知识库...
# 向量数据库已保存到: ./vector_store
# ✅ 知识库初始化完成

# 2. 添加新PDF文件后，自动增量更新
# 将新PDF放入 dataset/ 目录
python main.py --init
# 输出示例：
# 检测到已存在的向量数据库，检查是否有新文件...
# 发现 1 个新PDF文件，开始增量更新...
# 正在处理新文件: 新文档.pdf
#   - 提取了 5000 个字符，分割成 10 个块
# ✅ 成功添加 10 个新文本块
# ✅ 向量数据库已更新并保存

# 3. 执行单次查询
python main.py --query "客户经理每年评聘申报时间是怎样的？"

# 4. 交互式查询模式
python main.py --interactive
# 输出示例：
# ==================================================
# 进入交互式查询模式
# 输入 'quit' 或 'exit' 退出
# ==================================================
# 请输入您的问题: 投诉一次扣多少分？
# 请输入您的问题: 劳动法规定的工作时间是多少？
# 请输入您的问题: quit
# 感谢使用，再见！
```

### 输出说明

查询结果包含：
- **答案内容**：基于文档内容生成的回答
- **答案来源**：显示PDF名称和页码，便于追溯和验证

**示例输出：**

```
正在处理查询：客户经理的考核标准是什么？
--------------------------------------------------
查询已处理。
根据考核办法，客户经理的考核标准主要包括以下几个方面：
1. 业绩指标：包括存款、贷款、中间业务等各项业务指标
2. 服务质量：客户满意度、投诉处理等
3. 合规管理：遵守各项规章制度，无违规行为
...

==================================================
📚 答案来源:
==================================================
  📄 文档: 浦发上海浦东发展银行西安分行个金客户经理考核办法.pdf
  📑 页码: 第 5 页

  📄 文档: 中华人民共和国劳动法.pdf
  📑 页码: 第 8 页
--------------------------------------------------
```

## 📁 项目结构

```
chapter2/
├── readme/                    # 文档和配置文件目录
│   ├── README.md              # 项目说明文档（本文件）
│   ├── requirements.txt       # 项目依赖列表
│   └── run.ps1                # PowerShell 启动脚本
├── main.py                    # 主入口文件（参数解析、流程控制）
├── knowledge_base_manager.py  # 知识库管理模块（初始化、增量更新）
├── data_process.py            # 数据处理模块（PDF提取、向量化）
├── user_query.py              # 用户查询处理模块（查询执行、结果展示）
├── .gitignore                 # Git 忽略规则
├── dataset/                   # PDF 文档目录
│   ├── *.pdf                 # PDF 文档文件（支持多个）
│   └── ...                   # 添加新PDF文件后会自动处理
└── vector_store/              # 向量数据库存储目录（自动生成）
    ├── index.faiss            # FAISS 向量索引
    ├── index.pkl              # FAISS 索引元数据
    ├── page_info.pkl          # 页码信息文件
    └── processed_files.pkl    # 已处理文件列表（用于增量更新）
```

### 模块说明

| 模块 | 职责 | 主要功能 |
|------|------|----------|
| `main.py` | 程序入口 | 命令行参数解析、流程控制、调用其他模块 |
| `knowledge_base_manager.py` | 知识库管理 | 初始化知识库、增量更新、文件列表管理 |
| `data_process.py` | 数据处理 | PDF文本提取、文本分割、向量化、数据库保存/加载 |
| `user_query.py` | 查询处理 | 查询执行、LLM调用、结果展示、溯源信息显示 |

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `DASHSCOPE_API_KEY` | 阿里云 DashScope API Key | ✅ 是 |

### 默认配置

- **数据集目录**：`./dataset`（会处理目录下所有PDF文件）
- **向量数据库路径**：`./vector_store`
- **嵌入模型**：`text-embedding-v2`（阿里云百炼平台）
- **大语言模型**：`deepseek-v3`（通过 Tongyi 调用）
- **文本分割参数**：
  - `chunk_size`: 512 字符
  - `chunk_overlap`: 128 字符
  - `separators`: `["\n\n", "\n", ".", " ", ""]`

### 技术栈

| 技术/库 | 用途 |
|---------|------|
| **LangChain** | RAG 框架，提供文档处理、向量存储、LLM 调用等功能 |
| **FAISS** | Facebook AI Similarity Search，高效的向量相似度搜索库 |
| **DashScope** | 阿里云百炼平台，提供文本嵌入和大语言模型服务 |
| **PyPDF2** | PDF 文档解析和文本提取 |
| **Tongyi** | 通义千问大语言模型接口（通过 LangChain 集成） |

### 自定义配置

可以通过命令行参数自定义：

```bash
# 自定义数据集目录
python main.py --init --dataset "./your_dataset_folder"

# 自定义向量数据库路径
python main.py --init --vector-store "./custom_store"
```

### 增量更新机制

系统会自动检测 `dataset/` 目录下的新PDF文件：

1. **首次运行**：处理所有PDF文件，创建向量数据库
2. **添加新文件后**：自动检测新文件，只处理新增的PDF
3. **强制重建**：使用 `--force` 参数重新处理所有文件

**工作流程：**
```
运行 --init
  ↓
检查向量数据库是否存在
  ├─ 不存在 → 处理所有PDF，创建数据库
  │   ├─ 提取PDF文本和页码
  │   ├─ 文本分割成块
  │   ├─ 生成向量嵌入
  │   ├─ 创建FAISS索引
  │   └─ 保存数据库和元数据
  └─ 存在 → 检查新文件
      ├─ 有新文件 → 增量更新（只处理新文件）
      │   ├─ 提取新PDF文本和页码
      │   ├─ 生成向量嵌入
      │   ├─ 添加到现有FAISS索引
      │   └─ 更新已处理文件列表
      └─ 无新文件 → 直接加载现有数据库
```

**查询流程：**
```
用户输入问题
  ↓
向量相似度搜索（在FAISS中查找最相关的文档块）
  ↓
检索到相关文档块（通常返回top-k个结果）
  ↓
构建提示词（问题 + 文档上下文）
  ↓
调用大语言模型生成答案
  ↓
解析并显示答案 + 来源信息（PDF名称和页码）
```

## ❓ 常见问题

**Q: 如何激活 conda 环境？**  
A: 使用 `conda activate jukeChapter2` 命令激活环境。

**Q: 安装依赖时出现错误怎么办？**  
A: 请确保已激活正确的 conda 环境，并检查 Python 版本是否符合要求。

**Q: 如何设置 API Key？**  
A: 在 PowerShell 中运行 `$env:DASHSCOPE_API_KEY="sk-你的密钥"`，或编辑 `readme/run.ps1` 脚本。

**Q: 向量数据库在哪里？**  
A: 默认保存在 `./vector_store` 目录，首次运行 `--init` 时自动创建。

**Q: 如何添加新的PDF文档？**  
A: 直接将新PDF文件放入 `dataset/` 目录，然后运行 `python main.py --init`，系统会自动检测并处理新文件。

**Q: 增量更新和完全重建有什么区别？**  
A: 
- **增量更新**（默认）：只处理新增的PDF文件，添加到现有数据库，速度快
- **完全重建**（`--force`）：删除旧数据库，重新处理所有PDF文件，确保数据一致性

**Q: 查询结果中的PDF名称和页码是什么意思？**  
A: 
- **PDF名称**：答案来源的文档文件名
- **页码**：答案在该文档中的具体页面
- 格式：`文档名.pdf:页码`，便于追溯和验证答案的准确性

**Q: 如何确保新添加的PDF被处理？**  
A: 系统会自动检测，如果新文件没有被处理，可以：
1. 检查 `vector_store/processed_files.pkl` 文件
2. 使用 `--force` 参数强制重新构建
3. 删除 `vector_store/` 目录后重新初始化

**Q: 支持处理多个PDF文件吗？**  
A: 是的，系统会自动处理 `dataset/` 目录下的所有PDF文件，并将它们合并到一个向量数据库中。每个PDF文件的名称和页码信息都会被保留，便于答案溯源。

**Q: 如何查看已处理的PDF文件列表？**  
A: 已处理的文件列表保存在 `vector_store/processed_files.pkl` 文件中。系统在每次增量更新时会自动更新该列表。

**Q: 如果修改了已处理的PDF文件，系统会重新处理吗？**  
A: 目前系统只检测新增文件，不会检测已处理文件的修改。如果修改了已处理的PDF文件，建议使用 `--force` 参数强制重新构建向量数据库。

**Q: 向量数据库文件很大，可以删除吗？**  
A: 可以删除 `vector_store/` 目录，但删除后需要重新运行 `--init` 来重建向量数据库。建议定期备份该目录。

**Q: 支持其他格式的文档吗（如 Word、TXT）？**  
A: 当前版本仅支持PDF格式。如需支持其他格式，需要修改 `data_process.py` 中的文档提取逻辑。

## ⚠️ 注意事项

1. **API Key 安全**：
   - 不要将 API Key 提交到 Git 仓库
   - 使用环境变量或 `.env` 文件管理密钥
   - `.gitignore` 已配置忽略敏感文件

2. **向量数据库管理**：
   - `vector_store/` 目录包含重要的索引文件，请勿手动修改
   - 定期备份 `vector_store/` 目录，避免数据丢失
   - 删除 `vector_store/` 目录后需要重新初始化

3. **PDF 文件要求**：
   - 确保PDF文件可以正常打开和读取
   - 扫描版PDF（图片格式）需要先进行OCR处理
   - 建议PDF文件大小不超过100MB

4. **性能优化**：
   - 大量PDF文件处理可能需要较长时间，请耐心等待
   - 增量更新比完全重建快得多，优先使用增量更新
   - 查询速度取决于向量数据库大小和硬件性能

5. **错误处理**：
   - 如果遇到 API 调用错误，检查网络连接和 API Key 有效性
   - 如果向量数据库加载失败，尝试使用 `--force` 重新构建
   - 查看终端输出的错误信息，根据提示解决问题

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

（待补充）

## 👤 作者

（待补充）

## 📧 联系方式

（待补充）

