import requests
import re
from copyheaders import headers_raw_to_dict
from bs4 import BeautifulSoup
import pandas as pd


# 根据url和参数获取网页的HTML：

def get_html(url, params):

    my_headers = b'''
    Accept:application/json, text/plain, */*
    Accept-Encoding:gzip, deflate, br, zstd
    Accept-Language:zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7
    Cookie:x-zp-client-id=c34039c9-1b7f-407f-9213-0d54bdb32778; sajssdk_2015_cross_new_user=1; locationInfo_search={%22code%22:%22538%22%2C%22name%22:%22%E4%B8%8A%E6%B5%B7%22%2C%22message%22:%22%E5%8C%B9%E9%85%8D%E5%88%B0%E5%B8%82%E7%BA%A7%E7%BC%96%E7%A0%81%22}; Hm_lvt_7fa4effa4233f03d11c7e2c710749600=1720360410; HMACCOUNT=569521891F06760E; LastCity=%E4%B8%8A%E6%B5%B7; LastCity%5Fid=538; selectCity_search=538; zp_passport_deepknow_sessionId=b89b16a6sa5e3c4c008b68771ec6274d59e6; at=ddcc1c26332a4055b9eb50f79d3bcbb6; rt=fe7e27612fb3447fbc6677085546ad8e; ZL_REPORT_GLOBAL={%22//www%22:{%22seid%22:%22%22%2C%22actionid%22:%22cab556dd-b9b4-43e3-98d2-c011d1be873c-cityPage%22}%2C%22jobs%22:{%22recommandActionidShare%22:%22f4433c4a-6062-49ab-9560-a8313c118acf-job%22}}; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; Hm_lpvt_7fa4effa4233f03d11c7e2c710749600=1720361177; acw_tc=276077b917203627580211685e1d598db95c2266148f5583197b309820fcb5; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221187602446%22%2C%22first_id%22%3A%221908d7844187b5-0ce4f5d0f19a298-4c657b58-1821369-1908d784419b92%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkwOGQ3ODQ0MTg3YjUtMGNlNGY1ZDBmMTlhMjk4LTRjNjU3YjU4LTE4MjEzNjktMTkwOGQ3ODQ0MTliOTIiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIxMTg3NjAyNDQ2In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221187602446%22%7D%2C%22%24device_id%22%3A%221908d7844187b5-0ce4f5d0f19a298-4c657b58-1821369-1908d784419b92%22%7D
    Origin:https://sou.zhaopin.com
    Priority:u=1, i
    Referer:https://sou.zhaopin.com/
    Sec-Ch-Ua:"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"
    Sec-Ch-Ua-Mobile:?0
    Sec-Ch-Ua-Platform:"Windows"
    Sec-Fetch-Dest:empty
    Sec-Fetch-Mode:cors
    Sec-Fetch-Site:same-site
    User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0
    X-Zp-Page-Code:4019    '''     # b：将字符串转换为二进制； 三引号：为输入多行字符串，即包含\n的字符串
    my_headers = headers_raw_to_dict(my_headers)  # 把复制的浏览器需求头转化为字典形式
    req = requests.get(url, headers=my_headers, params=params)
    req.encoding = req.apparent_encoding
    html = req.text

    return html


# 输入url和城市编号，获取由所有职位信息的html标签的字符串组成的列表：

def get_html_list(url, position):

    html_list = list()

    for i in range(1, 20):
        params = {'jl': '538', 'kw': position, 'p': str(i)}
        html = get_html(url, params)

        """
        test
        
        with open("D:\python\python_project\Job\job\soupExample.html", 'r', encoding='utf-8') as file:
            html_content = file.read()
        """

        soup = BeautifulSoup(html, 'html.parser')
        jobs = soup.find_all(name='div', attrs={'class': 'joblist-box__iteminfo'})     # 参数：名称，属性（化成字典）
        html_list += jobs

    for i in range(len(html_list)):     # soup.find_all()得到的列表元素是特殊类型
        html_list[i] = str(html_list[i])

    return html_list


# 根据上面的HTML标签列表，把每个职位信息的有效数据提取出来，保存csv文件：

def get_csv(html_list):
    city, specific_position, company_name, company_size, company_type, salary, education, ability, experience = ([] for i in range(9))

    for i in html_list:
        # 提取职位名称
        if re.search(r'<a[^>]*class="jobinfo__name"[^>]*>(.*?)</a>', i):
            s = re.search(r'<a[^>]*class="jobinfo__name"[^>]*>(.*?)</a>', i).group(1)
            specific_position.append(s)
        else:
            specific_position.append(' ')

        # 提取薪资
        if re.search(r'<p class="jobinfo__salary">\s*(.*?)\s*</p>', i):
            s = re.search(r'<p class="jobinfo__salary">\s*(.*?)\s*</p>', i).group(1).strip()
            salary.append(s)
        else:
            salary.append(' ')

        # 提取公司名称
        if re.search(r'<a class="companyinfo__name"[^>]*title="(.*?)"', i):
            s = re.search(r'<a class="companyinfo__name"[^>]*title="(.*?)"', i).group(1)
            company_name.append(s)
        else:
            company_name.append(' ')

        # 提取公司类型和规模，丢弃不需要的信息
        company_info_match = re.findall(
            r'<div class="companyinfo__tag">.*?<div class="joblist-box__item-tag">\s*(.*?)\s*</div>.*?<div class="joblist-box__item-tag">\s*(.*?)\s*</div>',
            i, re.DOTALL)
        if company_info_match:
            company_type.append(company_info_match[0][0])  # 提取公司类型
            company_size.append(company_info_match[0][1])  # 提取公司规模
        else:
            company_type.append(' ')
            company_size.append(' ')

        #提取工作地点
        if re.search(r'<div class="jobinfo__other-info-item">.*?<span>(.*?)</span></div>', i):
            s = re.search(r'<div class="jobinfo__other-info-item">.*?<span>(.*?)</span></div>', i).group(1)
            city.append(s)
        else:
            city.append(' ')

        # 提取工作地点、经验和学历要求
        other_info_match = re.findall(r'<div class="jobinfo__other-info-item">\s*(.*?)\s*</div>', i)
        if other_info_match:
            if len(other_info_match) >= 2:
                experience.append(other_info_match[1].strip())
                education.append(other_info_match[2].strip())
            else:
                experience.append(' ')
                education.append(' ')
        else:
            experience.append(' ')
            education.append(' ')

        # 提取能力要求，确保不包括公司信息
        abilities_section_match = re.findall(r'<div class="jobinfo__tag">(.*?)<span class="jobinfo__hit-words">', i, re.DOTALL)
        if abilities_section_match:
            abilities = []
            for section in abilities_section_match:
                abilities_match = re.findall(r'<div class="joblist-box__item-tag">\s*(.*?)\s*</div>', section)
                abilities.extend(abilities_match)
            ability.append(' '.join(abilities))
        else:
            ability.append(' ')



    table = list(zip(city, specific_position, company_name, company_size, company_type, salary, education, ability, experience))
    df = pd.DataFrame(table, columns=['city', 'specific_position', 'company_name', 'company_size', 'company_type', 'salary', 'education', 'ability', 'experience'])
    return df



if __name__ == '__main__':

    url = 'https://sou.zhaopin.com/'
    positions = ['java','python','c++','前端开发','算法','数据挖掘','数据开发','数据分析','硬件开发','运维','产品经理']
    for i in positions:
        html_list = get_html_list(url, i)
        df0 = get_csv(html_list)
        position = [i]*(df0.shape[0])
        df_position = pd.DataFrame(position, columns=['position'])
        df = pd.concat([df_position, df0], axis=1)
        file_name = i + '.csv'
        df.to_csv(file_name)


