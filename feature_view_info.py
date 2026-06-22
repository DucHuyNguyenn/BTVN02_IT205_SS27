# -*- coding: utf-8 -*-
"""
feature_view_info.py
----------------------
Chức năng 2: Xem thông tin chi tiết sản phẩm hiện tại & in danh sách MRO
của lớp đó (kiểm tra kỹ thuật đa kế thừa).
"""


def feature2_view_info(current_product):
    if current_product is None:
        print("\nHệ thống chưa có thông tin sản phẩm. Vui lòng đăng ký sản phẩm ở Chức năng 1 trước.")
        return

    print("\n--- THÔNG TIN SẢN PHẨM HIỆN TẠI ---")
    print(f"Loại sản phẩm: {type(current_product).__name__}")
    print(f"Chuỗi kho: {current_product.warehouse_name}")
    print(f"Mã sản phẩm: {current_product.product_code}")
    print(f"Tên sản phẩm: {current_product.product_name}")
    print(f"Số lượng tồn kho: {current_product.stock_quantity:g} đơn vị")

    # Hiển thị thuộc tính riêng tùy loại sản phẩm (đa hình về thuộc tính)
    if hasattr(current_product, "required_temperature"):
        print(f"Nhiệt độ yêu cầu: {current_product.required_temperature:g} độ C")
    if hasattr(current_product, "max_safety_limit"):
        print(f"Hạn mức an toàn tối đa: {current_product.max_safety_limit:g} đơn vị")

    print("\n--- KIỂM TRA MRO (Method Resolution Order) ---")
    mro_chain = " -> ".join(cls.__name__ for cls in type(current_product).__mro__)
    print(mro_chain)
