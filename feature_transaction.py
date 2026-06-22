# -*- coding: utf-8 -*-
"""
feature_transaction.py
-------------------------
Chức năng 3: Giao dịch Nhập / Xuất kho (Đa hình).

Cùng một lệnh gọi current_product.import_stock(quantity) /
current_product.export_stock(quantity), nhưng hành vi thực thi sẽ khác
nhau tùy loại sản phẩm đang active (ColdStorageProduct hao hụt 5% khi
xuất, HazardousProduct chặn nhập vượt hạn mức an toàn, HybridPremiumProduct
áp dụng đồng thời cả hai cơ chế). Đây chính là Đa hình (Polymorphism).
"""

from utils import parse_int


def feature3_transaction(current_product):
    if current_product is None:
        print("\nHệ thống chưa có sản phẩm nào được chọn. Vui lòng đăng ký/chọn sản phẩm trước.")
        return

    print("\n--- GIAO DỊCH NHẬP / XUẤT KHO ---")
    print("1. Nhập kho")
    print("2. Xuất kho")
    choice = input("Chọn giao dịch (1-2): ").strip()

    if choice == "1":
        _handle_import(current_product)
    elif choice == "2":
        _handle_export(current_product)
    else:
        print("Lựa chọn không hợp lệ!")


def _handle_import(current_product):
    text = input("Nhập số lượng nhập kho: ").strip()
    try:
        quantity = parse_int(text)
        # Đa hình: import_stock() ở đây có thể là của ColdStorageProduct,
        # HazardousProduct hoặc HybridPremiumProduct (override gọi đích danh
        # HazardousProduct.import_stock để giải quyết xung đột MRO).
        current_product.import_stock(quantity)
        print("\nNhập kho thành công!")
        print(f"Số lượng nhập vào: {quantity:g} đơn vị")
        print(f"Số lượng tồn kho hiện tại: {current_product.stock_quantity:g} đơn vị")
    except ValueError as e:
        print(f"Giao dịch thất bại! {e}")


def _handle_export(current_product):
    text = input("Nhập số lượng cần xuất: ").strip()
    try:
        quantity = parse_int(text)
        result = current_product.export_stock(quantity)
        print("\nXuất kho thành công!")

        if isinstance(result, tuple):
            # Trường hợp ColdStorageProduct/HybridPremiumProduct: trả về (quantity, loss)
            _, loss = result
            total_deduct = quantity + loss
            print(f"Số lượng yêu cầu: {quantity:g} đơn vị")
            print(f"Số lượng hao hụt bảo quản (5%): {loss:g} đơn vị")
            print(f"Tổng số lượng khấu trừ trong kho: {total_deduct:g} đơn vị")
        else:
            # Trường hợp HazardousProduct: xuất kho bình thường, không hao hụt
            print(f"Số lượng xuất: {quantity:g} đơn vị")

        print(f"Số lượng tồn kho còn lại: {current_product.stock_quantity:g} đơn vị")
    except ValueError as e:
        print(f"Giao dịch thất bại! {e}")
