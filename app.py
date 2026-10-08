import streamlit as st
from datetime import datetime
import pandas as pd
import io

# =========================
# CẤU HÌNH
# =========================
st.set_page_config(
    page_title="Quản lý Bill Trà Sữa",
    page_icon="🧋",
    layout="wide"
)

# =========================
# DỮ LIỆU MENU
# =========================
MENU = {
    "Trà sữa truyền thống": 30000,
    "Trà sữa matcha": 35000,
    "Trà sữa socola": 35000,
    "Trà sữa khoai môn": 35000,
    "Trà sữa dâu": 35000,
    "Trà đào": 30000,
    "Trà vải": 30000,
    "Trà chanh": 25000,
    "Matcha latte": 40000,
    "Socola đá xay": 45000,
}

SIZE_PRICE = {
    "M": 0,
    "L": 5000,
    "XL": 10000
}

TOPPING_PRICE = {
    "Không topping": 0,
    "Trân châu đen": 5000,
    "Trân châu trắng": 5000,
    "Thạch dừa": 5000,
    "Thạch trái cây": 5000,
    "Pudding trứng": 7000,
    "Kem cheese": 10000,
}

SUGAR_LEVEL = [
    "0% - Không đường",
    "30%",
    "50%",
    "70%",
    "100%"
]

ICE_LEVEL = [
    "0% - Không đá",
    "30%",
    "50%",
    "70%",
    "100%"
]

# =========================
# HÀM ĐỊNH DẠNG TIỀN
# =========================
def format_money(number):
    return f"{number:,.0f} đ".replace(",", ".")


# =========================
# KHỞI TẠO SESSION
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "paid" not in st.session_state:
    st.session_state.paid = False

if "invoice" not in st.session_state:
    st.session_state.invoice = None


# =========================
# HEADER
# =========================
st.title("🧋 QUẢN LÝ BILL QUÁN TRÀ SỮA")
st.caption("Tạo đơn hàng • Tính tiền • Thanh toán • Xuất hóa đơn")

st.divider()


# =========================
# THÔNG TIN KHÁCH HÀNG
# =========================
st.subheader("👤 Thông tin khách hàng")

col1, col2 = st.columns(2)

with col1:
    customer_name = st.text_input(
        "Tên khách hàng",
        placeholder="Nhập tên khách hàng..."
    )

with col2:
    customer_phone = st.text_input(
        "Số điện thoại",
        placeholder="Không bắt buộc"
    )


st.divider()


# =========================
# THÊM MÓN
# =========================
st.subheader("🧋 Thêm món")

col1, col2 = st.columns(2)

with col1:
    drink = st.selectbox(
        "Loại trà sữa / thức uống",
        list(MENU.keys())
    )

    size = st.selectbox(
        "Size",
        list(SIZE_PRICE.keys())
    )

    topping = st.selectbox(
        "Topping",
        list(TOPPING_PRICE.keys())
    )

with col2:
    sugar = st.selectbox(
        "Mức độ đường",
        SUGAR_LEVEL
    )

    ice = st.selectbox(
        "Mức độ đá",
        ICE_LEVEL
    )

    quantity = st.number_input(
        "Số lượng",
        min_value=1,
        max_value=50,
        value=1,
        step=1
    )


# =========================
# TÍNH GIÁ MÓN
# =========================
base_price = MENU[drink]
size_price = SIZE_PRICE[size]
topping_price = TOPPING_PRICE[topping]

unit_price = base_price + size_price + topping_price
total_item = unit_price * quantity


st.info(
    f"💰 Đơn giá: **{format_money(unit_price)}** | "
    f"Thành tiền: **{format_money(total_item)}**"
)


if st.button("➕ THÊM MÓN VÀO HÓA ĐƠN", use_container_width=True):

    item = {
        "Tên món": drink,
        "Size": size,
        "Topping": topping,
        "Đường": sugar,
        "Đá": ice,
        "SL": quantity,
        "Đơn giá": unit_price,
        "Thành tiền": total_item
    }

    st.session_state.cart.append(item)

    st.success(f"Đã thêm {quantity} x {drink} vào hóa đơn!")


st.divider()


# =========================
# GIỎ HÀNG
# =========================
st.subheader("🛒 Danh sách món trong hóa đơn")

if len(st.session_state.cart) == 0:

    st.warning("Chưa có món nào trong hóa đơn.")

else:

    for i, item in enumerate(st.session_state.cart):

        col1, col2, col3 = st.columns([6, 2, 1])

        with col1:
            st.write(
                f"**{i + 1}. {item['Tên món']} - Size {item['Size']}**"
            )

            st.caption(
                f"Topping: {item['Topping']} | "
                f"Đường: {item['Đường']} | "
                f"Đá: {item['Đá']}"
            )

        with col2:
            st.write(
                f"{item['SL']} × {format_money(item['Đơn giá'])}"
            )

            st.write(
                f"**{format_money(item['Thành tiền'])}**"
            )

        with col3:
            if st.button("🗑️", key=f"delete_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()

        st.divider()


# =========================
# TỔNG TIỀN
# =========================
subtotal = sum(
    item["Thành tiền"]
    for item in st.session_state.cart
)

col1, col2 = st.columns(2)

with col1:
    discount = st.number_input(
        "Giảm giá (VNĐ)",
        min_value=0,
        value=0,
        step=1000
    )

with col2:
    tax_percent = st.number_input(
        "Thuế VAT (%)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=1.0
    )


after_discount = max(subtotal - discount, 0)

tax = after_discount * tax_percent / 100

grand_total = after_discount + tax


st.markdown("### 💰 TỔNG THANH TOÁN")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Tạm tính",
        format_money(subtotal)
    )

with c2:
    st.metric(
        "Giảm giá",
        format_money(discount)
    )

with c3:
    st.metric(
        f"VAT {tax_percent:.0f}%",
        format_money(tax)
    )

with c4:
    st.metric(
        "THÀNH TIỀN",
        format_money(grand_total)
    )


st.divider()


# =========================
# THANH TOÁN
# =========================
st.subheader("💳 Thanh toán")

payment_method = st.radio(
    "Phương thức thanh toán",
    ["💵 Tiền mặt", "💳 Chuyển khoản", "📱 Ví điện tử"],
    horizontal=True
)

if payment_method == "💵 Tiền mặt":

    money_received = st.number_input(
        "Tiền khách đưa",
        min_value=0,
        value=0,
        step=10000
    )

    change = money_received - grand_total

    if money_received > 0:

        if change >= 0:
            st.success(
                f"💵 Tiền thừa: **{format_money(change)}**"
            )
        else:
            st.error(
                f"⚠️ Khách còn thiếu: "
                f"**{format_money(abs(change))}**"
            )


# =========================
# TẠO HÓA ĐƠN
# =========================
if st.button(
    "✅ THANH TOÁN & TẠO HÓA ĐƠN",
    type="primary",
    use_container_width=True
):

    if not customer_name.strip():
        st.error("Vui lòng nhập tên khách hàng.")

    elif len(st.session_state.cart) == 0:
        st.error("Vui lòng thêm ít nhất một món.")

    elif payment_method == "💵 Tiền mặt" and money_received < grand_total:
        st.error("Số tiền khách đưa chưa đủ.")

    else:

        invoice_time = datetime.now()

        invoice_number = invoice_time.strftime(
            "HD%Y%m%d%H%M%S"
        )

        change_money = 0

        if payment_method == "💵 Tiền mặt":
            change_money = money_received - grand_total

        invoice = {
            "invoice_number": invoice_number,
            "time": invoice_time.strftime("%d/%m/%Y %H:%M:%S"),
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "items": st.session_state.cart.copy(),
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "tax_percent": tax_percent,
            "total": grand_total,
            "payment_method": payment_method,
            "money_received": money_received
            if payment_method == "💵 Tiền mặt"
            else grand_total,
            "change": change_money
        }

        st.session_state.invoice = invoice
        st.session_state.paid = True

        st.success(
            f"🎉 Thanh toán thành công! Mã hóa đơn: **{invoice_number}**"
        )


# =========================
# HIỂN THỊ HÓA ĐƠN
# =========================
if st.session_state.paid and st.session_state.invoice:

    invoice = st.session_state.invoice

    st.divider()

    st.subheader("🧾 HÓA ĐƠN")

    invoice_text = ""

    invoice_text += "================================\n"
    invoice_text += "       QUÁN TRÀ SỮA\n"
    invoice_text += "================================\n"
    invoice_text += f"Mã hóa đơn: {invoice['invoice_number']}\n"
    invoice_text += f"Thời gian: {invoice['time']}\n"
    invoice_text += f"Khách hàng: {invoice['customer_name']}\n"

    if invoice["customer_phone"]:
        invoice_text += f"SĐT: {invoice['customer_phone']}\n"

    invoice_text += "--------------------------------\n"

    for i, item in enumerate(invoice["items"]):

        invoice_text += (
            f"{i + 1}. {item['Tên món']} "
            f"(Size {item['Size']})\n"
        )

        invoice_text += (
            f"   Topping: {item['Topping']}\n"
            f"   Đường: {item['Đường']}\n"
            f"   Đá: {item['Đá']}\n"
            f"   SL: {item['SL']} x "
            f"{format_money(item['Đơn giá'])}\n"
            f"   Thành tiền: "
            f"{format_money(item['Thành tiền'])}\n"
        )

    invoice_text += "--------------------------------\n"
    invoice_text += (
        f"Tạm tính: {format_money(invoice['subtotal'])}\n"
    )
    invoice_text += (
        f"Giảm giá: {format_money(invoice['discount'])}\n"
    )
    invoice_text += (
        f"VAT: {format_money(invoice['tax'])}\n"
    )
    invoice_text += (
        f"TỔNG CỘNG: {format_money(invoice['total'])}\n"
    )
    invoice_text += "--------------------------------\n"
    invoice_text += (
        f"Thanh toán: {invoice['payment_method']}\n"
    )

    if invoice["payment_method"] == "💵 Tiền mặt":
        invoice_text += (
            f"Khách đưa: "
            f"{format_money(invoice['money_received'])}\n"
        )

        invoice_text += (
            f"Tiền thừa: "
            f"{format_money(invoice['change'])}\n"
        )

    invoice_text += "================================\n"
    invoice_text += "       CẢM ƠN QUÝ KHÁCH!\n"
    invoice_text += "================================\n"

    # Hiển thị hóa đơn
    st.code(invoice_text, language="text")


    # =========================
    # XUẤT CSV
    # =========================
    export_data = []

    for item in invoice["items"]:

        export_data.append({
            "Mã hóa đơn": invoice["invoice_number"],
            "Thời gian": invoice["time"],
            "Khách hàng": invoice["customer_name"],
            "Số điện thoại": invoice["customer_phone"],
            "Tên món": item["Tên món"],
            "Size": item["Size"],
            "Topping": item["Topping"],
            "Đường": item["Đường"],
            "Đá": item["Đá"],
            "Số lượng": item["SL"],
            "Đơn giá": item["Đơn giá"],
            "Thành tiền": item["Thành tiền"],
            "Tổng hóa đơn": invoice["total"],
            "Thanh toán": invoice["payment_method"]
        })

    df = pd.DataFrame(export_data)

    csv_data = df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        label="📥 XUẤT HÓA ĐƠN CSV",
        data=csv_data,
        file_name=f"{invoice['invoice_number']}.csv",
        mime="text/csv",
        use_container_width=True
    )


    # =========================
    # TẠO FILE TXT
    # =========================
    txt_bytes = invoice_text.encode("utf-8")

    st.download_button(
        label="📄 TẢI HÓA ĐƠN TXT",
        data=txt_bytes,
        file_name=f"{invoice['invoice_number']}.txt",
        mime="text/plain",
        use_container_width=True
    )


# =========================
# NÚT TẠO HÓA ĐƠN MỚI
# =========================
if st.session_state.cart:

    st.divider()

    if st.button(
        "🔄 TẠO HÓA ĐƠN MỚI",
        use_container_width=True
    ):

        st.session_state.cart = []
        st.session_state.paid = False
        st.session_state.invoice = None

        st.rerun()


# =========================
# FOOTER
# =========================
st.divider()

st.caption(
    "🧋 Milk Tea POS • Ứng dụng quản lý hóa đơn trà sữa bằng Streamlit"
)
