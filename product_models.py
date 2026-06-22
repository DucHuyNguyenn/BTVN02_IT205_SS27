# -*- coding: utf-8 -*-
"""
product_models.py
-------------------
Module định nghĩa toàn bộ các lớp sản phẩm của hệ thống Amazon Inventory
Simulator Pro: lớp trừu tượng BaseProduct, các lớp con ColdStorageProduct/
HazardousProduct, và lớp đa kế thừa kiểu "diamond" HybridPremiumProduct.
"""

from abc import ABC, abstractmethod


class BaseProduct(ABC):
    """
    Lớp trừu tượng (Abstract Base Class) làm bộ khung chuẩn cho mọi loại
    hàng hóa trong kho. Không thể khởi tạo trực tiếp lớp này vì có chứa
    @abstractmethod (Bẫy 1: Python tự ném TypeError nếu cố tình gọi
    BaseProduct(...) trực tiếp, đây là cơ chế bảo vệ tính trừu tượng có
    sẵn của ABCMeta, không cần code thêm).
    """

    # Class Attributes: dùng chung cho toàn hệ thống
    warehouse_name = "Amazon Logistics"
    base_storage_fee = 5000  # Phí lưu kho cơ bản/ngày

    def __init__(self, product_code, product_name, stock_quantity=0, **kwargs):
        self._product_code = product_code
        # Gọi qua property setter để tự động chuẩn hóa tên (in hoa, xóa khoảng trắng thừa)
        self.product_name = product_name
        # Private attribute (đóng gói số lượng tồn kho) -> _BaseProduct__stock_quantity
        self.__stock_quantity = stock_quantity
        # super().__init__(**kwargs) ở cuối chuỗi __init__ hợp tác (cooperative
        # multiple inheritance): xem giải thích chi tiết trong HybridPremiumProduct.
        super().__init__(**kwargs)

    # ---------------------- PROPERTIES ----------------------
    @property
    def stock_quantity(self):
        """Chỉ cho đọc số lượng tồn kho, không có setter để tránh thao túng bừa bãi."""
        return self.__stock_quantity

    @property
    def product_code(self):
        return self._product_code

    @property
    def product_name(self):
        return self._product_name

    @product_name.setter
    def product_name(self, name):
        # Chuẩn hóa: xóa khoảng trắng thừa ở 2 đầu/giữa các từ, sau đó in hoa
        self._product_name = " ".join(name.split()).upper()

    # ---------------------- PROTECTED HELPER ----------------------
    def _adjust_stock(self, delta):
        """
        Vì __stock_quantity bị name-mangling (chỉ BaseProduct truy cập trực
        tiếp được), các lớp con dùng phương thức bảo vệ này để cộng/trừ số
        lượng tồn kho an toàn, vẫn giữ nguyên tính đóng gói (encapsulation).
        """
        self.__stock_quantity += delta

    # ---------------------- ABSTRACT METHODS ----------------------
    @abstractmethod
    def import_stock(self, quantity):
        """Mỗi loại sản phẩm phải tự định nghĩa cách nhập kho (Đa hình)."""
        raise NotImplementedError

    @abstractmethod
    def export_stock(self, quantity):
        """Mỗi loại sản phẩm phải tự định nghĩa cách xuất kho (Đa hình)."""
        raise NotImplementedError

    # ---------------------- OPERATOR OVERLOADING ----------------------
    def __add__(self, other):
        """
        Nạp chồng toán tử +: cộng số lượng tồn kho của 2 sản phẩm bất kỳ.
        Bẫy 3: nếu `other` không phải BaseProduct (str, int...) -> trả về
        NotImplemented để Python tự chuyển thành TypeError chuẩn.
        """
        if not isinstance(other, BaseProduct):
            return NotImplemented
        return self.stock_quantity + other.stock_quantity

    def __lt__(self, other):
        """
        Nạp chồng toán tử <: so sánh số lượng tồn kho của 2 sản phẩm.
        Bẫy 3: tương tự __add__, trả về NotImplemented nếu kiểu không hợp lệ.
        """
        if not isinstance(other, BaseProduct):
            return NotImplemented
        return self.stock_quantity < other.stock_quantity

    # ---------------------- STATIC & CLASS METHOD ----------------------
    @staticmethod
    def validate_product_code(product_code):
        """
        Static method: logic kiểm tra hoàn toàn độc lập với trạng thái của
        đối tượng/lớp. Mã sản phẩm phải là chuỗi đúng 10 ký tự và ký tự
        đầu tiên phải là chữ cái (ví dụ "AMZ1234567").
        """
        return (
            isinstance(product_code, str)
            and len(product_code) == 10
            and product_code[0].isalpha()
        )

    @classmethod
    def update_warehouse_name(cls, new_name):
        """
        Class method: dùng cls để thay đổi Class Attribute `warehouse_name`,
        áp dụng cho toàn hệ thống (mọi đối tượng đều dùng chung thuộc tính
        cấp lớp này).
        """
        cls.warehouse_name = new_name

    def __repr__(self):
        return f"{type(self).__name__}({self.product_code}, {self.product_name}, {self.stock_quantity:g} units)"


class ColdStorageProduct(BaseProduct):
    """Hàng đông lạnh: cần kiểm soát nhiệt độ, hao hụt 5% khi xuất kho."""

    COOLING_LOSS_RATE = 0.05        # Hao hụt bảo quản khi xuất kho
    COOLING_COST_PER_UNIT = 3000    # Chi phí làm lạnh / đơn vị tồn kho / ngày

    def __init__(self, product_code, product_name, stock_quantity=0,
                 required_temperature=-18, **kwargs):
        self.required_temperature = required_temperature
        # super().__init__() tái sử dụng logic khởi tạo của lớp cha (kế thừa).
        # Lưu ý: trong ngữ cảnh đa kế thừa (HybridPremiumProduct), lệnh super()
        # này KHÔNG nhất thiết gọi thẳng BaseProduct mà sẽ đi theo đúng MRO
        # (có thể là HazardousProduct trước, xem chi tiết ở HybridPremiumProduct).
        super().__init__(product_code, product_name, stock_quantity, **kwargs)

    def import_stock(self, quantity):
        """Ghi đè (override): nhập kho bình thường, không có điều kiện đặc biệt."""
        if quantity <= 0:
            raise ValueError("Số lượng nhập kho phải lớn hơn 0.")
        self._adjust_stock(quantity)
        return quantity

    def export_stock(self, quantity):
        """
        Ghi đè (override): hàng đông lạnh khi xuất kho luôn chịu thêm 5% phí
        hao hụt bảo quản phụ trội tính trên số lượng xuất.
        Trả về tuple (quantity, loss) để feature hiển thị chi tiết.
        """
        if quantity <= 0:
            raise ValueError("Số lượng xuất kho phải lớn hơn 0.")
        loss = quantity * self.COOLING_LOSS_RATE
        total_deduct = quantity + loss
        if total_deduct > self.stock_quantity:
            raise ValueError("Số lượng tồn kho không đủ để xuất (đã bao gồm hao hụt bảo quản).")
        self._adjust_stock(-total_deduct)
        return quantity, loss

    def apply_cooling_cost(self):
        """Tính chi phí vận hành máy lạnh phát sinh dựa trên số lượng tồn kho hiện tại."""
        return self.stock_quantity * self.COOLING_COST_PER_UNIT


class HazardousProduct(BaseProduct):
    """Hàng nguy hiểm: tuyệt đối không vượt quá hạn mức lưu trữ an toàn."""

    def __init__(self, product_code, product_name, stock_quantity=0,
                 max_safety_limit=500, **kwargs):
        self.max_safety_limit = max_safety_limit
        super().__init__(product_code, product_name, stock_quantity, **kwargs)

    def import_stock(self, quantity):
        """
        Ghi đè (override): kiểm tra nếu stock_quantity + quantity vượt quá
        max_safety_limit thì từ chối nhập kho (Bẫy 2).
        """
        if quantity <= 0:
            raise ValueError("Số lượng nhập kho phải lớn hơn 0.")
        if self.stock_quantity + quantity > self.max_safety_limit:
            raise ValueError(
                f"Số lượng nhập vào khiến tồn kho vượt quá hạn mức an toàn "
                f"cho phép (Tối đa: {self.max_safety_limit:g})."
            )
        self._adjust_stock(quantity)
        return quantity

    def export_stock(self, quantity):
        """Ghi đè (override): xuất kho bình thường theo quy trình an toàn."""
        if quantity <= 0:
            raise ValueError("Số lượng xuất kho phải lớn hơn 0.")
        if quantity > self.stock_quantity:
            raise ValueError("Số lượng tồn kho không đủ để xuất.")
        self._adjust_stock(-quantity)
        return quantity


class HybridPremiumProduct(ColdStorageProduct, HazardousProduct):
    """
    Dòng sản phẩm lai cao cấp: đa kế thừa (Multiple Inheritance) kiểu
    "diamond" từ CẢ ColdStorageProduct VÀ HazardousProduct -- cả hai lớp
    cha này đều cùng kế thừa từ BaseProduct.

    MRO (Method Resolution Order) theo C3-linearization của Python:
        HybridPremiumProduct -> ColdStorageProduct -> HazardousProduct
                              -> BaseProduct -> ABC -> object
    Có thể kiểm tra trực tiếp bằng HybridPremiumProduct.__mro__.

    XUNG ĐỘT PHƯƠNG THỨC: cả ColdStorageProduct và HazardousProduct đều
    định nghĩa import_stock()/export_stock() với hành vi KHÁC nhau. Nếu
    không override, Python sẽ tự động chọn phiên bản của ColdStorageProduct
    (vì nó đứng trước trong MRO) cho cả 2 phương thức -- điều này SAI với
    yêu cầu nghiệp vụ (Hybrid cần áp dụng đồng thời kiểm tra an toàn của
    Hazardous KHI nhập kho, và hao hụt bảo quản của ColdStorage KHI xuất
    kho). Vì vậy ta phải override rõ ràng, gọi đích danh class mong muốn
    (TênLớp.phương_thức(self, ...)) thay vì dùng super() đơn thuần.
    """

    def __init__(self, product_code, product_name, stock_quantity=0,
                 required_temperature=-18, max_safety_limit=500):
        # Cooperative multiple inheritance: super().__init__() ở đây sẽ đi
        # vào ColdStorageProduct.__init__ trước (theo MRO). Bên trong đó,
        # super().__init__() tiếp theo của ColdStorageProduct lại trỏ tới
        # HazardousProduct.__init__ (KHÔNG phải BaseProduct trực tiếp, vì
        # MRO của HybridPremiumProduct quy định thứ tự này) -- và cuối cùng
        # HazardousProduct.__init__ gọi tiếp BaseProduct.__init__. Nhờ vậy
        # cả required_temperature và max_safety_limit đều được khởi tạo đầy
        # đủ chỉ với một lệnh super().__init__() duy nhất.
        super().__init__(
            product_code, product_name, stock_quantity,
            required_temperature=required_temperature,
            max_safety_limit=max_safety_limit,
        )

    def import_stock(self, quantity):
        """
        Giải quyết xung đột: nhập kho của Hybrid PHẢI tuân thủ kiểm tra an
        toàn nghiêm ngặt của HazardousProduct (Bẫy 2 áp dụng cho cả Hybrid).
        Gọi đích danh HazardousProduct.import_stock thay vì để MRO tự chọn
        ColdStorageProduct.import_stock (vốn không có kiểm tra an toàn).
        """
        return HazardousProduct.import_stock(self, quantity)

    def export_stock(self, quantity):
        """
        Giải quyết xung đột: xuất kho của Hybrid PHẢI áp dụng hao hụt bảo
        quản đông lạnh 5% của ColdStorageProduct. Gọi đích danh
        ColdStorageProduct.export_stock để đảm bảo đúng nghiệp vụ.
        """
        return ColdStorageProduct.export_stock(self, quantity)


if __name__ == "__main__":
    # Demo nhanh Bẫy 1: khởi tạo trực tiếp lớp trừu tượng BaseProduct
    try:
        p = BaseProduct("AMZ0000001", "test")
    except TypeError as e:
        print(f"[Bẫy 1 - OK] Không thể khởi tạo BaseProduct trực tiếp: {e}")

    print("\nMRO của HybridPremiumProduct:")
    for cls in HybridPremiumProduct.__mro__:
        print(" ->", cls.__name__)

    print("\nDemo khởi tạo Hybrid và kiểm tra cả 2 thuộc tính cha:")
    hybrid = HybridPremiumProduct("AMZ0012345", "special vaccine lo a",
                                   stock_quantity=100, required_temperature=-70,
                                   max_safety_limit=200)
    print(hybrid)
    print("required_temperature:", hybrid.required_temperature)
    print("max_safety_limit:", hybrid.max_safety_limit)
