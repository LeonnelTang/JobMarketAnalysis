import requests
import json
import geopandas as gpd
import matplotlib.pyplot as plt

# 百度地图API密钥
ak = "GSjqjV1GE2IJwwp5yolugPIw3M50r9tk"
url = "https://api.map.baidu.com/staticimage/v2"

def get_boundary_data(city):
    params = {
        "width": "280",
        "height": "140",
        "zoom": "10",
        "ak": ak,
    }

    response = requests.get(url=url, params=params,)
    data = response.json()

    if data['status'] == 0 and data['results']:
        city_data = data['results'][0]
        city_name = city_data['name']
        location = city_data['location']
        lat, lng = location['lat'], location['lng']

        # 获取边界数据
        boundary_url = f"http://api.map.baidu.com/place/v2/detail?uid={city_data['uid']}&output=json&ak={api_key}"
        boundary_response = requests.get(boundary_url)
        boundary_data = boundary_response.json()

        if boundary_data['status'] == 0 and boundary_data['result']:
            boundary_info = boundary_data['result']
            return boundary_info
    return None


# 获取上海市边界数据
city = "上海市"
boundary_info = get_boundary_data(city)

# 保存为GeoJSON文件
if boundary_info:
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [point['lng'], point['lat']] for point in boundary_info['geo']
                    ]]
                },
                "properties": {
                    "name": city
                }
            }
        ]
    }

    with open('shanghai_boundary.geojson', 'w') as f:
        json.dump(geojson_data, f)

    # 使用GeoPandas加载并绘制GeoJSON数据
    gdf = gpd.read_file('shanghai_boundary.geojson')

    # 绘制地图
    fig, ax = plt.subplots(figsize=(15, 10))
    gdf.plot(ax=ax, color='lightgrey')

    plt.title(f'{city}边界', fontsize=16)
    plt.xlabel('经度', fontsize=14)
    plt.ylabel('纬度', fontsize=14)
    plt.show()
else:
    print("无法获取边界数据")
