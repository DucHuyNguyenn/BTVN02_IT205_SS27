# -*- coding: utf-8 -*-
"""
carrier_partner.py
---------------------
Minh họa kỹ thuật Duck Typing: FedExCarrier và DHLCarrier là 2 lớp HOÀN
TOÀN ĐỘC LẬP, không kế thừa từ một interface/abstract chung nào. Hàm
dispatch_to_carrier() chỉ quan tâm đối tượng truyền vào có phương thức
ship_package(product, quantity) hay không.
"""


class FedExCarrier:
    """Đối tác vận chuyển FedEx - độc lập, không kế thừa BaseProduct hay interface nào."""

    def ship_package(self, product, quantity):
        print(f"[Hệ thống FedEx]: Đang tiếp nhận mã sản phẩm {product.product_code}...")
        product.export_stock(quantity)
        return True


class DHLCarrier:
    """Đối tác vận chuyển DHL - độc lập, không kế thừa BaseProduct hay interface nào."""

    def ship_package(self, product, quantity):
        print(f"[Hệ thống DHL]: Đang tiếp nhận mã sản phẩm {product.product_code}...")
        product.export_stock(quantity)
        return True


def dispatch_to_carrier(carrier_agent, product, quantity):
    """
    Hàm toàn cục độc lập, KHÔNG quan tâm carrier_agent thuộc class nào.
    Miễn là đối tượng truyền vào có hàm ship_package(product, quantity) thì
    hàm này hoạt động được -- tinh thần Duck Typing, cho phép tích hợp
    hàng trăm đơn vị vận chuyển mới trong tương lai mà không cần sửa code
    ở lớp sản phẩm gốc hay ở hàm này.

    Bẫy 4: nếu đối tượng truyền vào không có ship_package -> bắt AttributeError.
    """
    try:
        carrier_agent.ship_package(product, quantity)
        print("Xác thực đối tác bằng Duck Typing thành công!")
        print(f"Đơn vị vận chuyển đã tiếp nhận đơn hàng số lượng: {quantity:g} đơn vị.")
        print(f"Số lượng tồn kho cập nhật: {product.stock_quantity:g} đơn vị.")
    except AttributeError:
        print("Đơn vị vận chuyển không hợp lệ hoặc chưa ký kết hợp đồng kỹ thuật")
