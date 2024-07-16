import pandas as pd

# 读取CSV文件
csv_file = 'combined_processed_data.csv'
df = pd.read_csv(csv_file)

# 保存为Excel文件
excel_file = '上海市互联网行业招聘数据集.xlsx'
df.to_excel(excel_file, index=False)
print(f"CSV文件已成功转换为Excel文件：{excel_file}")

df.to_csv('上海市互联网行业招聘数据集.csv', index=False)
print(f"CSV文件已成功转换为CSV文件：{'上海市互联网行业招聘数据集.csv'}")
