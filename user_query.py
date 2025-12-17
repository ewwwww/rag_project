from langchain_community.llms import Tongyi
from data_process import load_knowledge_base
from langchain_community.embeddings import DashScopeEmbeddings
import os

# 设置查询问题
# query = "客户经理被投诉了，投诉一次扣多少分？"

def user_query(query: str):
    if query:
        # 示例：如何加载已保存的向量数据库
        # 注释掉以下代码以避免在当前运行中重复加载
        # 创建嵌入模型
        embeddings = DashScopeEmbeddings(
            model="text-embedding-v2"
        )
        # 从磁盘加载向量数据库
        loaded_knowledgeBase = load_knowledge_base("./vector_store", embeddings)
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
        print("来源:")

        # 记录唯一的页码
        unique_pages = set()

        # 显示每个文档块的来源页码
        for doc in docs:
            text_content = getattr(doc, "page_content", "")
            source_page = loaded_knowledgeBase.page_info.get(
                text_content.strip(), "未知"
            )

            if source_page not in unique_pages:
                unique_pages.add(source_page)
                print(f"文本块页码: {source_page}")