# -*- coding: utf-8 -*-
"""
feature_cooling_cost.py
--------------------------
Chức năng 4: Kiểm tra điều kiện bảo quản / Tính chi phí phụ trội.

Chỉ áp dụng cho sản phẩm có tính chất đông lạnh (ColdStorageProduct hoặc
HybridPremiumProduct, vì HybridPremiumProduct kế thừa ColdStorageProduct).
HazardousProduct thông thường không hỗ trợ tính năng này.
"""

from product_models import ColdStorageProduct, HazardousProduct


def feature4_cooling_cost(current_product):
    if current_product is None:
        print("\nHệ thống chưa có sản phẩm nào được chọn. Vui lòng đăng ký/chọn sản phẩm trước.")
        return

    if isinstance(current_product, ColdStorageProduct):
        print("\n--- TÍNH PHÍ BẢO QUẢN ĐÔNG LẠNH ---")
        print(f"Số lượng tồn kho hiện tại: {current_product.stock_quantity:g} đơn vị")
        print(f"Nhiệt độ yêu cầu: {current_product.required_temperature:g} độ C")
        cost = current_product.apply_cooling_cost()
        print(f"Chi phí làm lạnh phát sinh trong ngày: +{cost:,.0f} VND")

    elif isinstance(current_product, HazardousProduct):
        print("\nSản phẩm Nguy Hiểm thông thường không hỗ trợ tính năng tính chi phí làm lạnh.")

    else:
        print("\nLoại sản phẩm này không hỗ trợ tính năng bảo quản đông lạnh.")
