"""
RAG 系统主入口文件
"""
import os
import argparse
from PyPDF2 import PdfReader
from data_process import (
    extract_text_with_page_numbers,
    process_text_with_splitter,
    load_knowledge_base
)
from user_query import user_query


def initialize_knowledge_base(pdf_path: str, vector_store_path: str):
    """
    初始化知识库（向量数据库）
    
    参数:
        pdf_path: PDF文件路径
        vector_store_path: 向量数据库保存路径
    
    返回:
        knowledge_base: FAISS向量数据库对象
    """
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
    return knowledge_base


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
        user_query(query)
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ 查询处理失败：{e}")
        return False


def main():
    """主函数：RAG 系统的入口点"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="RAG 系统：文档检索与智能问答",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    使用示例:
    # 初始化知识库
    python main.py --init
    
    # 执行查询
    python main.py --query "客户经理的考核标准是什么？"
    
    # 交互式查询模式
    python main.py --interactive
        """
    )
    
    parser.add_argument(
        "--init",
        action="store_true",
        help="初始化知识库（处理PDF并创建向量数据库）"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="要查询的问题"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="进入交互式查询模式"
    )
    parser.add_argument(
        "--pdf-path",
        type=str,
        default="./dataset/浦发上海浦东发展银行西安分行个金客户经理考核办法.pdf",
        help="PDF文件路径（默认：./dataset/浦发上海浦东发展银行西安分行个金客户经理考核办法.pdf）"
    )
    parser.add_argument(
        "--vector-store",
        type=str,
        default="./vector_store",
        help="向量数据库保存路径（默认：./vector_store）"
    )
    
    args = parser.parse_args()
    
    # 配置参数
    pdf_path = args.pdf_path
    vector_store_path = args.vector_store
    
    # 如果没有指定任何操作，默认初始化知识库
    if not args.init and not args.query and not args.interactive:
        args.init = True
    
    try:
        # 初始化知识库（如果需要）
        if args.init:
            print("=" * 50)
            print("初始化知识库...")
            print("=" * 50)
            knowledge_base = initialize_knowledge_base(pdf_path, vector_store_path)
            if knowledge_base is None:
                print("❌ 知识库初始化失败")
                return None
            print("✅ 知识库初始化完成")
        
        # 执行单次查询
        if args.query:
            success = run_query_mode(args.query, vector_store_path)
            return success
        
        # 交互式查询模式
        if args.interactive:
            print("\n" + "=" * 50)
            print("进入交互式查询模式")
            print("输入 'quit' 或 'exit' 退出")
            print("=" * 50)
            
            while True:
                try:
                    query = input("\n请输入您的问题: ").strip()
                    
                    if not query:
                        continue
                    
                    if query.lower() in ['quit', 'exit', '退出']:
                        print("\n感谢使用，再见！")
                        break
                    
                    run_query_mode(query, vector_store_path)
                    
                except KeyboardInterrupt:
                    print("\n\n程序被用户中断")
                    break
                except Exception as e:
                    print(f"❌ 发生错误：{e}")
            
            return True
        
        # 如果只是初始化，返回知识库对象
        return knowledge_base
        
    except FileNotFoundError as e:
        print(f"❌ 错误：文件未找到 - {e}")
        return None
    except Exception as e:
        print(f"❌ 错误：{e}")
        return None


if __name__ == "__main__":
    main()

