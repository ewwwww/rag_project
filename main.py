"""
RAG 系统主入口文件
"""
import os
import argparse
from knowledge_base_manager import initialize_knowledge_base
from user_query import run_query_mode


def main():
    """主函数：RAG 系统的入口点"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="RAG 系统：文档检索与智能问答",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
     使用示例:
     # 初始化知识库（首次运行或增量更新）
     python main.py --init
     
     # 强制重新构建向量数据库
     python main.py --init --force
     
     # 执行查询
     python main.py --query "客户经理的考核标准是什么？"
     
     # 连续交互式查询模式（退出：quit/exit/退出）
     python main.py --interactive
        """
    )
    
    parser.add_argument(
        "--init",
        action="store_true",
        help="初始化知识库（处理PDF并创建向量数据库，支持增量更新）"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制重新构建向量数据库（忽略已处理的文件）"
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
        "--dataset",
        type=str,
        default="./dataset",
        help="数据集目录路径（默认：./dataset，会处理目录下所有PDF文件）"
    )
    parser.add_argument(
        "--vector-store",
        type=str,
        default="./vector_store",
        help="向量数据库保存路径（默认：./vector_store）"
    )
    
    args = parser.parse_args()
    
    # 配置参数
    dataset_path = args.dataset
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
            knowledge_base = initialize_knowledge_base(dataset_path, vector_store_path, force_rebuild=args.force)
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

