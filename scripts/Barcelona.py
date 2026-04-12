import csv
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


def main():
    # 初始化地理编码器
    # 务必替换 user_agent 中的邮箱为你的真实邮箱，否则可能被拒绝
    geolocator = Nominatim(user_agent="postal_geocoder (your-email@example.com)", timeout=10)

    # 使用 RateLimiter 控制请求频率（每秒最多 1 次）
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.0)

    results = []
    start_code = 8001
    end_code = 8042

    for code in range(start_code, end_code + 1):
        postal = f"0{code}" if code < 10000 else str(code)
        print(f"正在查询邮政编码 {postal} ...")

        try:
            # 构造查询字符串
            query = f"{postal} Barcelona, Spain"
            location = geocode(query)

            if location:
                lat = location.latitude
                lon = location.longitude
                address = location.address
                print(f"  -> 成功: ({lat}, {lon})")
            else:
                lat = lon = None
                address = None
                print(f"  -> 未找到该邮政编码")
        except Exception as e:
            print(f"  -> 出错: {e}")
            lat = lon = address = None

        results.append({
            "postal_code": postal,
            "latitude": lat,
            "longitude": lon,
            "display_name": address
        })

        # 额外睡眠确保速率限制（RateLimiter 已处理，但再留一点缓冲）
        time.sleep(0.1)

    # 保存到 CSV
    with open("barcelona_postal_codes.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["postal_code", "latitude", "longitude", "display_name"])
        writer.writeheader()
        writer.writerows(results)

    success = sum(1 for r in results if r["latitude"] is not None)
    print(f"\n完成！成功获取 {success} / {len(results)} 个邮政编码的坐标。")
    print("结果已保存到 barcelona_postal_codes.csv")


if __name__ == "__main__":
    main()