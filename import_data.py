import pandas as pd
import os
import sys

def import_data(file_path):
    """
    导入新数据到项目中
    
    Args:
        file_path: 本地数据文件路径（支持CSV或Excel格式）
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    # 获取文件扩展名
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # 读取数据
    print(f"正在读取数据文件: {file_path}")
    try:
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            print(f"❌ 不支持的文件格式: {file_ext}")
            return False
        
        print(f"✅ 数据读取成功！")
        print(f"数据行数：{len(df)}，列数：{len(df.columns)}")
        print(f"列名：{list(df.columns)}")
        
        # 显示前5行数据预览
        print("\n前5行数据预览：")
        print(df.head())
        
        # 保存数据到 data/raw 目录
        save_dir = r"E:\PythonProgram\FedGreen-C\data\raw"
        os.makedirs(save_dir, exist_ok=True)
        
        # 生成保存文件名
        file_name = os.path.basename(file_path)
        save_path = os.path.join(save_dir, file_name)
        
        # 保存数据
        if file_ext == '.csv':
            # 保存为Excel格式，与现有数据格式一致
            excel_path = os.path.join(save_dir, os.path.splitext(file_name)[0] + '.xlsx')
            df.to_excel(excel_path, index=False)
            print(f"✅ 数据已保存至：{excel_path}")
        else:
            # 直接保存Excel文件
            df.to_excel(save_path, index=False)
            print(f"✅ 数据已保存至：{save_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据处理失败：{e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python import_data.py <数据文件路径>")
        print("支持的格式: CSV, Excel (.xlsx, .xls)")
        sys.exit(1)
    
    file_path = sys.argv[1]
    import_data(file_path)
