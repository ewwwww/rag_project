"""
RAG 系统主入口文件
"""
import os
from PyPDF2 import PdfReader
from rag_tool import (
    extract_text_with_page_numbers,
    process_text_with_splitter,
    load_knowledge_base
)


def main():
    """主函数：RAG 系统的入口点"""
    # PDF 文件路径
    pdf_path = './dataset/浦发上海浦东发展银行西安分行个金客户经理考核办法.pdf'
    
    # 向量数据库保存路径
    vector_store_path = './vector_store'
    
    # 检查向量数据库是否已存在
    if os.path.exists(vector_store_path) and os.path.exists(os.path.join(vector_store_path, 'index.faiss')):
        print("检测到已存在的向量数据库，正在加载...")
        knowledge_base = load_knowledge_base(vector_store_path)
    else:
        print("未找到向量数据库，开始处理PDF文件...")
        # 读取PDF文件
        pdf_reader = PdfReader(pdf_path)
        
        # 提取文本和页码信息
        text, page_numbers = extract_text_with_page_numbers(pdf_reader)
        print(f"已从PDF提取文本，共 {len(text)} 个字符。")
        
        # 处理文本并创建向量存储
        knowledge_base = process_text_with_splitter(
            text=text,
            page_numbers=page_numbers,
            save_path=vector_store_path
        )
    
    print("\n向量数据库准备完成！")
    print("可以在后续代码中使用 knowledge_base 进行检索和问答。")
    
    return knowledge_base


if __name__ == "__main__":
    main()

