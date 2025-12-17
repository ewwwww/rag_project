"""
知识库管理模块
负责向量数据库的初始化、增量更新等功能
"""
import os
import pickle
import shutil
from PyPDF2 import PdfReader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from data_process import (
    extract_text_with_page_numbers,
    process_text_with_splitter,
    load_knowledge_base
)


def get_processed_files(vector_store_path: str) -> set:
    """
    获取已处理的PDF文件列表
    
    参数:
        vector_store_path: 向量数据库路径
    
    返回:
        已处理文件名的集合
    """
    processed_files_path = os.path.join(vector_store_path, "processed_files.pkl")
    if os.path.exists(processed_files_path):
        with open(processed_files_path, "rb") as f:
            return pickle.load(f)
    return set()


def save_processed_files(vector_store_path: str, processed_files: set):
    """
    保存已处理的PDF文件列表
    
    参数:
        vector_store_path: 向量数据库路径
        processed_files: 已处理文件名的集合
    """
    os.makedirs(vector_store_path, exist_ok=True)
    processed_files_path = os.path.join(vector_store_path, "processed_files.pkl")
    with open(processed_files_path, "wb") as f:
        pickle.dump(processed_files, f)


def add_new_documents_to_knowledge_base(
    knowledge_base,
    new_pdf_files: list,
    dataset_path: str,
    vector_store_path: str
):
    """
    将新文档添加到现有知识库
    
    参数:
        knowledge_base: 现有的知识库对象
        new_pdf_files: 新增的PDF文件名列表
        dataset_path: 数据集目录路径
        vector_store_path: 向量数据库保存路径
    """
    print(f"\n发现 {len(new_pdf_files)} 个新PDF文件，开始增量更新...")
    
    # 创建文本分割器和嵌入模型
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " ", ""],
        chunk_size=512,
        chunk_overlap=128,
        length_function=len,
    )
    embeddings = DashScopeEmbeddings(model="text-embedding-v2")
    
    all_new_chunks = []
    all_new_page_numbers = []
    
    # 处理每个新PDF文件
    for pdf_file in new_pdf_files:
        file_path = os.path.join(dataset_path, pdf_file)
        print(f"\n正在处理新文件: {pdf_file}")
        pdf_reader = PdfReader(file_path)
        text, page_numbers = extract_text_with_page_numbers(pdf_reader)
        
        # 分割文本
        chunks = text_splitter.split_text(text)
        print(f"  - 提取了 {len(text)} 个字符，分割成 {len(chunks)} 个块")
        
        # 为每个chunk找到对应的页码
        # 使用与 process_text_with_splitter 相同的逻辑
        for i, chunk in enumerate(chunks):
            all_new_chunks.append(chunk)
            # 使用索引对应的页码（与原始实现保持一致）
            if page_numbers and i < len(page_numbers):
                page_num = page_numbers[i]
            elif page_numbers:
                # 如果索引超出范围，使用最后一个页码
                page_num = page_numbers[-1]
            else:
                page_num = 1
            all_new_page_numbers.append(f"{pdf_file}:{page_num}")
    
    if not all_new_chunks:
        print("没有新的文本块需要添加")
        return
    
    print(f"\n准备添加 {len(all_new_chunks)} 个新文本块到向量数据库...")
    
    # 添加到现有知识库
    knowledge_base.add_texts(all_new_chunks, embeddings=embeddings)
    
    # 更新页码信息
    for i, chunk in enumerate(all_new_chunks):
        knowledge_base.page_info[chunk] = all_new_page_numbers[i]
    
    print(f"✅ 成功添加 {len(all_new_chunks)} 个新文本块")
    
    # 保存更新后的向量数据库和页码信息
    knowledge_base.save_local(vector_store_path)
    with open(os.path.join(vector_store_path, "page_info.pkl"), "wb") as f:
        pickle.dump(knowledge_base.page_info, f)
    
    print("✅ 向量数据库已更新并保存")


def initialize_knowledge_base(dataset_path: str, vector_store_path: str, force_rebuild: bool = False):
    """
    初始化知识库（向量数据库），支持增量更新
    
    参数:
        dataset_path: 数据集目录路径（会处理目录下所有PDF文件）
        vector_store_path: 向量数据库保存路径
        force_rebuild: 是否强制重新构建（忽略已处理的文件）
    
    返回:
        knowledge_base: FAISS向量数据库对象
    """
    # 检查目录是否存在
    if not os.path.isdir(dataset_path):
        raise FileNotFoundError(f"数据集目录不存在: {dataset_path}")
    
    # 获取目录下的所有PDF文件
    all_pdf_files = [f for f in os.listdir(dataset_path) if f.lower().endswith('.pdf')]
    if not all_pdf_files:
        raise FileNotFoundError(f"目录 {dataset_path} 中没有找到PDF文件")
    
    # 检查向量数据库是否已存在
    db_exists = os.path.exists(vector_store_path) and os.path.exists(os.path.join(vector_store_path, 'index.faiss'))
    
    if db_exists and not force_rebuild:
        print("检测到已存在的向量数据库，检查是否有新文件...")
        knowledge_base = load_knowledge_base(vector_store_path)
        
        # 获取已处理的文件列表
        processed_files = get_processed_files(vector_store_path)
        
        # 找出新增的文件
        new_pdf_files = [f for f in all_pdf_files if f not in processed_files]
        
        if new_pdf_files:
            # 增量更新：添加新文件
            add_new_documents_to_knowledge_base(
                knowledge_base, new_pdf_files, dataset_path, vector_store_path
            )
            # 更新已处理文件列表
            processed_files.update(new_pdf_files)
            save_processed_files(vector_store_path, processed_files)
        else:
            print("✅ 所有PDF文件已处理，无需更新")
    else:
        # 首次构建或强制重建
        if force_rebuild and db_exists:
            print("强制重建：删除旧的向量数据库...")
            shutil.rmtree(vector_store_path)
        
        print("开始处理PDF文件并创建向量数据库...")
        
        all_text = ""
        all_page_numbers = []
        
        for pdf_file in all_pdf_files:
            file_path = os.path.join(dataset_path, pdf_file)
            print(f"\n正在处理: {pdf_file}")
            pdf_reader = PdfReader(file_path)
            text, page_numbers = extract_text_with_page_numbers(pdf_reader)
            all_text += f"\n\n[文档: {pdf_file}]\n\n" + text
            all_page_numbers.extend([f"{pdf_file}:{p}" for p in page_numbers])
            print(f"  - 提取了 {len(text)} 个字符")
        
        print(f"\n总共提取文本，共 {len(all_text)} 个字符。")
        
        # 处理所有文本并创建向量存储
        knowledge_base = process_text_with_splitter(
            text=all_text,
            page_numbers=all_page_numbers,
            save_path=vector_store_path
        )
        
        # 保存已处理文件列表
        save_processed_files(vector_store_path, set(all_pdf_files))
    
    print("\n向量数据库准备完成！")
    return knowledge_base

