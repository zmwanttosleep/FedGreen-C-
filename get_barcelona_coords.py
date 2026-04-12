import csv
import time
from geopy.geocoders import ArcGIS

# 初始化 ArcGIS 地理编码器（无需 API Key）
geolocator = ArcGIS(timeout=30)

# 生成巴塞罗那的 42 个邮编：08001 ~ 08042
postal_codes = [f"080{i:02d}" for i in range(1, 43)]

results = []

print(f"开始查询 {len(postal_codes)} 个巴塞罗那邮编...\n")

for idx, code in enumerate(postal_codes, 1):
    print(f"[{idx}/{len(postal_codes)}] 查询 {code} ...", end=' ')
    try:
        # 查询 "08001, Barcelona, Spain"
        location = geolocator.geocode(f"{code}, Barcelona, Spain")
        if location:
            lat, lon = location.latitude, location.longitude
            print(f"✓ 坐标: ({lat:.6f}, {lon:.6f})")
            results.append({
                "original_id": 8000 + idx,  # 对应 8001..8042
                "postal_code": code,
                "latitude": lat,
                "longitude": lon
            })
        else:
            print("✗ 未找到")
    except Exception as e:
        print(f"✗ 异常: {e}")

    time.sleep(0.5)  # 避免请求过快

# 保存结果到 CSV
output_file = "barcelona_postal_coords.csv"
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["original_id", "postal_code", "latitude", "longitude"])
    writer.writeheader()
    writer.writerows(results)

print(f"\n✅ 成功获取 {len(results)} 条记录，已保存至 {output_file}")

# 打印前几行预览
if results:
    print("\n预览：")
    for r in results[:5]:
        print(f"  {r['postal_code']} -> ({r['latitude']:.6f}, {r['longitude']:.6f})")