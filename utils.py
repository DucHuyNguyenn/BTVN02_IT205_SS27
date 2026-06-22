# -*- coding: utf-8 -*-
"""
utils.py
---------
Các hàm tiện ích dùng chung cho toàn hệ thống.
"""


def parse_int(text):
    """
    Chuyển chuỗi người dùng nhập (có thể có dấu phẩy phân cách) thành số
    nguyên (int). Ném ValueError nếu chuỗi không hợp lệ.
    """
    cleaned = text.replace(",", "").strip()
    if not cleaned.lstrip("-").isdigit():
        raise ValueError("Số lượng không hợp lệ, vui lòng chỉ nhập số nguyên.")
    return int(cleaned)
