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

def extract_text_with_page_numbers(pdf) -> Tuple[str, List[int], List[Tuple[int, int]]]:
    """
    从PDF中提取文本并记录每行文本对应的页码和字符位置
    
    参数:
        pdf: PDF文件对象
    
    返回:
        text: 提取的文本内容
        page_numbers: 每行文本对应的页码列表
        line_ranges: 每行文本在原始文本中的字符位置范围列表，格式为[(start, end), ...]
    """
    text = ""
    page_numbers = []
    line_ranges = []

    for page_number, page in enumerate(pdf.pages, start=1):
        extracted_text = page.extract_text()
        if extracted_text:
            # 记录添加文本前的起始位置
            text_start_pos = len(text)
            # 添加当前页的文本
            text += extracted_text
            # 按行分割并计算每行的位置
            lines = extracted_text.split("\n")
            current_line_start = text_start_pos
            
            for i, line in enumerate(lines):
                line_start = current_line_start
                line_end = line_start + len(line)
                line_ranges.append((line_start, line_end))
                page_numbers.append(page_number)
                # 下一行的起始位置 = 当前行结束位置 + 1（换行符）
                current_line_start = line_end + 1
        else:
            logging.warning(f"No text found on page {page_number}.")

    return text, page_numbers, line_ranges

def process_text_with_splitter(text: str, page_numbers: List, line_ranges: List[Tuple[int, int]] = None, save_path: str = None) -> FAISS:
    """
    处理文本并创建向量存储
    
    参数:
        text: 提取的文本内容
        page_numbers: 每行文本对应的页码列表（可以是整数或带文件名的字符串，如"file.pdf:1"）
        line_ranges: 每行文本在原始文本中的字符位置范围列表，格式为[(start, end), ...]
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
    
    # 根据chunk在原始文本中的位置找到对应的页码
    page_info = {}
    search_start = 0  # 用于跟踪查找位置，考虑chunk overlap
    
    # 如果line_ranges可用，使用精确的位置映射
    if line_ranges and len(line_ranges) == len(page_numbers):
        for chunk in chunks:
            # 从search_start开始查找chunk（考虑overlap，向前搜索一些位置）
            search_from = max(0, search_start - 128)  # 128是chunk_overlap大小
            chunk_start = text.find(chunk, search_from)
            
            if chunk_start == -1:
                # 如果找不到，尝试全局查找
                chunk_start = text.find(chunk)
            
            if chunk_start != -1:
                # 找到包含chunk起始位置的行
                page_num = page_numbers[0] if page_numbers else ("未知:1" if page_numbers and isinstance(page_numbers[0], str) else 1)
                
                # 二分查找或线性查找包含chunk_start的行
                for line_idx, (line_start, line_end) in enumerate(line_ranges):
                    if line_start <= chunk_start <= line_end:
                        # chunk起始位置在这一行内
                        page_num = page_numbers[line_idx]
                        break
                    elif chunk_start < line_start:
                        # chunk起始位置在行之前，使用前一行（如果存在）
                        if line_idx > 0:
                            page_num = page_numbers[line_idx - 1]
                        break
                else:
                    # chunk超出所有行范围，使用最后一个页码
                    page_num = page_numbers[-1] if page_numbers else page_num
                
                # 更新search_start为当前chunk结束位置（考虑overlap）
                search_start = chunk_start + len(chunk) - 64  # 减去部分overlap
            else:
                # 如果找不到chunk位置，使用默认值
                page_num = page_numbers[-1] if page_numbers else ("未知:1" if page_numbers and isinstance(page_numbers[0], str) else 1)
            
            page_info[chunk] = page_num
    else:
        # 回退到旧方法：使用chunk索引映射（不准确，但兼容）
        for i, chunk in enumerate(chunks):
            if page_numbers and i < len(page_numbers):
                page_num = page_numbers[i]
            elif page_numbers:
                page_num = page_numbers[-1]
            else:
                page_num = "未知:1" if isinstance(page_numbers, list) and page_numbers and isinstance(page_numbers[0], str) else 1
            page_info[chunk] = page_num
    
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
