# -*- coding: utf-8 -*-
"""
main.py
--------
Điểm khởi chạy chương trình Amazon Inventory Simulator Pro.
Chỉ chịu trách nhiệm hiển thị menu và điều phối (route) sang các module
feature_*.py tương ứng. Toàn bộ logic nghiệp vụ nằm trong các module riêng
để dễ quản lý, mở rộng và sửa lỗi độc lập.
"""

from feature_register_product import feature1_register_product
from feature_view_info import feature2_view_info
from feature_transaction import feature3_transaction
from feature_cooling_cost import feature4_cooling_cost
from feature_compare_merge import feature5_compare_merge
from feature_dispatch import feature6_dispatch


def main():
    # State chung của toàn hệ thống, được truyền vào/lấy ra từ mỗi feature
    products = []           # Danh sách toàn bộ sản phẩm đã đăng ký trong hệ thống
    current_product = None  # Sản phẩm đang được chọn để giao dịch

    while True:
        print("\n" + " AMAZON INVENTORY SIMULATOR PRO ".center(70, "="))
        print('''
        1. Đăng ký mã hàng hóa mới (Chọn loại sản phẩm)
        2. Xem thông tin & Kiểm tra thứ tự kế thừa (MRO)
        3. Giao dịch Nhập / Xuất kho (Đa hình)
        4. Kiểm tra điều kiện bảo quản / Tính chi phí phụ trội
        5. Kiểm tra tính năng gộp lô hàng & So sánh tồn kho (Overloading)
        6. Điều phối vận chuyển qua Đối tác thứ ba (Duck Typing)
        7. Thoát chương trình
        ''')
        print("=" * 70)

        choice = input("Chọn chức năng (1-7): ").strip()

        match choice:
            case "1":
                new_product = feature1_register_product(products)
                if new_product is not None:
                    current_product = new_product

            case "2":
                feature2_view_info(current_product)

            case "3":
                feature3_transaction(current_product)

            case "4":
                feature4_cooling_cost(current_product)

            case "5":
                feature5_compare_merge(products, current_product)

            case "6":
                feature6_dispatch(current_product)

            case "7":
                print("\nCảm ơn đã sử dụng hệ thống Amazon Inventory Simulator Pro!")
                break

            case _:
                print("\nChức năng không tồn tại!")


if __name__ == "__main__":
    main()
