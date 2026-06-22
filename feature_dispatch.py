# -*- coding: utf-8 -*-
"""
feature_dispatch.py
----------------------
Chức năng 6: Điều phối vận chuyển qua Đối tác thứ ba (Duck Typing).
"""

from carrier_partner import FedExCarrier, DHLCarrier, dispatch_to_carrier
from utils import parse_int


def feature6_dispatch(current_product):
    if current_product is None:
        print("\nVui lòng đăng ký/chọn sản phẩm trước khi điều phối vận chuyển.")
        return

    print("\n--- ĐIỀU PHỐI ĐƠN VỊ VẬN CHUYỂN NGOÀI ---")
    print("1. Vận chuyển qua đối tác FedEx")
    print("2. Vận chuyển qua đối tác DHL")
    choice = input("Chọn đối tác vận chuyển (1-2): ").strip()

    if choice == "1":
        carrier = FedExCarrier()
    elif choice == "2":
        carrier = DHLCarrier()
    else:
        print("Đối tác vận chuyển không hợp lệ!")
        return

    text = input("Nhập số lượng hàng hóa bàn giao: ").strip()
    try:
        quantity = parse_int(text)
    except ValueError:
        print("Số lượng không hợp lệ!")
        return

    try:
        # dispatch_to_carrier không quan tâm `carrier` thuộc class nào (Duck
        # Typing), miễn là nó có ship_package(product, quantity). Bẫy 4
        # (AttributeError) được xử lý bên trong dispatch_to_carrier().
        dispatch_to_carrier(carrier, current_product, quantity)
    except ValueError as e:
        # Trường hợp product.export_stock() bên trong ship_package() báo lỗi
        # nghiệp vụ (ví dụ không đủ tồn kho để xuất)
        print(f"Điều phối vận chuyển thất bại: {e}")
