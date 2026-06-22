# -*- coding: utf-8 -*-
"""
feature_compare_merge.py
---------------------------
Chức năng 5: Kiểm tra tính năng gộp lô hàng & so sánh tồn kho (Operator Overloading).

Sử dụng __lt__ (so sánh tồn kho bằng toán tử <) và __add__ (gộp tồn kho
bằng toán tử +) đã được nạp chồng trong BaseProduct.
"""


def feature5_compare_merge(products, current_product):
    if current_product is None:
        print("\nVui lòng đăng ký/chọn sản phẩm hiện tại trước (Chức năng 1).")
        return

    others = [p for p in products if p is not current_product]
    if not others:
        print("\nHệ thống chưa có sản phẩm khác để so sánh/gộp tồn kho.")
        return

    print("\n--- ĐỒNG BỘ & SO SÁNH TỒN KHO (OPERATOR OVERLOADING) ---")
    print(f"Sản phẩm hiện tại (A): {current_product.product_name} (Tồn kho: {current_product.stock_quantity:g} đơn vị)")
    print("Danh sách sản phẩm khác trong hệ thống:")
    for idx, p in enumerate(others, start=1):
        print(f"{idx}. {p.product_code} - {p.product_name} (Tồn kho: {p.stock_quantity:g} đơn vị)")

    choice = input("Chọn sản phẩm đối ứng (B) theo số thứ tự: ").strip()
    try:
        target = others[int(choice) - 1]
    except (ValueError, IndexError):
        print("Lựa chọn không hợp lệ!")
        return

    print(f"Sản phẩm đối ứng (B): {target.product_name} (Tồn kho: {target.stock_quantity:g} đơn vị)")

    # --- Toán tử __lt__ (Bẫy 3: nếu kiểu không hợp lệ, Python sẽ tự ném
    # TypeError vì __lt__ trả về NotImplemented khi không phải BaseProduct) ---
    try:
        if current_product < target:
            print("[Kết quả So sánh (__lt__)]: Tồn kho sản phẩm A ÍT HƠN tồn kho sản phẩm B.")
        else:
            print("[Kết quả So sánh (__lt__)]: Tồn kho sản phẩm A NHIỀU HƠN HOẶC BẰNG tồn kho sản phẩm B.")
    except TypeError:
        print("[Kết quả So sánh (__lt__)]: Không thể so sánh (kiểu dữ liệu không hợp lệ).")

    # --- Toán tử __add__ ---
    try:
        total = current_product + target
        print(f"[Kết quả Tổng hợp (__add__)]: Tổng số lượng tồn kho của cả 2 mã sản phẩm là: {total:g} đơn vị.")
    except TypeError:
        print("[Kết quả Tổng hợp (__add__)]: Không thể cộng (kiểu dữ liệu không hợp lệ).")
