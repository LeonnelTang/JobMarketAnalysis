import glob
import os

import pandas as pd


def process_csv(file_name):

    df = pd.read_csv(file_name)

    # 将空格或空字符串视为缺失值
    df['specific_position'] = df['specific_position'].replace(r'^\s*$', None, regex=True)
    df['company_name'] = df['company_name'].replace(r'^\s*$', None, regex=True)
    df['ability'] = df['ability'].replace(r'^\s*$', None, regex=True)

    # 填充specific_position的缺失值
    df['specific_position'] = df['specific_position'].fillna(df['position'])

    # 填充company_name的缺失值
    df['company_name'] = df['company_name'].fillna('其他')

    # 删除为实习薪资或面议的行
    patterns = [r'\d+-\d+/天', r'\d+元/时', r'面议']
    for pattern in patterns:
        df = df[~df['salary'].str.contains(pattern, na=False)]

    # 处理salary字段，转换为数字并计算年薪范围
    def parse_salary(salary_str):
        if pd.isna(salary_str):
            return (None, None)

        # 移除多余字符
        salary_str = salary_str.replace('·', ' ')

        # 处理有额外月数的情况，如"1.5万-3万·15薪"
        total_months = 12
        if ' ' in salary_str:
            salary_parts = salary_str.split()
            salary_str = salary_parts[0]
            total_months = int(salary_parts[1].replace('薪', ''))

        # 解析薪资范围
        if '-' in salary_str:
            parts = salary_str.split('-')
            min_salary_str = parts[0]
            max_salary_str = parts[1]

            def convert_to_annual(salary):
                if '万' in salary:
                    return float(salary.replace('万', '')) * 10000 * total_months
                elif '千' in salary:
                    return float(salary.replace('千', '')) * 1000 * total_months
                elif '元/月' in salary:
                    return float(salary.replace('元/月', '')) * 12
                else:
                    return float(salary) * 12  # 默认月薪

            min_salary = convert_to_annual(min_salary_str)
            max_salary = convert_to_annual(max_salary_str)

            return (min_salary, max_salary)

        return (None, None)

    df[['min_annual_salary', 'max_annual_salary']] = df['salary'].apply(parse_salary).apply(pd.Series)

    # 删除原来的salary列
    df.drop(columns=['salary'], inplace=True)

    # 填充ability的缺失值
    df['ability'] = df['ability'].fillna('无要求')

    # 检查company_size不符合预定模式的情况，并用company_type的值填充
    size_pattern = r'^\d+-\d+人$|^\d+人以上$|^\d+人以下$'
    invalid_size_mask = ~df['company_size'].str.match(size_pattern, na=False)
    df.loc[invalid_size_mask, 'company_size'] = df['company_type']
    df.loc[invalid_size_mask, 'company_type'] = None

    # 处理company_size字段，转换为数值范围
    def parse_company_size(size_str):
        if pd.isna(size_str):
            return (None, None)

        if '-' in size_str:
            parts = size_str.split('-')
            min_size = int(parts[0].replace('人', ''))
            max_size = int(parts[1].replace('人', ''))
            return (min_size, max_size)
        elif '以上' in size_str:
            min_size = int(size_str.replace('人以上', ''))
            return (min_size, None)
        elif '以下' in size_str:
            max_size = int(size_str.replace('人以下', ''))
            return (None, max_size)

        return (None, None)

    # 应用parse_company_size函数，并将结果展开为两列
    df[['min_company_size', 'max_company_size']] = df['company_size'].apply(parse_company_size).apply(pd.Series)

    # 删除原来的company_size列
    df.drop(columns=['company_size'], inplace=True)

    # 生成新的文件名并保存
    base_name = os.path.basename(file_name)  # 获取文件名部分
    new_file_name = 'processed_' + base_name  # 构建新的文件名
    processed_file_name = os.path.join('processedCsv', new_file_name)  # 构建新的文件路径

    df.to_csv(processed_file_name, index=False)
    print(f'Processed file saved as {processed_file_name}')

# 示例文件处理
if __name__ == '__main__':
    positions = ['java','python','c++','前端开发','算法','数据挖掘','数据开发','数据分析','硬件开发','运维','产品经理']
    for file_name in glob.glob(os.path.join('originCsv', '*.csv')):
        process_csv(file_name)

