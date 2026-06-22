#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  AMAZON INVENTORY SIMULATOR PRO
  Module: Quan ly Kho Hang Thong Minh Amazon Logistics
  Session 27 - Bai tap 2: OOP Nang cao
=============================================================================

  DESIGN DOCUMENT / PHAN TICH & THIET KE GIAI PHAP
  ===================================================

  1. SO DO CAU TRUC KIEN TRUC (Class Hierarchy)
  ----------------------------------------------
  
      BaseProduct (ABC - Abstract Base Class)
      +--- Dinh nghia bo khung chuan: thuoc tinh kho, phi luu kho
      +--- Private: __stock_quantity (dong goi nghiem ngat)
      +--- Properties: stock_quantity (read-only), product_name (get/set)
      +--- Abstract Methods: import_stock(), export_stock()
      +--- Operator Overloading: __add__, __lt__
      +--- @staticmethod: validate_product_code()
      +--- @classmethod: update_warehouse_name()
      |
      +-- ColdStorageProduct (Ke thua don tu BaseProduct)
      |   +--- Bo sung: required_temperature
      |   +--- Override import_stock(): nhap kho thong thuong
      |   +--- Override export_stock(): ap dung 5% hao hut bao quan
      |   +--- Instance Method: apply_cooling_cost()
      |
      +-- HazardousProduct (Ke thua don tu BaseProduct)
      |   +--- Bo sung: max_safety_limit
      |   +--- Override import_stock(): chan neu vuot gioi han an toan
      |   +--- Override export_stock(): xuat kho an toan thong thuong
      |
      +-- HybridPremiumProduct (DA KE THUA: ColdStorageProduct, HazardousProduct)
          +--- Tich hop: required_temperature + max_safety_limit
          +--- import_stock(): uu tien co che an toan cua HazardousProduct
          +--- export_stock(): uu tien co che hao hut 5% cua ColdStorageProduct

  2. BAO CAO KY THUAT - MRO (Method Resolution Order)
  ----------------------------------------------------
  Python su dung thuat toan C3 Linearization de xac dinh MRO.
  Voi HybridPremiumProduct(ColdStorageProduct, HazardousProduct), MRO la:
  
      HybridPremiumProduct -> ColdStorageProduct -> HazardousProduct 
      -> BaseProduct -> ABC -> object
  
  Khi mot phuong thuc duoc goi tren HybridPremiumProduct:
  - Python tim trong HybridPremiumProduct truoc
  - Neu khong co, tim trong ColdStorageProduct (lop cha thu nhat)
  - Sau do moi tim trong HazardousProduct (lop cha thu hai)
  - Cuoi cung la BaseProduct
  
  De giai quyet XUNG DOT phuong thuc trung ten (import_stock, export_stock
  deu co o ca hai lop cha), HybridPremiumProduct GHI DE TUONG MINH
  (explicit override) va goi truc tiep phuong thuc cua lop cha mong muon
  thong qua cu phap ClassName.method(self, ...), thay vi dung super().
  Dieu nay dam bao:
  - import_stock() luon kich hoat co che chan an toan cua Hazardous
  - export_stock() luon kich hoat co che hao hut cua ColdStorage

  3. PHAN TICH DUCK TYPING
  -------------------------
  Ham dispatch_to_carrier(carrier_agent, product, quantity) khong kiem tra
  kieu du lieu (type/class) cua carrier_agent. No chi quan tam den VIEC
  DOI TUONG CO PHUONG THUC ship_package() HAY KHONG.
  
  Uu diem:
  - Khong can interface chung hay lop co so cho cac carrier
  - Co the tich hop hang tram don vi van chuyen moi (FedEx, DHL, UPS, 
    VNPost...) chi can moi class co phuong thuc ship_package(product, quantity)
  - Khong can sua doi code lop san pham goc (BaseProduct va cac subclass)
  - Giam coupling, tang tinh mo rong (Open-Closed Principle)

=============================================================================
"""

from abc import ABC, abstractmethod


# ============================================================
#  ABSTRACT BASE CLASS: BaseProduct
# ============================================================
class BaseProduct(ABC):
    """
    Lop truu tuong dinh nghia bo khung chuan cho moi loai hang hoa trong kho.
    
    - @abstractmethod: Danh dau phuong thuc bat buoc subclass phai ghi de.
      Neu khong, Python se tu choi khoi tao doi tuong va nem TypeError.
    - @property: Bien phuong thuc thanh thuoc tinh chi doc (getter),
      giup dong goi du lieu, ngan chan truy cap truc tiep vao bien private.
    - @classmethod: Phuong thuc nhan cls (lop) thay vi self (doi tuong),
      dung de thay doi bien lop dung chung cho toan bo he thong.
    - @staticmethod: Phuong thuc tien ich khong phu thuoc vao lop hay doi tuong,
      dung cho cac ham validation doc lap.
    """
    
    # --- Class Attributes (Thuoc tinh lop - dung chung toan he thong) ---
    warehouse_name: str = "Amazon Logistics"
    base_storage_fee: int = 5000  # Phi luu kho co ban/ngay (VND)
    
    def __init__(self, product_code: str, product_name: str):
        """
        Khoi tao san pham co so.
        - __stock_quantity: Su dung dau gach duoi kep (name mangling) de
          Python tu dong doi ten thanh _BaseProduct__stock_quantity,
          ngan chan truy cap vo tinh tu ben ngoai hoac subclass.
        """
        self._product_code: str = product_code         # protected
        self._product_name: str = ""                    # protected, se qua setter
        self.__stock_quantity: int = 0                  # private (name mangling)
        self.product_name = product_name                # goi setter de chuan hoa
    
    # ================================================================
    #  PROPERTIES (Dong goi - Encapsulation)
    # ================================================================
    
    @property
    def stock_quantity(self) -> float:
        """
        @property: Getter cho so luong ton kho.
        Cho phep doc gia tri __stock_quantity mot cach an toan tu ben ngoai.
        KHONG co setter - ngan chan thao tung so luong bua bai.
        Subclass phai dung _increase_stock() / _decrease_stock() de thay doi.
        """
        return self.__stock_quantity
    
    @property
    def product_code(self) -> str:
        """Getter cho ma san pham."""
        return self._product_code
    
    @property
    def product_name(self) -> str:
        """Getter cho ten san pham."""
        return self._product_name
    
    @product_name.setter
    def product_name(self, value: str) -> None:
        """
        Setter cho ten san pham: Tu dong chuan hoa.
        - strip(): xoa khoang trang thua o dau/cuoi
        - upper(): chuyen thanh chu IN HOA
        - ' '.join(...split()): chuan hoa khoang trang giua cac tu
        """
        self._product_name = ' '.join(value.strip().upper().split())
    
    # ================================================================
    #  PROTECTED HELPERS (Danh cho subclass)
    # ================================================================
    
    def _increase_stock(self, quantity: int) -> None:
        """Tang so luong ton kho (dung noi bo boi subclass)."""
        if quantity < 0:
            raise ValueError("So luong nhap khong duoc am.")
        self.__stock_quantity += quantity
    
    def _decrease_stock(self, quantity: float) -> None:
        """
        Giam so luong ton kho (dung noi bo boi subclass).
        Chap nhan float vi co hao hut (vd: 52.5 don vi).
        """
        if quantity < 0:
            raise ValueError("So luong xuat khong duoc am.")
        if quantity > self.__stock_quantity:
            raise ValueError(f"Khong du ton kho! Hien co: {self.__stock_quantity}")
        self.__stock_quantity -= quantity
    
    # ================================================================
    #  ABSTRACT METHODS
    # ================================================================
    
    @abstractmethod
    def import_stock(self, quantity: int):
        """
        @abstractmethod: Phuong thuc truu tuong - BAT BUOC moi subclass
        phai ghi de. Neu khong ghi de, Python se tu choi khoi tao doi tuong
        va nem TypeError khi co gang tao instance.
        
        Nhap hang vao kho. Moi loai san pham co quy tac nhap khac nhau.
        """
        pass
    
    @abstractmethod
    def export_stock(self, quantity: int):
        """
        @abstractmethod: Xuat hang khoi kho.
        Moi loai san pham co quy tac xuat khac nhau.
        """
        pass
    
    # ================================================================
    #  OPERATOR OVERLOADING (Nap chong toan tu)
    # ================================================================
    
    def __add__(self, other) -> int:
        """
        Nap chong toan tu + : Cong so luong ton kho cua 2 san pham.
        
        Edge Case: Kiem tra other co phai la BaseProduct khong.
        Neu khong, tra ve NotImplemented de Python thu goi __radd__
        hoac nem TypeError phu hop (thay vi crash voi AttributeError).
        """
        if not isinstance(other, BaseProduct):
            return NotImplemented
        return self.stock_quantity + other.stock_quantity
    
    def __lt__(self, other) -> bool:
        """
        Nap chong toan tu < : So sanh so luong ton kho.
        
        Edge Case: Kiem tra other co phai la BaseProduct khong.
        Neu khong, tra ve NotImplemented.
        """
        if not isinstance(other, BaseProduct):
            return NotImplemented
        return self.stock_quantity < other.stock_quantity
    
    # ================================================================
    #  STATIC METHOD
    # ================================================================
    
    @staticmethod
    def validate_product_code(product_code: str) -> bool:
        """
        @staticmethod: Phuong thuc tinh - khong phu thuoc vao cls hay self.
        Kiem tra ma san pham:
        - Phai bat dau bang CHU CAI (A-Z hoac a-z)
        - Phai co DUNG 10 KY TU
        
        Vi du hop le: "AMZ1234567"
        Vi du khong hop le: "1234567890" (bat dau bang so), "AMZ123" (< 10 ky tu)
        """
        if len(product_code) != 10:
            return False
        if not product_code[0].isalpha():
            return False
        return True
    
    # ================================================================
    #  CLASS METHOD
    # ================================================================
    
    @classmethod
    def update_warehouse_name(cls, new_name: str) -> None:
        """
        @classmethod: Phuong thuc lop - nhan cls (chinh lop do) lam tham so dau tien.
        Cho phep cap nhat ten kho hang TREN TOAN HE THONG (tat ca cac instance
        deu thay su thay doi vi day la class attribute).
        """
        cls.warehouse_name = new_name.strip()
    
    def __str__(self) -> str:
        """Bieu dien chuoi than thien cho san pham."""
        return f"{self.product_code} | {self.product_name} | Ton: {self.stock_quantity}"


# ============================================================
#  SUBCLASS 1: ColdStorageProduct (Hang Dong Lanh)
# ============================================================
class ColdStorageProduct(BaseProduct):
    """
    San pham dong lanh - Ke thua tu BaseProduct.
    Yeu cau kiem soat nhiet do nghiem ngat.
    """
    
    def __init__(self, product_code: str, product_name: str, required_temperature: float):
        """
        Khoi tao san pham dong lanh.
        Su dung super().__init__() de goi ham khoi tao cua lop cha (BaseProduct),
        dam bao ke thua day du logic khoi tao goc.
        """
        super().__init__(product_code, product_name)
        self.required_temperature: float = required_temperature
    
    def import_stock(self, quantity: int) -> None:
        """
        Nhap kho hang dong lanh - Thong thuong, khong co han che dac biet.
        """
        if quantity <= 0:
            raise ValueError("So luong nhap phai lon hon 0.")
        self._increase_stock(quantity)
    
    def export_stock(self, quantity: int) -> tuple:
        """
        Xuat kho hang dong lanh - CHIU THEM 5% PHI HAO HUT BAO QUAN.
        
        Hanh vi dac thu: Khi xuat kho, ngoai so luong yeu cau, he thong
        con tru them 5% hao hut do chenh lech nhiet do trong qua trinh
        van chuyen ra khoi kho lanh.
        
        Returns:
            tuple: (so_luong_yeu_cau, so_luong_hao_hut, tong_khau_tru)
        """
        if quantity <= 0:
            raise ValueError("So luong xuat phai lon hon 0.")
        
        loss: float = quantity * 0.05          # 5% hao hut bao quan
        total_deduction: float = quantity + loss
        
        self._decrease_stock(total_deduction)
        return (quantity, loss, total_deduction)
    
    def apply_cooling_cost(self) -> float:
        """
        Tinh chi phi van hanh may lanh phat sinh dua tren:
        - So luong ton kho hien tai
        - Nhiet do yeu cau (cang thap, chi phi cang cao)
        
        Cong thuc: cost = stock * |temp| * base_rate + fixed_overhead
        Trong do: base_rate = 40 VND/don vi/do C, fixed_overhead = 20,000 VND
        """
        base_rate: int = 40
        fixed_overhead: int = 20000
        cost: float = self.stock_quantity * abs(self.required_temperature) * base_rate + fixed_overhead
        return cost


# ============================================================
#  SUBCLASS 2: HazardousProduct (Hang Hoa Nguy Hiem)
# ============================================================
class HazardousProduct(BaseProduct):
    """
    San pham nguy hiem (hoa chat, chat de chay) - Ke thua tu BaseProduct.
    Co han muc luu tru toi da an toan trong mot phan khu.
    """
    
    def __init__(self, product_code: str, product_name: str, max_safety_limit: int):
        """
        Khoi tao san pham nguy hiem voi han muc an toan.
        """
        super().__init__(product_code, product_name)
        self.max_safety_limit: int = max_safety_limit
    
    def import_stock(self, quantity: int) -> None:
        """
        Nhap kho hang nguy hiem - KIEM TRA GIOI HAN AN TOAN.
        
        Co che: Neu so luong sau khi nhap vuot qua max_safety_limit,
        GIAO DICH BI TU CHOI de dam bao an toan chay no/hoa chat.
        """
        if quantity <= 0:
            raise ValueError("So luong nhap phai lon hon 0.")
        
        if self.stock_quantity + quantity > self.max_safety_limit:
            raise ValueError(
                f"Giao dich that bai! So luong nhap vao khien ton kho "
                f"vuot qua han muc an toan cho phep (Toi da: {self.max_safety_limit})."
            )
        
        self._increase_stock(quantity)
    
    def export_stock(self, quantity: int) -> None:
        """
        Xuat kho hang nguy hiem - Quy trinh an toan thong thuong.
        """
        if quantity <= 0:
            raise ValueError("So luong xuat phai lon hon 0.")
        self._decrease_stock(quantity)


# ============================================================
#  SUBCLASS 3: HybridPremiumProduct (DA KE THUA - Multiple Inheritance)
# ============================================================
class HybridPremiumProduct(ColdStorageProduct, HazardousProduct):
    """
    SAN PHAM LAI CAO CAP - Da ke thua tu ColdStorageProduct VA HazardousProduct.
    
    Day la dong san pham tich hop dac biet, vua yeu cau kiem soat nhiet do
    nghiem ngat (nhu hang dong lanh), vua phai tuan thu gioi han khoi luong
    an toan (nhu hang nguy hiem).
    
    Vi du: Cac hop chat sinh hoc, vac-xin dac chung, hoa chat can bao quan lanh.
    
    MRO (Method Resolution Order):
        HybridPremiumProduct -> ColdStorageProduct -> HazardousProduct
        -> BaseProduct -> ABC -> object
    
    Giai quyet xung dot phuong thuc:
    - import_stock(): Goi TRUC TIEP HazardousProduct.import_stock() de
      dam bao co che chan gioi han an toan luon duoc kich hoat.
    - export_stock(): Goi TRUC TIEP ColdStorageProduct.export_stock() de
      dam bao co che hao hut 5% luon duoc ap dung.
    """
    
    def __init__(
        self,
        product_code: str,
        product_name: str,
        required_temperature: float,
        max_safety_limit: int
    ):
        """
        Khoi tao HybridPremiumProduct.
        
        Vi day la da ke thua, ta goi __init__ cua BaseProduct mot cach
        tuong minh, sau do gan thu cong cac thuoc tinh tu ca hai nhanh cha.
        Dieu nay tranh duoc van de MRO phuc tap trong __init__.
        """
        # Goi truc tiep BaseProduct.__init__ de khoi tao cac thuoc tinh cot loi
        BaseProduct.__init__(self, product_code, product_name)
        
        # Gan thuoc tinh tu ColdStorageProduct
        self.required_temperature: float = required_temperature
        
        # Gan thuoc tinh tu HazardousProduct
        self.max_safety_limit: int = max_safety_limit
    
    def import_stock(self, quantity: int) -> None:
        """
        Nhap kho Hybrid - UU TIEN CO CHE AN TOAN.
        
        Goi TRUC TIEP HazardousProduct.import_stock() de kich hoat
        co che kiem tra gioi han an toan. Neu goi qua super(), MRO
        se dan den ColdStorageProduct.import_stock() (nhap thong thuong,
        khong co safety check).
        """
        HazardousProduct.import_stock(self, quantity)
    
    def export_stock(self, quantity: int) -> tuple:
        """
        Xuat kho Hybrid - UU TIEN CO CHE HAO HUT 5%.
        
        Goi TRUC TIEP ColdStorageProduct.export_stock() de kich hoat
        co che tinh hao hut bao quan 5%.
        """
        return ColdStorageProduct.export_stock(self, quantity)
    
    def apply_cooling_cost(self) -> float:
        """Ke thua phuong thuc tinh chi phi lam lanh tu ColdStorageProduct."""
        return ColdStorageProduct.apply_cooling_cost(self)


# ============================================================
#  DUCK TYPING: Doi tac van chuyen doc lap
# ============================================================
# Cac class nay KHONG ke thua tu bat ky lop co so chung nao.
# Duck Typing: "If it walks like a duck and quacks like a duck, it is a duck"
# Chi can co phuong thuc ship_package(), he thong se chap nhan.

class FedExCarrier:
    """Doi tac van chuyen FedEx - Tuan thu Duck Typing ug."""
    
    def ship_package(self, product: BaseProduct, quantity: int) -> None:
        """
        Phuong thuc van chuyen cua FedEx.
        Day chinh la "hop dong ky thuat" ma Duck Typing yeu cau.
        """
        print(f"[He thong FedEx]: Dang tiep nhan ma san pham {product.product_code}...")
        print(f"[FedEx] Xac nhan: Se van chuyen {quantity} don vi "
              f"san pham '{product.product_name}'")
        print("Xac thuc doi tac bang Duck Typing thanh cong!")


class DHLCarrier:
    """Doi tac van chuyen DHL - Tuan thu Duck Typing."""
    
    def ship_package(self, product: BaseProduct, quantity: int) -> None:
        """
        Phuong thuc van chuyen cua DHL.
        Chi can co phuong thuc nay voi signature tuong thich,
        he thong se tu dong tich hop ma khong can sua code goc.
        """
        print(f"[He thong DHL]: Dang tiep nhan ma san pham {product.product_code}...")
        print(f"[DHL] Xac nhan: Se van chuyen {quantity} don vi "
              f"san pham '{product.product_name}'")
        print("Xac thuc doi tac bang Duck Typing thanh cong!")


def dispatch_to_carrier(carrier_agent, product: BaseProduct, quantity: int):
    """
    Ham dieu phoi van chuyen DOC LAP - Minh hoa Duck Typing.
    
    Ham nay KHONG kiem tra carrier_agent thuoc class nao.
    No chi quan tam: "Doi tuong co phuong thuc ship_package() khong?"
    
    LUU Y: Dispatch la hoat dong BAN GIAO hang cho doi tac van chuyen,
    khong phai xuat kho thong thuong. So luong tru trong kho LA CHINH XAC
    so luong ban giao (khong ap dung 5% hao hut bao quan nhu export_stock).
    
    Edge Case (Bay 4): Neu carrier_agent khong co ship_package(),
    AttributeError se bi bat va thong bao loi ro rang.
    
    Day la suc manh cua Duck Typing: Co the tich hop HANG TRAM
    don vi van chuyen moi (UPS, VNPost, Grab, NinjaVan...)
    ma KHONG CAN SUA MOT DONG CODE NAO trong lop san pham goc.
    """
    try:
        # Duck Typing: Chi can co ship_package() la du
        carrier_agent.ship_package(product, quantity)
        
        # Ban giao hang cho carrier - tru DUNG so luong (khong hao hut)
        product._decrease_stock(quantity)
        
        print(f"Don vi van chuyen da tiep nhan don hang so luong: {quantity} don vi.")
        print(f"So luong ton kho cap nhat: {product.stock_quantity} don vi.")
        
    except AttributeError:
        # Bay 4: Doi tuong khong co phuong thuc ship_package
        print("LOI: Don vi van chuyen khong hop le hoac chua ky ket hop dong ky thuat!")
        print("      (Doi tuong khong co phuong thuc ship_package())")

# ============================================================
#  CLI MENU SYSTEM (He thong Menu)
# ============================================================

def print_header():
    """In tieu de chuong trinh."""
    print("\n" + "=" * 50)
    print("===== AMAZON INVENTORY SIMULATOR PRO =====")
    print("=" * 50)


def print_menu():
    """In menu chuc nang."""
    print("""
1. Dang ky ma hang hoa moi (Chon loai san pham)
2. Xem thong tin & Kiem tra thu tu ke thua (MRO)
3. Giao dich Nhap / Xuat kho (Da hinh)
4. Kiem tra dieu kien bao quan / Tinh chi phi phu troi
5. Kiem tra tinh nang gop lo hang & So sanh ton kho (Overloading)
6. Dieu phoi van chuyen qua Doi tac thu ba (Duck Typing)
7. Thoat chuong trinh
""" + "=" * 50)


def function_1_register(products: list):
    """
    Chuc nang 1: Dang ky ma hang hoa moi.
    Cho phep nguoi dung chon loai san pham va nhap thong tin dang ky.
    """
    print("\n--- CHON LOAI SAN PHAM KHOI TAO ---")
    print("1. Cold Storage Product (Hang Dong Lanh)")
    print("2. Hazardous Product (Hang Nguy Hiem)")
    print("3. Hybrid Premium Product (Hang Lai Cao Cap)")
    
    try:
        product_type = int(input("Chon loai san pham (1-3): ").strip())
    except ValueError:
        print("Loi: Vui long nhap so tu 1 den 3.")
        return None
    
    if product_type not in (1, 2, 3):
        print("Loi: Lua chon khong hop le.")
        return None
    
    # Nhap va validate ma san pham
    product_code = input("Nhap ma san pham 10 ky tu: ").strip()
    if not BaseProduct.validate_product_code(product_code):
        print("Ma san pham khong hop le! Phai gom dung 10 ky tu va bat dau bang chu cai.")
        return None
    
    # Nhap ten san pham
    product_name = input("Nhap ten san pham: ").strip()
    if not product_name:
        print("Loi: Ten san pham khong duoc de trong.")
        return None
    
    new_product = None
    
    try:
        if product_type == 1:
            # Cold Storage
            temp_input = input("Nhap nhiet do bao quan yeu cau (do C): ").strip()
            required_temperature = float(temp_input)
            new_product = ColdStorageProduct(product_code, product_name, required_temperature)
            print("Dang ky san pham Dong Lanh thanh cong!")
            
        elif product_type == 2:
            # Hazardous
            limit_input = input("Nhap han muc luu tru an toan toi da (don vi): ").strip()
            max_safety_limit = int(limit_input)
            if max_safety_limit <= 0:
                print("Loi: Han muc an toan phai lon hon 0.")
                return None
            new_product = HazardousProduct(product_code, product_name, max_safety_limit)
            print("Dang ky san pham Nguy Hiem thanh cong!")
            
        elif product_type == 3:
            # Hybrid Premium
            temp_input = input("Nhap nhiet do bao quan yeu cau (do C): ").strip()
            required_temperature = float(temp_input)
            limit_input = input("Nhap han muc luu tru an toan toi da (don vi): ").strip()
            max_safety_limit = int(limit_input)
            if max_safety_limit <= 0:
                print("Loi: Han muc an toan phai lon hon 0.")
                return None
            new_product = HybridPremiumProduct(
                product_code, product_name, required_temperature, max_safety_limit
            )
            print("Dang ky san pham Hybrid Lai Cao Cap thanh cong!")
        
        print(f"Ten san pham: {new_product.product_name}")
        print(f"Ma san pham: {new_product.product_code}")
        
    except ValueError as e:
        print(f"Loi du lieu dau vao: {e}")
        return None
    
    products.append(new_product)
    return new_product


def function_2_view_info(current_product: BaseProduct, products: list):
    """
    Chuc nang 2: Xem thong tin san pham & Kiem tra MRO.
    Hien thi chi tiet san pham va danh sach Method Resolution Order.
    """
    if current_product is None:
        if not products:
            print("Loi: Chua co san pham nao trong he thong. Vui long dang ky truoc (Chuc nang 1).")
            return None
        # Cho phep chon san pham tu danh sach
        print("\n--- DANH SACH SAN PHAM ---")
        for i, p in enumerate(products, 1):
            print(f"  {i}. {p}")
        try:
            choice = int(input("Chon san pham de xem thong tin (so thu tu): ").strip())
            if 1 <= choice <= len(products):
                current_product = products[choice - 1]
            else:
                print("Loi: Lua chon khong hop le.")
                return None
        except ValueError:
            print("Loi: Vui long nhap so.")
            return None
    
    print("\n--- THONG TIN SAN PHAM HIEN TAI ---")
    
    # Xac dinh loai san pham
    product_type = type(current_product).__name__
    print(f"Loai san pham: {product_type}")
    print(f"Chuoi kho: {BaseProduct.warehouse_name}")
    print(f"Ma san pham: {current_product.product_code}")
    print(f"Ten san pham: {current_product.product_name}")
    print(f"So luong ton kho: {current_product.stock_quantity} don vi")
    
    # Hien thi thong tin dac thu theo loai
    if isinstance(current_product, ColdStorageProduct):
        print(f"Nhiet do yeu cau: {current_product.required_temperature} do C")
    
    if isinstance(current_product, HazardousProduct):
        print(f"Han muc an toan toi da: {current_product.max_safety_limit} don vi")
    
    # Hien thi MRO
    print(f"\n--- METHOD RESOLUTION ORDER (MRO) ---")
    mro_list = type(current_product).__mro__
    for i, cls in enumerate(mro_list):
        print(f"  {i + 1}. {cls.__name__}")
    
    return current_product


def function_3_transaction(current_product: BaseProduct):
    """
    Chuc nang 3: Giao dich Nhap / Xuat kho (Tinh Da hinh - Polymorphism ug).
    
    Cung mot loi goi import_stock() hoac export_stock(), nhung hanh vi
    thuc te se KHAC NHAU tuy thuoc vao loai doi tuong (ColdStorage,
    Hazardous, hay Hybrid). Day chinh la suc manh cua Da hinh.
    """
    if current_product is None:
        print("Loi: Chua chon san pham. Vui long dang ky/xem thong tin truoc.")
        return
    
    print("\n--- GIAO DICH NHAP / XUAT KHO ---")
    print("1. Nhap kho")
    print("2. Xuat kho")
    
    try:
        choice = int(input("Chon giao dich (1-2): ").strip())
    except ValueError:
        print("Loi: Vui long nhap 1 hoac 2.")
        return
    
    if choice not in (1, 2):
        print("Loi: Lua chon khong hop le.")
        return
    
    try:
        quantity = int(input(f"Nhap so luong can {'nhap' if choice == 1 else 'xuat'}: ").strip())
    except ValueError:
        print("Loi: So luong phai la so nguyen.")
        return
    
    try:
        if choice == 1:
            # NHAP KHO - Da hinh: hanh vi thay doi theo loai san pham
            current_product.import_stock(quantity)
            print("Nhap kho thanh cong!")
            print(f"San pham: {current_product.product_name}")
            print(f"So luong nhap: {quantity} don vi")
            print(f"Tong ton kho hien tai: {current_product.stock_quantity} don vi")
        else:
            # XUAT KHO - Da hinh: hanh vi thay doi theo loai san pham
            result = current_product.export_stock(quantity)
            print("Xuat kho thanh cong!")
            
            # Xu ly ket qua tra ve khac nhau giua cac loai
            if isinstance(result, tuple):
                # ColdStorageProduct / HybridPremiumProduct tra ve tuple (qty, loss, total)
                req_qty, loss, total_deduction = result
                print(f"So luong yeu cau: {req_qty} don vi")
                print(f"So luong hao hut bao quan (5%): {loss} don vi")
                print(f"Tong so luong khau tru trong kho: {total_deduction} don vi")
            else:
                # HazardousProduct khong tra ve tuple
                print(f"So luong xuat: {quantity} don vi")
            
            print(f"Tong ton kho con lai: {current_product.stock_quantity} don vi")
    
    except ValueError as e:
        print(f"Giao dich that bai: {e}")
    except Exception as e:
        print(f"Loi khong xac dinh: {e}")


def function_4_cooling_cost(current_product: BaseProduct):
    """
    Chuc nang 4: Kiem tra dieu kien bao quan / Tinh chi phi phu troi.
    
    Chi ap dung cho san pham co tinh chat dong lanh:
    - ColdStorageProduct
    - HybridPremiumProduct
    
    Neu la HazardousProduct thong thuong, bao khong ho tro.
    """
    if current_product is None:
        print("Loi: Chua chon san pham. Vui long dang ky/xem thong tin truoc.")
        return
    
    # Chi ColdStorage va Hybrid moi co tinh nang lam lanh
    if not isinstance(current_product, ColdStorageProduct):
        print("Tinh nang khong ho tro: San pham hien tai khong thuoc nhom hang dong lanh.")
        print("Chi ColdStorageProduct va HybridPremiumProduct moi co chi phi lam lanh.")
        return
    
    print("\n--- TINH PHI BAO QUAN DONG LANH ---")
    print(f"So luong ton kho hien tai: {current_product.stock_quantity} don vi")
    print(f"Nhiet do yeu cau: {current_product.required_temperature} do C")
    
    cost = current_product.apply_cooling_cost()
    print(f"Chi phi lam lanh phat sinh trong ngay: +{cost:,.0f} VND")


def function_5_overloading(current_product: BaseProduct, products: list):
    """
    Chuc nang 5: Gop lo hang & So sanh ton kho (Operator Overloading).
    
    Kiem tra __add__ va __lt__ da duoc nap chong trong BaseProduct.
    """
    if current_product is None:
        print("Loi: Chua chon san pham. Vui long dang ky/xem thong tin truoc.")
        return
    
    # Loc cac san pham KHAC voi san pham hien tai
    other_products = [p for p in products if p is not current_product]
    
    if not other_products:
        print("Loi: Can it nhat 2 san pham trong he thong de thuc hien so sanh/gop lo.")
        print("Vui long dang ky them san pham (Chuc nang 1).")
        return
    
    print("\n--- DONG BO & SO SANH TON KHO (OPERATOR OVERLOADING) ---")
    print(f"San pham hien tai (A): {current_product.product_name} "
          f"(Ton kho: {current_product.stock_quantity} don vi)")
    
    print("\nDanh sach san pham doi ung:")
    for i, p in enumerate(other_products, 1):
        print(f"  {i}. {p.product_code} ({p.product_name} - Ton kho: {p.stock_quantity} don vi)")
    
    try:
        choice = int(input("Chon san pham doi ung (B) tu danh sach: ").strip())
        if not (1 <= choice <= len(other_products)):
            print("Loi: Lua chon khong hop le.")
            return
    except ValueError:
        print("Loi: Vui long nhap so.")
        return
    
    other_product = other_products[choice - 1]
    
    # --- So sanh voi __lt__ ---
    try:
        if current_product < other_product:
            print(f"[Ket qua So sanh (__lt__)]: Ton kho san pham A IT HON ton kho san pham B.")
        elif other_product < current_product:
            print(f"[Ket qua So sanh (__lt__)]: Ton kho san pham A NHIEU HON ton kho san pham B.")
        else:
            print(f"[Ket qua So sanh (__lt__)]: Ton kho san pham A BANG ton kho san pham B.")
    except TypeError:
        print("[Ket qua So sanh]: Khong the so sanh - doi tuong khong tuong thich.")
    
    # --- Cong gop voi __add__ ---
    try:
        total = current_product + other_product
        print(f"[Ket qua Tong hop (__add__)]: Tong so luong ton kho "
              f"cua ca 2 ma san pham la: {total} don vi.")
    except TypeError:
        print("[Ket qua Tong hop]: Khong the cong - doi tuong khong tuong thich.")
    
    # --- Edge Case Demo: Thu cong voi non-BaseProduct ---
    print("\n--- KIEM TRA EDGE CASE: Cong voi kieu du lieu khong tuong thich ---")
    try:
        result = current_product + 100  # Cong voi so nguyen
        print(f"Ket qua: {result}")
    except TypeError:
        print("TypeError duoc nem: Khong the cong BaseProduct voi int.")
        print("=> NotImplemented da hoat dong chinh xac!")


def function_6_dispatch(current_product: BaseProduct):
    """
    Chuc nang 6: Dieu phoi van chuyen qua Doi tac thu ba (Duck Typing).
    
    Minh hoa Duck Typing: Ham dispatch_to_carrier() khong can biet
    carrier_agent la FedExCarrier hay DHLCarrier, chi can co ship_package().
    """
    if current_product is None:
        print("Loi: Chua chon san pham. Vui long dang ky/xem thong tin truoc.")
        return
    
    print("\n--- DIEU PHOI DON VI VAN CHUYEN NGOAI ---")
    print("1. Van chuyen qua doi tac FedEx")
    print("2. Van chuyen qua doi tac DHL")
    print("3. [Edge Case] Kiem tra doi tac khong hop le")
    
    try:
        choice = int(input("Chon doi tac van chuyen (1-3): ").strip())
    except ValueError:
        print("Loi: Vui long nhap so.")
        return
    
    try:
        quantity = int(input("Nhap so luong hang hoa ban giao: ").strip())
        if quantity <= 0:
            print("Loi: So luong phai lon hon 0.")
            return
        if quantity > current_product.stock_quantity:
            print(f"Loi: Khong du ton kho! Hien co: {current_product.stock_quantity}")
            return
    except ValueError:
        print("Loi: So luong phai la so nguyen.")
        return
    
    if choice == 1:
        carrier = FedExCarrier()
        dispatch_to_carrier(carrier, current_product, quantity)
    
    elif choice == 2:
        carrier = DHLCarrier()
        dispatch_to_carrier(carrier, current_product, quantity)
    
    elif choice == 3:
        # Bay 4: Gui mot doi tuong khong co ship_package()
        print("\n[Edge Case] Gui doi tuong khong co phuong thuc ship_package()...")
        
        class InvalidCarrier:
            """Class khong co ship_package - se gay loi AttributeError."""
            pass
        
        invalid_carrier = InvalidCarrier()
        dispatch_to_carrier(invalid_carrier, current_product, quantity)
    
    else:
        print("Loi: Lua chon khong hop le.")


def function_8_edge_case_demo():
    """
    Chuc nang an (go 99): Demo cac Edge Cases.
    """
    print("\n--- DEMO EDGE CASES ---")
    
    # Bay 1: Khoi tao lop truu tuong truc tiep
    print("\n1. Bay 1 - Khoi tao BaseProduct truc tiep:")
    try:
        p = BaseProduct("AMZ0000001", "Test Product")
        print("  -> That bai: Da tao duoc BaseProduct (khong mong doi)!")
    except TypeError as e:
        print(f"  -> TypeError duoc nem (dung mong doi): {e}")
        print("  -> Khong the khoi tao lop truu tuong - Bao ve tinh truu tuong thanh cong!")
    
    # Bay 2: Vuot qua gioi han luu kho an toan
    print("\n2. Bay 2 - Vuot qua gioi han an toan:")
    hp = HazardousProduct("AMZ1111111", "Test Chemical", 100)
    hp.import_stock(80)
    print(f"  -> Da nhap 80 don vi. Ton kho: {hp.stock_quantity}")
    try:
        hp.import_stock(30)  # 80 + 30 = 110 > 100
        print("  -> That bai: Da nhap vuot han muc (khong mong doi)!")
    except ValueError as e:
        print(f"  -> Bi tu choi (dung mong doi): {e}")
    
    # Bay 3: Operator Overloading voi kieu khong tuong thich
    print("\n3. Bay 3 - __add__ voi kieu du lieu khong tuong thich:")
    cp = ColdStorageProduct("AMZ2222222", "Test Frozen", -18)
    cp.import_stock(50)
    
    result = cp.__add__("invalid_string")
    print(f"  -> cp + 'string' tra ve: {result}")
    print("  -> NotImplemented hoat dong chinh xac (Python se nem TypeError neu dung toan tu +)")
    
    # Bay 4: Duck Typing voi doi tuong khong co ship_package
    print("\n4. Bay 4 - Duck Typing voi doi tuong khong hop le:")
    print("  -> (Da demo o Chuc nang 6, lua chon 3)")


# ============================================================
#  MAIN PROGRAM
# ============================================================

def main():
    """
    Ham chinh dieu khien vong lap menu CLI.
    """
    products: list = []           # Danh sach tat ca san pham trong he thong
    current_product = None        # San pham dang duoc chon de thao tac
    
    while True:
        print_header()
        print_menu()
        
        try:
            choice = input("Chon chuc nang (1-7): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCam on da su dung he thong Amazon Inventory Simulator Pro!")
            break
        
        if choice == "1":
            new_product = function_1_register(products)
            if new_product:
                current_product = new_product
                print(f"\n[Da tu dong chon san pham '{new_product.product_name}' lam san pham hien tai]")
        
        elif choice == "2":
            result = function_2_view_info(current_product, products)
            if result is not None:
                current_product = result
        
        elif choice == "3":
            function_3_transaction(current_product)
        
        elif choice == "4":
            function_4_cooling_cost(current_product)
        
        elif choice == "5":
            function_5_overloading(current_product, products)
        
        elif choice == "6":
            function_6_dispatch(current_product)
        
        elif choice == "7":
            print("\nCam on da su dung he thong Amazon Inventory Simulator Pro!")
            break
        
        elif choice == "99":
            # Chuc nang an: Demo Edge Cases
            function_8_edge_case_demo()
        
        else:
            print("Loi: Vui long chon tu 1 den 7.")
        
        input("\nNhan Enter de tiep tuc...")


if __name__ == "__main__":
    main()
