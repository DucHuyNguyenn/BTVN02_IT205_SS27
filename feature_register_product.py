# -*- coding: utf-8 -*-
"""
feature_register_product.py
------------------------------
Chức năng 1: Đăng ký mã hàng hóa mới (chọn loại: Đông lạnh / Nguy hiểm / Hybrid).
"""

from product_models import BaseProduct, ColdStorageProduct, HazardousProduct, HybridPremiumProduct


def feature1_register_product(products):
    """
    Tạo và thêm một sản phẩm mới vào danh sách `products`.
    Trả về đối tượng sản phẩm mới (để main.py gán làm current_product),
    hoặc None nếu đăng ký thất bại (dữ liệu không hợp lệ).
    """
    print("\n--- CHỌN LOẠI SẢN PHẨM KHỞI TẠO ---")
    print("1. Cold Storage Product (Hàng Đông Lạnh)")
    print("2. Hazardous Product (Hàng Nguy Hiểm)")
    print("3. Hybrid Premium Product (Hàng Lai Cao Cấp)")
    product_type = input("Chọn loại sản phẩm (1-3): ").strip()

    if product_type not in ("1", "2", "3"):
        print("\nLoại sản phẩm không hợp lệ!")
        return None

    product_code = input("Nhập mã sản phẩm 10 ký tự: ").strip()
    # Bẫy: mã sản phẩm phải đúng 10 ký tự và bắt đầu bằng chữ -> @staticmethod
    if not BaseProduct.validate_product_code(product_code):
        print("Mã sản phẩm không hợp lệ! Phải gồm đúng 10 ký tự và bắt đầu bằng chữ cái.")
        return None

    if any(p.product_code == product_code for p in products):
        print("Mã sản phẩm đã tồn tại trong hệ thống!")
        return None

    product_name_raw = input("Nhập tên sản phẩm: ")

    try:
        if product_type == "1":
            temperature = float(input("Nhập nhiệt độ bảo quản yêu cầu (độ C): ").strip())
            new_product = ColdStorageProduct(
                product_code, product_name_raw, stock_quantity=0, required_temperature=temperature
            )
            print("\nĐăng ký sản phẩm Đông Lạnh thành công!")

        elif product_type == "2":
            safety_limit = int(input("Nhập hạn mức an toàn tối đa (đơn vị): ").strip())
            new_product = HazardousProduct(
                product_code, product_name_raw, stock_quantity=0, max_safety_limit=safety_limit
            )
            print("\nĐăng ký sản phẩm Nguy Hiểm thành công!")

        else:  # product_type == "3"
            temperature = float(input("Nhập nhiệt độ bảo quản yêu cầu (độ C): ").strip())
            safety_limit = int(input("Nhập hạn mức an toàn tối đa (đơn vị): ").strip())
            new_product = HybridPremiumProduct(
                product_code, product_name_raw, stock_quantity=0,
                required_temperature=temperature, max_safety_limit=safety_limit
            )
            print("\nĐăng ký sản phẩm Lai Cao Cấp (Hybrid) thành công!")

    except ValueError:
        print("Dữ liệu nhập không hợp lệ (nhiệt độ/hạn mức phải là số)!")
        return None

    products.append(new_product)
    print(f"Tên sản phẩm: {new_product.product_name}")
    return new_product
