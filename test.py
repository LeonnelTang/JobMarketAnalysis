import pandas as pd

# 创建一个包含 None 和 {None, None} 的示例 DataFrame
data = {
    'city': ['上海·静安·静安寺', '上海·张江', '上海·虹口·北外滩',
             '上海·浦东·唐镇', '上海·徐汇·斜土路'],
    'location_data': [None, {'lat': 31.23, 'lng': 121.48}, {None, None}, None, {'lat': 31.19, 'lng': 121.44}]
}

df = pd.DataFrame(data)

print("原始 DataFrame:")
print(df)

# 使用 dropna 函数过滤掉包含 None 的行
df_cleaned = df.dropna(subset=['location_data'])

print("\n使用 dropna 过滤后的 DataFrame:")
print(df_cleaned)

# 使用 apply 函数来处理 location_data 列，将 {None, None} 替换为 None
df['location_data'] = df['location_data'].apply(lambda x: None if isinstance(x, set) and None in x else x)

# 使用 dropna 函数再次过滤掉包含 None 的行
df_cleaned = df.dropna(subset=['location_data'])

print("\n处理 {None, None} 并使用 dropna 过滤后的 DataFrame:")
print(df_cleaned)
