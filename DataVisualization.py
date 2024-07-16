import glob
import json
import os

import pandas as pd
import matplotlib.pyplot as plt
import requests
import seaborn as sns
from folium import folium
from folium.plugins import HeatMap
from geopy.extra.rate_limiter import RateLimiter
from matplotlib.font_manager import FontProperties
from wordcloud import WordCloud

# 读取所有CSV文件并合并
file_paths = glob.glob('processedCsv/*.csv')
df_list = [pd.read_csv(file) for file in file_paths]
combined_df = pd.concat(df_list, ignore_index=True)
combined_df.to_csv('combined_processed_data.csv', index=False)
df = pd.DataFrame(combined_df['city'])

# 设置字体
font_path = r'SimHei.ttf'  # 替换为实际字体路径
font_prop = FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False


# 定义各个分析函数


# 地区分布分析
def city_distribution():

    # 提取具体区和街道的信息（假设格式固定为：城市·区·街道）
    df['district'] = df['city'].apply(lambda x: x.split('·')[1] if '·' in x else x)
    df['location'] = df['city'].apply(lambda x: x.replace('·', ' '))

    # 缓存文件路径
    cache_file = 'location_cache.json'

    # 读取缓存
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as file:
            location_cache = json.load(file)
    else:
        location_cache = {}

    # 使用 百度地图api 将地址转换为经纬度
    def get_lng_lat(address):
        if address in location_cache:
            return location_cache[address]

        # 接口地址
        base_url = "https://api.map.baidu.com/geocoding/v3"
        # 百度地图apikey
        ak = "GSjqjV1GE2IJwwp5yolugPIw3M50r9tk"

        # 构建请求参数
        params = {
            "ak": ak,
            "output": "json",
            "address": address,
        }

        # 发送GET请求并获取响应
        response = requests.get(base_url, params=params, verify=False)
        data = response.json()

        if data['status'] == 0:
            location_cache[address] = data['result']['location']
            with open(cache_file, 'w', encoding='utf-8') as file:
                json.dump(location_cache, file, ensure_ascii=False, indent=4)
            return data['result']['location']
        else:
            return None

    geocoding = RateLimiter(get_lng_lat, min_delay_seconds=0.1)

    df['location_data'] = df['location'].apply(geocoding)

    # 过滤掉没有找到经纬度的地址
    df.dropna(subset=['location_data'], inplace=True)

    df['latitude'] = df['location_data'].apply(lambda loc: loc['lat'] if loc else None)
    df['longitude'] = df['location_data'].apply(lambda loc: loc['lng'] if loc else None)

    # 过滤掉没有成功解析经纬度的地址
    df.dropna(subset=['latitude', 'longitude'], inplace=True)

    # 创建地图中心点
    map_center = [31.2304, 121.4737]  # 上海市中心点

    # 创建 Folium 地图
    m = folium.Map(location=map_center, zoom_start=12)

    # 创建热力图数据
    heat_data = [[row['latitude'], row['longitude']] for index, row in df.iterrows()]

    # 添加热力图
    HeatMap(heat_data).add_to(m)

    # 添加标题
    title_html = '''
               <h3 align="center" style="font-size:20px"><b>上海市互联网职位数量分布热力图</b></h3>
               '''
    m.get_root().html.add_child(folium.Element(title_html))

    # 保存并显示地图
    m.save("VisualizedData/shanghai_heatmap.html")
    m.show_in_browser()


# 总体薪资分析
def general_salary_distribution():
    # 转换薪资为万单位，并计算平均年薪
    df['min_annual_salary'] = combined_df['min_annual_salary'] / 10000
    df['max_annual_salary'] = combined_df['max_annual_salary'] / 10000
    df['average_annual_salary'] = (df['min_annual_salary'] + df['max_annual_salary']) / 2

    # 绘制薪资分布的直方图和核密度估计图
    salarys = df['average_annual_salary']
    mean = round(salarys.mean(), 1)
    plt.figure(figsize=(8, 6), dpi=200)
    sns.distplot(salarys, hist=True, kde=True, kde_kws={"color": "r", "linewidth": 1.5, 'linestyle': '-'})
    plt.axvline(mean, color='r', linestyle=":")
    plt.text(mean, 0.04, '平均年薪: %.1f万' % (mean), color='k', horizontalalignment='center', fontsize=15)
    plt.xlim(0, 60)
    plt.xlabel('年薪（单位：万）')
    plt.title('互联网行业的薪资分布', fontsize=20)
    plt.savefig('VisualizedData/互联网行业的薪资分布.jpg')
    plt.show()


# 薪资分布分析
def salary_distribution():

    df['position'] = combined_df['position']

    salarys = []
    positions = list(set(list(df['position'])))  # 将职位列单独拉出来、去重、转化列表
    for i in positions:
        t = df.loc[df['position'] == i, 'average_annual_salary']
        salarys.append(round(t.mean(), 1))

    data = pd.DataFrame(list(zip(positions, salarys)), columns=['positions', 'salarys'])
    data = data.sort_values('salarys', ascending=False)
    fig = plt.figure(figsize=[8, 6], dpi=200)
    ax = fig.add_subplot()
    ax.bar(data['positions'], data['salarys'], alpha=0.8, color='dodgerblue')
    for i in zip(data['positions'], data['salarys'], data['salarys']):
        ax.text(i[0], i[1], i[2], horizontalalignment='center')
    ax.set_ylim(8, max(data['salarys']) * 1.1)
    ax.set_title('互联网热门职位的平均月薪（单位：万）', fontsize=20)
    plt.savefig('VisualizedData/互联网热门职位的平均年薪.jpg')
    plt.show()


# 学历要求分析
def education_distribution():
    # 合并 "其他" 部分
    df['education'] = combined_df['education'].apply(
        lambda x: x if x in ['本科', '大专', '硕士', '学历不限'] else '其他'
    )
    education_counts = df['education'].value_counts()

    plt.figure(figsize=(10, 6))
    wedges, texts, autotexts = plt.pie(
        education_counts.values,
        labels=education_counts.index,
        autopct='%1.1f%%',
        startangle=140,
        pctdistance=0.85,
        labeldistance=1.1,
    )

    # 调整百分比标签的大小
    for autotext in autotexts:
        autotext.set_fontproperties(font_prop)
        autotext.set_size(20)

    # 调整标签的大小
    for text in texts:
        text.set_fontproperties(font_prop)
        text.set_size(10)

    plt.title('学历要求分布', fontproperties=font_prop, fontsize=20)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # 添加图例，位置靠近中间
    plt.legend(wedges, education_counts.index, title='学历', loc='center left', bbox_to_anchor=(0.8, 0.5),
               prop=font_prop)

    plt.savefig('VisualizedData/学历要求分布.jpg')
    plt.show()


# 工作经验要求分析
def experience_distribution():
    # 合并 "其他" 部分
    df['experience'] = combined_df['experience'].apply(
        lambda x: '其他' if x in ['无经验', '1年以下', '10年以上'] else x
    )

    experience_counts = df['experience'].value_counts()

    # 设置explode参数，使占比极小的部分突出
    explode = [0.5 if count < 70 else 0 for count in experience_counts.values]

    plt.figure(figsize=(10, 6))
    wedges, texts, autotexts = plt.pie(
        experience_counts.values,
        labels=experience_counts.index,
        autopct='%1.1f%%',
        startangle=140,
        pctdistance=0.85,
        labeldistance=1.1,
        explode=explode,
    )

    # 调整百分比标签的大小
    for autotext in autotexts:
        autotext.set_fontproperties(font_prop)
        autotext.set_size(20)

    # 调整标签的大小
    for text in texts:
        text.set_fontproperties(font_prop)
        text.set_size(20)

    plt.title('工作经验要求分布', fontproperties=font_prop, fontsize=20)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # 添加图例，位置靠近中间
    plt.legend(wedges, experience_counts.index, title='工作经验', loc='center left', bbox_to_anchor=(0.8, 0.5),
               prop=font_prop)

    plt.savefig('VisualizedData/工作经验要求分布.jpg')
    plt.show()


# 技能需求分析
def skill_distribution():

    # 生成词云图的函数
    def generate_wordcloud(specific_position):
        ability = combined_df.loc[combined_df['position'] == specific_position, 'ability']
        ability_list = list(ability)
        filtered_ability_list = [str(item) for item in ability_list if str(item) != '无要求']
        words = ' '.join(filtered_ability_list)

        if not words.strip():
            print(f"{specific_position} 职位无技能要求数据可生成词云图。")
            return

        # 生成词云
        cloud = WordCloud(
            font_path=font_path,  # 设置字体文件路径
            background_color='white',  # 设置背景颜色，默认是黑色
            max_words=100,  # 词云显示的最大词语数量
            random_state=3,  # 设置随机生成状态，即多少种配色方案
            collocations=False,  # 是否包括词语之间的搭配，默认True，可能会产生语意重复的词语
            width=1200, height=900  # 设置大小，默认图片比较小，模糊
        ).generate(words)

        # 绘制词云
        plt.figure(figsize=(8, 6), dpi=200)
        plt.imshow(cloud)  # 在figure对象上绘制词云图
        plt.gcf().suptitle(f'{specific_position} 职位的技能要求关键词频统计', fontsize=30, fontproperties=font_prop)
        plt.axis('off')  # 设置词云图中无坐标轴
        plt.savefig(f"VisualizedData/{specific_position}职位的技能要求关键词频统计.jpg")
        plt.show()

    # 职位列表
    positions = combined_df['position'].unique()

    # 生成每个职位的词云图
    for position in positions:
        generate_wordcloud(position)


# 执行分析函数
if __name__ == '__main__':
    city_distribution()
    general_salary_distribution()
    salary_distribution()
    education_distribution()
    experience_distribution()
    skill_distribution()
