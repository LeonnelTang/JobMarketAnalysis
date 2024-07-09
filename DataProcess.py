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

    # 填充ability的缺失值
    df['ability'] = df['ability'].fillna('无要求')

    # 保存处理后的CSV文件
    processed_file_name = 'processed_' + file_name
    df.to_csv(processed_file_name, index=False)
    print(f'Processed file saved as {processed_file_name}')

# 示例文件处理
if __name__ == '__main__':
    positions = ['java','python','c++','前端开发','算法','数据挖掘','数据开发','数据分析','硬件开发','运维','产品经理']
    for position in positions:
        file_name = (position + '.csv')  # 替换为实际文件名
        process_csv(file_name)
