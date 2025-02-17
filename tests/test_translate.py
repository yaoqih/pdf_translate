import os
from pathlib import Path
from pdf2zh import translate as pdf_translate
from dotenv import load_dotenv
import traceback
# 加载环境变量
load_dotenv()

def test_pdf_translation():
    """
    测试PDF翻译功能
    """
    # 测试配置
    # 设置环境变量
    os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL", "https://api.lingyiwanwu.com/v1")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "9b74841dc6f9441ca3e09e700168512e")
    os.environ["OPENAI_MODEL"] = os.getenv("OPENAI_MODEL", "yi-lightning")
    
    # 创建测试输出目录
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # 测试文件路径（请将此路径替换为实际的测试PDF文件路径）
    test_file = "2308.06721v1.pdf"
    
    if not os.path.exists(test_file):
        print(f"错误：测试文件 {test_file} 不存在")
        return
    
    try:
        print("开始测试PDF翻译...")
        print(f"使用配置：")
        
        # 调用翻译函数
        result_files = pdf_translate(
            files=[test_file],
            output=str(output_dir),
            pages=[1],  # 仅翻译第一页进行测试
            lang_in="en",
            lang_out="zh",
            service="openai",
            thread=4,
        )
        
        if result_files:
            print("\n翻译成功！")
            print("生成的文件：")
            for mono_file, dual_file in result_files:
                print(f"单语文件：{mono_file}")
                print(f"双语文件：{dual_file}")
        else:
            print("\n翻译失败：未生成输出文件")
            
    except Exception as e:
        print(f"\n翻译过程中出现错误：{str(e)}")
        traceback.print_exc()

    print("\n测试完成")

if __name__ == "__main__":
    test_pdf_translation() 