from langchain_community.llms import Tongyi
from data_process import load_knowledge_base
from langchain_community.embeddings import DashScopeEmbeddings
import os

# 设置查询问题
# query = "客户经理被投诉了，投诉一次扣多少分？"

def run_query_mode(query: str, vector_store_path: str = "./vector_store"):
    """
    运行查询模式：使用已初始化的知识库进行问答
    
    参数:
        query: 用户查询问题
        vector_store_path: 向量数据库路径（默认使用 ./vector_store）
    
    返回:
        bool: 查询是否成功执行
    """
    try:
        print(f"\n正在处理查询：{query}")
        print("-" * 50)
        user_query(query, vector_store_path)
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ 查询处理失败：{e}")
        return False


def user_query(query: str, vector_store_path: str = "./vector_store"):
    if query:
        # 示例：如何加载已保存的向量数据库
        # 注释掉以下代码以避免在当前运行中重复加载
        # 创建嵌入模型
        embeddings = DashScopeEmbeddings(
            model="text-embedding-v2"
        )
        # 从磁盘加载向量数据库
        loaded_knowledgeBase = load_knowledge_base(vector_store_path, embeddings)
        # 使用加载的知识库进行查询
        docs = loaded_knowledgeBase.similarity_search(query)
        
        # 初始化对话大模型
        DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
        llm = Tongyi(model_name="deepseek-v3", dashscope_api_key=DASHSCOPE_API_KEY)
        
        # 使用简单的 LLM 调用模式（兼容所有版本）
        # 将文档内容组合作为上下文
        context = "\n\n".join([doc.page_content for doc in docs])
        prompt = f"基于以下文档内容回答问题：\n\n{context}\n\n问题：{query}\n\n答案："
        

        response_text = llm.invoke(prompt)

        
        print("查询已处理。")
        print(response_text)
        print("\n" + "=" * 50)
        print("📚 答案来源:")
        print("=" * 50)

        # 记录唯一的来源信息（PDF名称和页码）
        unique_sources = set()

        # 显示每个文档块的来源信息
        for doc in docs:
            text_content = getattr(doc, "page_content", "")
            source_info = loaded_knowledgeBase.page_info.get(
                text_content.strip(), "未知"
            )

            if source_info not in unique_sources:
                unique_sources.add(source_info)
                # 解析PDF名称和页码
                if ":" in str(source_info):
                    pdf_name, page_num = str(source_info).split(":", 1)
                    print(f"  📄 文档: {pdf_name}")
                    print(f"  📑 页码: 第 {page_num} 页")
                    print()
                else:
                    # 兼容旧格式（纯数字页码）
                    print(f"  📑 页码: 第 {source_info} 页")
                    print()