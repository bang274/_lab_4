from langchain_core.tools import tool

# ==============================================================================
# MOCK DATA – Dữ liệu giả lập hệ thống du lịch
# Lưu ý: Giá cả có logic (VD: cuối tuần đắt hơn, hạng cao hơn đắt hơn)
# Sinh viên cần đọc hiểu dữ liệu để debug test cases.
# ==============================================================================

FLIGHTS_DB = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1_450_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2_800_000, "class": "business"},
        {"airline": "VietJet Air", "departure": "08:30", "arrival": "09:50", "price": 890_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "11:00", "arrival": "12:20", "price": 1_200_000, "class": "economy"},
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "10:00", "arrival": "12:15", "price": 1_350_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "16:00", "arrival": "18:15", "price": 1_100_000, "class": "economy"},
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "08:10", "price": 1_600_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "07:30", "arrival": "09:40", "price": 950_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "12:00", "arrival": "14:10", "price": 1_300_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "18:00", "arrival": "20:10", "price": 3_200_000, "class": "business"},
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1_300_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "13:00", "arrival": "14:20", "price": 780_000, "class": "economy"},
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "15:00", "arrival": "16:00", "price": 650_000, "class": "economy"},
    ]
}

HOTELS_DB = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury", "stars": 5, "price_per_night": 1_800_000, "area": "Mỹ Khê", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1_200_000, "area": "Mỹ Khê", "rating": 4.3},
        {"name": "Fivitel Danang", "stars": 3, "price_per_night": 650_000, "area": "Sơn Trà", "rating": 4.1},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250_000, "area": "Hải Châu", "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350_000, "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3_500_000, "area": "Bãi Dài", "rating": 4.4},
        {"name": "Sol by Meliá", "stars": 4, "price_per_night": 1_500_000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800_000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200_000, "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel", "stars": 5, "price_per_night": 2_800_000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central", "stars": 4, "price_per_night": 1_400_000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel", "stars": 3, "price_per_night": 550_000, "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room", "stars": 2, "price_per_night": 180_000, "area": "Quận 1", "rating": 4.6},
    ]
}

def format_currency(amount: int) -> str:
    return f"{amount:,.0f}".replace(",", ".") + "đ"

@tool
def search_flights(origin: str, destination: str) -> str:
    """
    Tìm kiếm các chuyến bay giữa hai thành phố.
    Tham số:
    - origin: thành phố khởi hành (VD: 'Hà Nội', 'Hồ Chí Minh')
    - destination: thành phố đến (VD: 'Đà Nẵng', 'Phú Quốc')
    Trả về danh sách chuyến bay với hãng, giờ bay, giá vé.
    Nếu không tìm thấy tuyến bay, trả về thông báo không có chuyến.
    """
    # Xử lý input case-insensitive (tùy chọn nhưng tốt cho UX)
    # Ở đây giữ nguyên theo DB keys
    flights = FLIGHTS_DB.get((origin, destination))
    
    if not flights:
        # Thử tra ngược
        flights = FLIGHTS_DB.get((destination, origin))
    
    if not flights:
        return f"Không tìm thấy chuyến bay từ {origin} đến {destination}."
    
    result = [f"Danh sách chuyến bay từ {origin} đến {destination}:"]
    for f in flights:
        price_str = format_currency(f['price'])
        result.append(f"- {f['airline']} ({f['class']}): {f['departure']} -> {f['arrival']} | Giá: {price_str}")
        
    return "\n".join(result)

@tool
def search_hotels(city: str) -> str:
    """
    Tìm kiếm khách sạn tại một thành phố.
    Tham số:
    - city: tên thành phố cần tìm khách sạn (VD: 'Đà Nẵng', 'Phú Quốc', 'Hồ Chí Minh')
    Trả về danh sách khách sạn với số sao, khu vực, giá mỗi đêm và đánh giá.
    """
    hotels = HOTELS_DB.get(city)
    
    if not hotels:
        return f"Hiện tại không có dữ liệu khách sạn tại {city}."
    
    result = [f"Danh sách khách sạn tại {city}:"]
    for h in hotels:
        price_str = format_currency(h['price_per_night'])
        result.append(f"- {h['name']} ({h['stars']}*): Khu vực {h['area']} | Giá/đêm: {price_str} | Đánh giá: {h['rating']}/5")
        
    return "\n".join(result)

@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """
    Tính toán ngân sách còn lại sau khi trừ các khoản chi phí.
    Tham số:
    - total_budget: tổng ngân sách ban đầu (VNĐ)
    - expenses: chuỗi mô tả các khoản chi, mỗi khoản cách nhau bởi dấu phẩy,
      định dạng 'tên_khoản:số_tiền' (VD: 'vé_máy_bay:890000,khách_sạn:650000')
    Trả về bảng chi tiết các khoản chi và số tiền còn lại.
    Nếu vượt ngân sách, cảnh báo rõ ràng số tiền thiếu.
    """
    try:
        expense_items = []
        total_cost = 0
        
        # Parse chuỗi expenses
        items = [i.strip() for i in expenses.split(",") if i.strip()]
        for item in items:
            name, amount = item.split(":")
            amount_val = int(amount.strip())
            total_cost += amount_val
            expense_items.append((name.strip().replace("_", " ").capitalize(), amount_val))
            
        remaining = total_budget - total_cost
        
        # Format bảng
        lines = ["Bảng chi phí:"]
        for name, amount in expense_items:
            lines.append(f"- {name}: {format_currency(amount)}")
        
        lines.append("---")
        lines.append(f"Tổng chi: {format_currency(total_cost)}")
        lines.append(f"Ngân sách: {format_currency(total_budget)}")
        
        if remaining >= 0:
            lines.append(f"Còn lại: {format_currency(remaining)}")
        else:
            lines.append(f"Vượt ngân sách {format_currency(abs(remaining))}! Cần điều chỉnh.")
            
        return "\n".join(lines)
        
    except ValueError:
        return "Lỗi: Định dạng chuỗi chi phí sai. Vui lòng sử dụng định dạng 'tên:số_tiền,tên:số_tiền'."
    except Exception as e:
        return f"Lỗi không xác định: {str(e)}"
