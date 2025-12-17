import os
import logging
import pickle
from PyPDF2 import PdfReader
# 以下导入为预留，用于后续问答功能（当前未使用）
# from langchain.chains.question_answering import load_qa_chain
# from langchain_openai import OpenAI, ChatOpenAI
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.callbacks.manager import get_openai_callback
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from typing import List, Tuple

def extract_text_with_page_numbers(pdf) -> Tuple[str, List[int]]:
    """
    从PDF中提取文本并记录每行文本对应的页码
    
    参数:
        pdf: PDF文件对象
    
    返回:
        text: 提取的文本内容
        page_numbers: 每行文本对应的页码列表
    """
    text = ""
    page_numbers = []

    for page_number, page in enumerate(pdf.pages, start=1):
        extracted_text = page.extract_text()
        if extracted_text:
            text += extracted_text
            page_numbers.extend([page_number] * len(extracted_text.split("\n")))
        else:
            logging.warning(f"No text found on page {page_number}.")

    return text, page_numbers

def process_text_with_splitter(text: str, page_numbers: List[int], save_path: str = None) -> FAISS:
    """
    处理文本并创建向量存储
    
    参数:
        text: 提取的文本内容
        page_numbers: 每行文本对应的页码列表
        save_path: 可选，保存向量数据库的路径
    
    返回:
        knowledgeBase: 基于FAISS的向量存储对象
    """
    # 创建文本分割器，用于将长文本分割成小块
    text_splitter = RecursiveCharacterTextSplitter(
        separators = ["\n\n", "\n", ".", " ", ""],
        chunk_size = 512,
        chunk_overlap = 128,
        length_function = len,
    )

    # 分割文本
    chunks = text_splitter.split_text(text)
    # logging.debug(f"Text split into {len(chunks)} chunks.")
    print(f"文本被分割成 {len(chunks)} 个块。")

    # 调用阿里百炼平台文本嵌入模型，配置环境变量 DASHSCOPE_API_KEY
    embeddings = DashScopeEmbeddings(
        model = "text-embedding-v2"
    )
    # 从文本块创建知识库
    knowledgeBase = FAISS.from_texts(chunks, embeddings)
    print("已从文本块创建知识库...")
    
    # 存储每个文本块对应的页码信息
    page_info = {chunk: page_numbers[i] for i, chunk in enumerate(chunks)}
    knowledgeBase.page_info = page_info

    # 如果提供了保存路径，则保存向量数据库和页码信息
    if save_path:
        # 确保目录存在
        os.makedirs(save_path, exist_ok=True)
        
        # 保存FAISS向量数据库
        knowledgeBase.save_local(save_path)
        print(f"向量数据库已保存到: {save_path}")
        
        # 保存页码信息到同一目录
        with open(os.path.join(save_path, "page_info.pkl"), "wb") as f:
            pickle.dump(page_info, f)
        print(f"页码信息已保存到: {os.path.join(save_path, 'page_info.pkl')}")
    
    return knowledgeBase

def load_knowledge_base(load_path: str, embeddings = None) -> FAISS:
    """
    从磁盘加载向量数据库和页码信息
    
    参数:
        load_path: 向量数据库的保存路径
        embeddings: 可选，嵌入模型。如果为None，将创建一个新的DashScopeEmbeddings实例
    
    返回:
        knowledgeBase: 加载的FAISS向量数据库对象
    """
    # 如果没有提供嵌入模型，则创建一个新的
    if embeddings is None:
        embeddings = DashScopeEmbeddings(
            model="text-embedding-v2"
        )
    
    # 加载FAISS向量数据库，添加allow_dangerous_deserialization=True参数以允许反序列化
    knowledgeBase = FAISS.load_local(load_path, embeddings, allow_dangerous_deserialization=True)
    print(f"向量数据库已从 {load_path} 加载。")
    
    # 加载页码信息
    page_info_path = os.path.join(load_path, "page_info.pkl")
    if os.path.exists(page_info_path):
        with open(page_info_path, "rb") as f:
            page_info = pickle.load(f)
        knowledgeBase.page_info = page_info
        print("页码信息已加载。")
    else:
        print("警告: 未找到页码信息文件。")
    
    return knowledgeBase
