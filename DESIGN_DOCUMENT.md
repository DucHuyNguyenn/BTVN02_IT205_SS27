# Tài Liệu Phân Tích & Thiết Kế Giải Pháp
## Hệ Thống Quản Lý Kho Hàng Thông Minh Amazon Logistics — Amazon Inventory Simulator Pro

## 1. Sơ đồ kiến trúc & phân cấp kế thừa

```
                          ┌────────────────────────┐
                          │     BaseProduct (ABC)   │
                          │  - warehouse_name        │
                          │  - base_storage_fee      │
                          │  - __stock_quantity      │
                          │  + stock_quantity (property)│
                          │  + import_stock()  (abstract)│
                          │  + export_stock()  (abstract)│
                          │  + __add__ / __lt__      │
                          │  + validate_product_code() (static)│
                          │  + update_warehouse_name() (classmethod)│
                          └────────────┬─────────────┘
                    ┌──────────────────┴───────────────────┐
                    │                                       │
          ┌─────────▼──────────┐                  ┌─────────▼──────────┐
          │ ColdStorageProduct  │                  │  HazardousProduct   │
          │ - required_temperature│                │ - max_safety_limit  │
          │ + import_stock()    │                  │ + import_stock()    │
          │   (bình thường)      │                  │   (chặn vượt hạn mức)│
          │ + export_stock()    │                  │ + export_stock()    │
          │   (hao hụt 5%)       │                  │   (bình thường)      │
          │ + apply_cooling_cost()│                 └─────────┬──────────┘
          └─────────┬──────────┘                              │
                    │         (đa kế thừa kiểu "diamond")      │
                    └───────────────────┬──────────────────────┘
                              ┌─────────▼──────────┐
                              │ HybridPremiumProduct │
                              │ (kế thừa CẢ 2 nhánh) │
                              │ override import/export│
                              │ để giải quyết xung đột│
                              └───────────────────────┘
```

`BaseProduct` là bộ khung chuẩn, quy định mọi sản phẩm trong kho bắt buộc phải đóng gói số lượng tồn kho (`__stock_quantity` private, chỉ đọc qua `property stock_quantity`), bắt buộc phải tự định nghĩa `import_stock()` và `export_stock()` (abstract methods), và được trang bị sẵn 2 toán tử nạp chồng (`__add__`, `__lt__`) cùng 1 static method và 1 class method dùng chung toàn hệ thống.

`ColdStorageProduct` và `HazardousProduct` là hai nhánh kế thừa đơn trực tiếp từ `BaseProduct`, mỗi lớp override `import_stock()`/`export_stock()` theo nghiệp vụ riêng (đông lạnh hao hụt 5% khi xuất; nguy hiểm chặn nhập nếu vượt hạn mức an toàn).

`HybridPremiumProduct` là điểm đặc biệt của bài toán này: nó kế thừa kiểu "hình thoi" (diamond inheritance) từ CẢ HAI lớp `ColdStorageProduct` và `HazardousProduct` — hai lớp này lại cùng có một tổ tiên chung là `BaseProduct`. Đây chính là cấu trúc đa kế thừa phức tạp nhất trong hệ thống, đòi hỏi xử lý kỹ cả ở `__init__` (khởi tạo) và ở các phương thức bị trùng tên (`import_stock`, `export_stock`).

## 2. Báo cáo kỹ thuật

### 2.1. MRO của HybridPremiumProduct & cách giải quyết xung đột phương thức trùng tên

Khai báo `class HybridPremiumProduct(ColdStorageProduct, HazardousProduct)` khiến Python dựng MRO theo giải thuật C3-linearization:

```
HybridPremiumProduct -> ColdStorageProduct -> HazardousProduct -> BaseProduct -> ABC -> object
```

**Vấn đề xung đột:** cả `ColdStorageProduct` và `HazardousProduct` đều định nghĩa `import_stock()` và `export_stock()` với hành vi khác nhau. Nếu `HybridPremiumProduct` không tự override hai phương thức này, Python sẽ tra cứu theo đúng MRO và luôn chọn phiên bản của `ColdStorageProduct` trước (vì lớp này đứng trước `HazardousProduct` trong danh sách MRO) — tức là khi gọi `hybrid_obj.import_stock()`, hệ thống sẽ nhập kho "bình thường" mà KHÔNG kiểm tra hạn mức an toàn. Điều này vi phạm nghiêm trọng yêu cầu nghiệp vụ (Bẫy 2 phải áp dụng cho cả Hybrid).

**Giải pháp:** dự án này override rõ ràng cả hai phương thức ngay tại `HybridPremiumProduct`, và bên trong đó KHÔNG dùng `super()` (vì `super()` vẫn đi theo MRO tuyến tính, không giải quyết được việc "trộn" hành vi của cả hai lớp cha), mà gọi đích danh class mong muốn:

```python
def import_stock(self, quantity):
    return HazardousProduct.import_stock(self, quantity)   # áp dụng kiểm tra an toàn

def export_stock(self, quantity):
    return ColdStorageProduct.export_stock(self, quantity)  # áp dụng hao hụt 5%
```

Nhờ vậy, `HybridPremiumProduct` chủ động chọn đúng hành vi cần thiết cho từng phương thức, thay vì để MRO tự quyết định một cách "mặc định" và sai nghiệp vụ.

**Vấn đề thứ hai — khởi tạo (`__init__`) hợp tác (cooperative multiple inheritance):** `HybridPremiumProduct` cần cả `required_temperature` (từ `ColdStorageProduct`) và `max_safety_limit` (từ `HazardousProduct`) được khởi tạo đầy đủ. Dự án áp dụng kỹ thuật "cooperative `super()` với `**kwargs`": mỗi lớp `__init__` chỉ xử lý tham số của riêng mình rồi chuyển tiếp phần còn lại qua `super().__init__(**kwargs)`. Vì lệnh `super()` luôn bám theo MRO của lớp thực thể được tạo ra (`HybridPremiumProduct`, không phải lớp đang viết code), nên khi `HybridPremiumProduct.__init__` gọi `super().__init__(...)`, lệnh này sẽ lần lượt đi qua: `ColdStorageProduct.__init__` (gán `required_temperature`) → `HazardousProduct.__init__` (gán `max_safety_limit`, KHÔNG phải gọi trực tiếp `BaseProduct` dù `ColdStorageProduct` "tưởng" mình đang gọi lớp cha của chính nó) → cuối cùng `BaseProduct.__init__` (gán các thuộc tính gốc). Toàn bộ chuỗi này chỉ cần một lệnh `super().__init__()` duy nhất ở `HybridPremiumProduct`, minh chứng rõ MRO không chỉ ảnh hưởng đến tra cứu phương thức thông thường mà còn quyết định toàn bộ trình tự khởi tạo trong đa kế thừa.

### 2.2. Vì sao Duck Typing giúp mở rộng hàng trăm đơn vị vận chuyển mà không cần sửa code gốc

Hàm `dispatch_to_carrier(carrier_agent, product, quantity)` không kiểm tra `isinstance(carrier_agent, SomeBaseCarrierClass)` và không yêu cầu các đối tác vận chuyển phải kế thừa từ một interface chung. Điều duy nhất hàm này quan tâm là đối tượng truyền vào có sẵn phương thức `ship_package(product, quantity)` hay không — triết lý Duck Typing: "nếu nó đi như con vịt, kêu như con vịt, thì nó là con vịt".

Nhờ vậy, khi Amazon Logistics muốn tích hợp thêm đối tác mới (Ninja Van, J&T Express, GHN...), kỹ sư chỉ cần viết một lớp mới có `ship_package()` đúng chữ ký — hoàn toàn độc lập, không đụng đến `BaseProduct`, không đụng đến `dispatch_to_carrier()`, không đụng đến bất kỳ lớp sản phẩm nào đã tồn tại. Đây là nguyên lý Open/Closed (mở để mở rộng, đóng để sửa đổi) áp dụng qua Duck Typing thay vì qua kế thừa/interface cứng nhắc: hệ thống mở rộng được vô hạn số lượng đối tác vận chuyển mới với rủi ro phá vỡ code cũ gần như bằng không, vì không tồn tại điểm phụ thuộc chung (tight coupling) giữa các đối tác vận chuyển và lớp sản phẩm gốc.

## 3. Xử lý các bẫy dữ liệu (Edge Cases)

| Bẫy | Vị trí xử lý | Cơ chế |
|---|---|---|
| 1. Khởi tạo trực tiếp `BaseProduct` | `product_models.py` | Tự động: `ABCMeta` ném `TypeError` ngay khi gọi `BaseProduct(...)` vì lớp còn chứa `@abstractmethod` chưa triển khai |
| 2. Vượt giới hạn lưu kho an toàn | `HazardousProduct.import_stock()` (và được `HybridPremiumProduct.import_stock()` tái sử dụng đích danh) | Kiểm tra `stock_quantity + quantity > max_safety_limit` trước khi cộng, nếu vượt thì `raise ValueError(...)` |
| 3. Cộng/so sánh với kiểu dữ liệu sai | `BaseProduct.__add__` / `__lt__` | Kiểm tra `isinstance(other, BaseProduct)`, nếu sai kiểu thì `return NotImplemented` để Python tự chuyển thành `TypeError` chuẩn |
| 4. Đối tác vận chuyển thiếu `ship_package` | `carrier_partner.dispatch_to_carrier()` | Bọc `try...except AttributeError`, in thông báo "Đơn vị vận chuyển không hợp lệ hoặc chưa ký kết hợp đồng kỹ thuật" |

## 4. Cấu trúc module của dự án

Để dễ quản lý và sửa lỗi độc lập, code được chia thành các module sau (mỗi tính năng menu ứng với một file riêng):

- `product_models.py` — toàn bộ các lớp sản phẩm (BaseProduct, ColdStorageProduct, HazardousProduct, HybridPremiumProduct).
- `carrier_partner.py` — các lớp đối tác vận chuyển (FedExCarrier, DHLCarrier) và hàm `dispatch_to_carrier()`.
- `utils.py` — hàm tiện ích dùng chung (parse số lượng nguyên).
- `feature_register_product.py` — Chức năng 1.
- `feature_view_info.py` — Chức năng 2.
- `feature_transaction.py` — Chức năng 3.
- `feature_cooling_cost.py` — Chức năng 4.
- `feature_compare_merge.py` — Chức năng 5.
- `feature_dispatch.py` — Chức năng 6.
- `main.py` — chương trình chính, chỉ chứa menu CLI và import/gọi các module feature ở trên; quản lý state chung `products` (list) và `current_product`.
