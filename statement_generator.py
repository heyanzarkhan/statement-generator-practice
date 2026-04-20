#!/usr/bin/env python3
"""Mock bank statement PDF generator for practice/demo use."""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas


# Separate reusable arrays for realistic combinations.
NAME_GROUP_PERSONAL = [
    "Rohan Patel",
    "Aisha Khan",
    "Mohammed Arif",
    "Abdul Rahman",
    "Neha Verma",
    "Vikram Singh",
    "Ishita Sharma",
    "Imran Shaikh",
    "Arjun Nair",
    "Saba Fatima",
    "Priya Desai",
    "Kabir Mehta",
    "Sajid Ali",
    "Sneha Iyer",
    "Aditya Rao",
    "Ananya Gupta",
    "Mohit Bansal",
    "Sana Sheikh",
    "Yusuf Qureshi",
    "Amina Siddiqui",
    "Rahul Joshi",
    "Pooja Kulkarni",
    "Nida Parveen",
    "Aman Yadav",
    "Faizan Ansari",
    "Karan Malhotra",
    "Tanvi Shah",
    "Nikhil Arora",
    "Rehan Memon",
    "Zoya Khan",
    "Maya Menon",
    "Mustafa Lokhandwala",
    "Nausheen Bano",
    "Anzar Khan"
    "Anzar Khan"
]

UPI_HANDLE_GROUP = [
    "okhdfcbank",
    "oksbi",
    "okicici",
    "ibl",
    "paytm",
    "ybl",
    "axl",
    "upi",
]

VENDOR_GROUP_LOCAL = [
    "Essbee Petro",
    "Shree Ganesh Mart",
    "City Medical",
    "Rangrej Vasimak",
    "Fresh Basket",
    "Metro Pharmacy",
    "Blue Tokai",
    "Daily Needs Store",
    "Urban Bazaar",
    "Royal Fuel Point",
]

ONLINE_SHOPPING_GROUP = [
    "AMAZON PAY INDIA",
    "FLIPKART INTERNET",
    "MYNTRA DESIGNS",
    "AJIO ONLINE",
    "SWIGGY INSTAMART",
    "ZEPTO ONLINE",
    "BIGBASKET",
    "NYKAA ECOM",
]

CARD_USAGE_GROUP = [
    "DMART",
    "RELIANCE SMART",
    "PVR CINEMAS",
    "IRCTC",
    "UBER INDIA",
    "OLA CABS",
    "APOLLO PHARMACY",
    "CROMA STORE",
    "DECATHLON",
    "ZOMATO",
]

EMPLOYER_GROUP = [
    "ZENITH TECH PVT LTD",
    "NOVA ANALYTICS LLP",
    "SKYLINE DIGITAL",
]

BILLER_GROUP = [
    "Airtel Postpaid",
    "Jio Fiber",
    "BESCOM Electricity",
    "HDFC Credit Card",
    "FASTag Recharge",
]

CITY_GROUP = ["AHMEDABAD"]

POOLS: Dict[str, List[str]] = {
    "names": NAME_GROUP_PERSONAL,
    "upi_handles": UPI_HANDLE_GROUP,
    "vendors": VENDOR_GROUP_LOCAL,
    "online_shops": ONLINE_SHOPPING_GROUP,
    "card_merchants": CARD_USAGE_GROUP,
    "employers": EMPLOYER_GROUP,
    "billers": BILLER_GROUP,
    "cities": CITY_GROUP,
}


@dataclass
class Txn:
    serial: int
    date: datetime
    description: str
    ref_no: str
    debit: Optional[float]
    credit: Optional[float]
    balance: float


def compact_name(name: str) -> str:
    return " ".join(name.upper().split())


def random_mobile(rng: random.Random) -> str:
    return "".join(rng.choices("6789", k=1) + rng.choices("0123456789", k=9))


def random_upi_id(rng: random.Random) -> str:
    raw_name = rng.choice(POOLS["names"]).lower().replace(" ", "")
    handle = rng.choice(POOLS["upi_handles"])
    return f"{raw_name[:8]}{rng.randint(10, 99)}@{handle}"


def random_ref(rng: random.Random, prefix: str) -> str:
    return f"{prefix}-{rng.randint(6052000000000, 6059999999999)}"


def choose_amount(rng: random.Random, kind: str) -> float:
    if kind == "salary_fixed":
        return round(rng.uniform(23000, 25000), 2)
    if kind == "upi_credit":
        return round(rng.uniform(250, 4500), 2)
    if kind == "interest":
        return round(rng.uniform(20, 180), 2)
    if kind == "cashback":
        return round(rng.uniform(10, 220), 2)
    if kind == "atm":
        return float(rng.choice([500, 1000, 1500, 2000, 3000, 5000]))
    if kind == "card":
        return round(rng.uniform(90, 5000), 2)
    if kind == "bill":
        return round(rng.uniform(260, 7000), 2)
    if kind == "ecom":
        return round(rng.uniform(180, 10000), 2)
    return round(rng.uniform(20, 3500), 2)


def choose_ecom_amount(rng: random.Random, merchant: str) -> float:
    ranges = {
        "ZEPTO ONLINE": (120, 1800),
        "SWIGGY INSTAMART": (140, 2200),
        "BIGBASKET": (300, 3200),
        "AMAZON PAY INDIA": (250, 7000),
        "FLIPKART INTERNET": (350, 9000),
        "MYNTRA DESIGNS": (400, 6000),
        "AJIO ONLINE": (350, 5500),
        "NYKAA ECOM": (250, 4500),
    }
    low, high = ranges.get(merchant, (180, 5000))
    return round(rng.uniform(low, high), 2)


def choose_card_amount(rng: random.Random, merchant: str) -> float:
    ranges = {
        "OLA CABS": (90, 900),
        "UBER INDIA": (100, 1200),
        "PVR CINEMAS": (200, 1800),
        "DMART": (350, 4200),
        "RELIANCE SMART": (250, 3500),
        "IRCTC": (220, 4500),
        "APOLLO PHARMACY": (120, 2200),
        "CROMA STORE": (900, 5000),
        "DECATHLON": (350, 3600),
        "ZOMATO": (120, 1500),
    }
    low, high = ranges.get(merchant, (90, 3200))
    return round(rng.uniform(low, high), 2)


def make_transaction_payload(rng: random.Random, date: datetime) -> Tuple[str, str, Optional[float], Optional[float], str]:
    # Outgoing-heavy mix (incoming intentionally less frequent).
    tx_type = rng.choices(
        [
            "upi_debit",
            "card",
            "atm",
            "bill",
            "ecom",
            "upi_credit",
            "interest",
            "cashback",
        ],
        weights=[42, 16, 8, 12, 12, 7, 1, 2],
        k=1,
    )[0]

    if tx_type == "upi_debit":
        receiver = compact_name(rng.choice(POOLS["names"] + POOLS["vendors"]))
        desc = f"UPI/{receiver}/{random_mobile(rng)}/UPI/{random_upi_id(rng)}"
        if rng.random() < 0.15:
            desc += f" (Value Date: {(date + timedelta(days=1)).strftime('%d-%m-%Y')})"
        return desc, random_ref(rng, "UPI"), choose_amount(rng, "upi"), None, tx_type

    if tx_type == "upi_credit":
        sender = compact_name(rng.choice(POOLS["names"]))
        desc = f"UPI/{sender}/{random_mobile(rng)}/UPI/{random_upi_id(rng)}"
        return desc, random_ref(rng, "UPI"), None, choose_amount(rng, "upi_credit"), tx_type

    if tx_type == "card":
        merchant = rng.choice(POOLS["card_merchants"])
        desc = f"CARD/POS/{merchant}/{rng.randint(1000, 9999)}/{date.strftime('%d%m%y')}"
        return desc, random_ref(rng, "POS"), choose_card_amount(rng, merchant), None, tx_type

    if tx_type == "atm":
        desc = f"ATM CASH WDL/{rng.choice(POOLS['cities'])}/{rng.randint(1000, 9999)}"
        return desc, random_ref(rng, "ATM"), choose_amount(rng, "atm"), None, tx_type

    if tx_type == "bill":
        desc = f"BILLPAY/{rng.choice(POOLS['billers']).upper()}/ONLINE"
        return desc, random_ref(rng, "BIL"), choose_amount(rng, "bill"), None, tx_type

    if tx_type == "ecom":
        merchant = rng.choice(POOLS["online_shops"])
        desc = f"ECOM/{merchant}/{rng.randint(100000, 999999)}"
        return desc, random_ref(rng, "ECM"), choose_ecom_amount(rng, merchant), None, tx_type

    if tx_type == "cashback":
        desc = "CARD CASHBACK CREDIT/MONTHLY BENEFIT"
        return desc, random_ref(rng, "CBK"), None, choose_amount(rng, "cashback"), tx_type

    desc = "INTEREST CREDIT/SAVINGS ACCOUNT"
    return desc, random_ref(rng, "INT"), None, choose_amount(rng, "interest"), tx_type


def split_text_by_width(text: str, font_name: str, font_size: float, max_width: float, max_lines: int = 3) -> List[str]:
    words = text.split()
    if not words:
        return [""]

    lines: List[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
            if len(lines) >= max_lines - 1:
                break

    if len(lines) < max_lines:
        lines.append(current)

    # Truncate the last line if still too wide.
    if pdfmetrics.stringWidth(lines[-1], font_name, font_size) > max_width:
        base = lines[-1]
        while base and pdfmetrics.stringWidth(base + "...", font_name, font_size) > max_width:
            base = base[:-1]
        lines[-1] = (base + "...") if base else "..."

    return lines[:max_lines]


def generate_transactions(
    start_date: datetime,
    end_date: datetime,
    opening_balance: float,
    start_serial: int,
    seed: int,
    max_balance: float,
    max_txn_per_day: int,
) -> List[Txn]:
    rng = random.Random(seed)
    txns: List[Txn] = []
    balance = round(min(opening_balance, max_balance), 2)
    serial = start_serial

    txns.append(
        Txn(
            serial=serial,
            date=start_date,
            description="OPENING BALANCE",
            ref_no="-",
            debit=None,
            credit=None,
            balance=balance,
        )
    )
    serial += 1

    day = start_date
    while day <= end_date:
        day_txns: List[Txn] = []

        def append_txn(description: str, ref_no: str, debit: Optional[float], credit: Optional[float]) -> None:
            nonlocal balance, serial
            if len(day_txns) >= max_txn_per_day:
                return

            local_debit = debit
            local_credit = credit
            projected = balance

            if local_debit is not None:
                if balance - local_debit < 150:
                    # If debit would overdraw too much, convert this event to a small incoming.
                    local_debit = None
                    local_credit = round(rng.uniform(900, 4500), 2)
                    description = f"UPI/{compact_name(rng.choice(POOLS['names']))}/{random_mobile(rng)}/UPI/{random_upi_id(rng)}"
                    ref_no = random_ref(rng, "UPI")
                    projected = round(balance + local_credit, 2)
                else:
                    projected = round(balance - local_debit, 2)
            elif local_credit is not None:
                projected = round(balance + local_credit, 2)

            # If crossing max balance, keep row under cap and add balancing debit (if slot available).
            sweep_debit: Optional[float] = None
            if projected > max_balance and local_credit is not None:
                allowed_credit = round(max_balance - balance, 2)
                if allowed_credit < 0:
                    allowed_credit = 0.0
                overflow = round(projected - max_balance, 2)
                local_credit = allowed_credit
                projected = round(balance + local_credit, 2)
                if len(day_txns) < max_txn_per_day - 1:
                    sweep_debit = round(overflow + rng.uniform(120, 1100), 2)

            balance = projected
            day_txns.append(
                Txn(
                    serial=serial,
                    date=day,
                    description=description,
                    ref_no=ref_no,
                    debit=local_debit,
                    credit=local_credit,
                    balance=balance,
                )
            )
            serial += 1

            if sweep_debit is not None and len(day_txns) < max_txn_per_day:
                balance = round(balance - sweep_debit, 2)
                day_txns.append(
                    Txn(
                        serial=serial,
                        date=day,
                        description="AUTO SWEEP OUT / BALANCE LIMIT CONTROL",
                        ref_no=random_ref(rng, "SWP"),
                        debit=sweep_debit,
                        credit=None,
                        balance=balance,
                    )
                )
                serial += 1

        # Fixed salary transaction: exact 10th of each month, 23k to 25k credit.
        if day.day == 10:
            salary_credit = choose_amount(rng, "salary_fixed")
            projected_after_salary = balance + salary_credit
            if projected_after_salary > max_balance and len(day_txns) < max_txn_per_day:
                required_debit = round(projected_after_salary - max_balance + rng.uniform(120, 800), 2)
                max_possible_debit = round(max(0.0, balance - 250), 2)
                pre_salary_debit = min(required_debit, max_possible_debit)
                if pre_salary_debit > 0:
                    append_txn(
                        description="AUTO SWEEP OUT / PRE SALARY BALANCE CONTROL",
                        ref_no=random_ref(rng, "SWP"),
                        debit=pre_salary_debit,
                        credit=None,
                    )

            append_txn(
                description="NEFT SALARY/ONE IT SOLUTIONS/MONTHLY CREDIT",
                ref_no=random_ref(rng, "NEF"),
                debit=None,
                credit=salary_credit,
            )

        if len(day_txns) < max_txn_per_day:
            slots_left = max_txn_per_day - len(day_txns)
            count = rng.choices([0, 1, 2, 3, 4], weights=[30, 36, 20, 10, 4], k=1)[0]
            count = min(count, slots_left)
            for _ in range(count):
                desc, ref, debit, credit, _ = make_transaction_payload(rng, day)
                append_txn(desc, ref, debit, credit)

        txns.extend(day_txns)
        day += timedelta(days=1)

    return txns


def draw_table_header(c: canvas.Canvas, x0: float, y0: float, widths: List[float], header_h: float) -> None:
    headers = ["#", "Date", "Description", "Chq/Ref. No.", "Withdrawal (Dr.)", "Deposit (Cr.)", "Balance"]
    c.setFillColor(colors.HexColor("#97999c"))
    c.rect(x0, y0 - header_h, sum(widths), header_h, stroke=0, fill=1)

    c.setFillColor(colors.white)
    x = x0
    for i, title in enumerate(headers):
        max_w = widths[i] - 8
        font_size = 8.7
        while font_size > 6.4 and pdfmetrics.stringWidth(title, "Helvetica", font_size) > max_w:
            font_size -= 0.2
        c.setFont("Helvetica", font_size)
        c.drawString(x + 4, y0 - header_h + 8, title)
        if i > 0:
            c.setStrokeColor(colors.HexColor("#b2b3b6"))
            c.setLineWidth(1)
            c.line(x, y0 - header_h, x, y0)
        x += widths[i]


def draw_title_band(c: canvas.Canvas, page_w: float, y_top: float, margin: float, title_h: float) -> None:
    c.setFillColor(colors.HexColor("#de332f"))
    c.rect(margin, y_top - title_h, page_w - 2 * margin, title_h, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(page_w / 2, y_top - title_h + 9, "Savings Account Transactions")


def draw_statement_pdf(
    output_path: Path,
    txns: List[Txn],
    head_image: Optional[Path],
    second_last_image: Optional[Path],
    end_image: Optional[Path],
) -> None:
    page_w, page_h = A4  # Portrait
    c = canvas.Canvas(str(output_path), pagesize=A4)

    px = 0.75  # 1 CSS px ~= 0.75 pt
    side_margin = (16 * mm) - (10 * px)  # reduced by 10px from left and right
    top_margin = 12 * mm
    footer_h = 12 * mm
    page_header_h = 28 * mm
    title_h = 14 * mm
    table_header_h = 12 * mm

    usable_w = page_w - (2 * side_margin)
    widths_ratio = [0.05, 0.14, 0.33, 0.15, 0.11, 0.11, 0.11]
    widths = [w * usable_w for w in widths_ratio]
    desc_font = "Helvetica"
    desc_font_size = 8.7
    desc_text_width = widths[2] - 6
    generated_at = datetime.now().strftime("%d %b %Y, %H:%M")

    # Calculate exact transaction pages before rendering so footer can show "Page X of Y".
    def transaction_row_height(txn: Txn) -> float:
        desc_lines = split_text_by_width(txn.description, desc_font, desc_font_size, desc_text_width, max_lines=3)
        line_h_pt = 9.0
        return max(7.5 * mm, (len(desc_lines) * line_h_pt + 6) * 0.3528 * mm)

    tx_start_y = page_h - top_margin - page_header_h
    tx_content_top = tx_start_y - title_h - table_header_h
    tx_content_bottom = footer_h + 6 * mm
    tx_available_h = tx_content_top - tx_content_bottom
    rows_acc_h = 0.0
    tx_pages = 1
    for t in txns:
        rh = transaction_row_height(t)
        if rows_acc_h + rh > tx_available_h:
            tx_pages += 1
            rows_acc_h = 0.0
        rows_acc_h += rh
    total_pages = 1 + tx_pages + 2  # first image cover + transaction pages + summary page + end image page

    def draw_footer(page_no: int) -> None:
        c.setFillColor(colors.white)
        c.rect(0, 0, page_w, footer_h, stroke=0, fill=1)
        c.setFillColor(colors.HexColor("#bcc0c5"))  # lighter gray
        c.setFont("Helvetica-Bold", 8.2)
        c.drawString(side_margin, 4.2 * mm, f"Statement Generated on {generated_at}")
        c.drawRightString(page_w - side_margin, 4.2 * mm, f"Page {page_no} of {total_pages}")

    def draw_non_first_header() -> None:
        y_top = page_h - top_margin
        x = side_margin
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(x, y_top - 8.5 * mm, "Arab Juned Mohammed Iqbal")
        c.setFont("Helvetica", 8.8)
        c.setFillColor(colors.HexColor("#9ca0a5"))
        c.drawString(x, y_top - 14 * mm, "Account No.")
        c.drawString(x, y_top - 19.5 * mm, "Account Statement")
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 9.8)
        c.drawString(x + 21 * mm, y_top - 14 * mm, "1449503671")
        c.drawString(x + 33 * mm, y_top - 19.5 * mm, f"{txns[0].date.strftime('%d %b %Y')} - {txns[-1].date.strftime('%d %b %Y')}")

    def draw_full_page_image(image_path: Optional[Path]) -> None:
        if not image_path or not image_path.exists():
            return
        img = ImageReader(str(image_path))
        iw, ih = img.getSize()
        max_w = page_w - (2 * side_margin)
        max_h = page_h - footer_h - (2 * top_margin)
        scale = min(max_w / iw, max_h / ih)
        draw_w = iw * scale
        draw_h = ih * scale
        x = (page_w - draw_w) / 2
        y = footer_h + ((page_h - footer_h - draw_h) / 2)
        c.drawImage(
            str(image_path),
            x,
            y,
            width=draw_w,
            height=draw_h,
            preserveAspectRatio=True,
            anchor="sw",
            mask="auto",
        )

    def draw_account_summary_block(opening_balance: float, closing_balance: float, y_top: float) -> None:
        summary_margin = side_margin
        summary_title_h = 12 * mm
        header_h = 14 * mm
        row_h = 9 * mm
        total_w = page_w - (2 * summary_margin)
        cols = [0.45 * total_w, 0.275 * total_w, 0.275 * total_w]

        c.setFillColor(colors.HexColor("#f11522"))
        c.rect(summary_margin, y_top - summary_title_h, total_w, summary_title_h, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica", 12.5)  # smaller + regular weight
        c.drawCentredString(page_w / 2, y_top - summary_title_h + 8.5, "Account Summary")

        header_top = y_top - summary_title_h
        c.setFillColor(colors.HexColor("#9b9ea3"))
        c.rect(summary_margin, header_top - header_h, total_w, header_h, stroke=0, fill=1)
        c.setStrokeColor(colors.HexColor("#c2c4c7"))
        c.setLineWidth(1)
        c.line(summary_margin + cols[0], header_top - header_h, summary_margin + cols[0], header_top)
        c.line(summary_margin + cols[0] + cols[1], header_top - header_h, summary_margin + cols[0] + cols[1], header_top)

        c.setFillColor(colors.white)
        c.setFont("Helvetica", 10)
        c.drawString(summary_margin + 8, header_top - header_h + 8, "Particulars")
        c.drawString(summary_margin + cols[0] + 8, header_top - header_h + 8, "Opening Balance")
        c.drawString(summary_margin + cols[0] + cols[1] + 8, header_top - header_h + 8, "Closing Balance")

        row_top = header_top - header_h
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 11)
        c.drawString(summary_margin + 8, row_top - row_h + 3.5, "Savings Account (SA):")
        c.drawRightString(summary_margin + cols[0] + cols[1] - 10, row_top - row_h + 3.5, f"{opening_balance:,.2f}")
        c.drawRightString(summary_margin + total_w - 10, row_top - row_h + 3.5, f"{closing_balance:,.2f}")
        c.setStrokeColor(colors.HexColor("#acafb3"))
        c.line(summary_margin, row_top - row_h, summary_margin + total_w, row_top - row_h)

    # Page 1: full-height first image
    current_page = 1
    draw_full_page_image(head_image)
    draw_footer(current_page)

    # Transaction pages (from page 2)
    c.showPage()
    current_page += 1
    draw_non_first_header()
    draw_title_band(c, page_w, tx_start_y, side_margin, title_h)
    y = tx_start_y - title_h
    draw_table_header(c, side_margin, y, widths, table_header_h)
    y -= table_header_h
    c.setStrokeColor(colors.HexColor("#c4c4c4"))
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9.2)

    def new_tx_page() -> float:
        nonlocal current_page
        draw_footer(current_page)
        c.showPage()
        current_page += 1
        draw_non_first_header()
        draw_title_band(c, page_w, tx_start_y, side_margin, title_h)
        local_y = tx_start_y - title_h
        draw_table_header(c, side_margin, local_y, widths, table_header_h)
        c.setStrokeColor(colors.HexColor("#c4c4c4"))
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9.2)
        return local_y - table_header_h

    for t in txns:
        desc_lines = split_text_by_width(t.description, desc_font, desc_font_size, desc_text_width, max_lines=3)
        line_h_pt = 9.0
        row_h = max(7.5 * mm, (len(desc_lines) * line_h_pt + 6) * 0.3528 * mm)

        if y - row_h < tx_content_bottom:
            y = new_tx_page()

        c.line(side_margin, y - row_h, side_margin + sum(widths), y - row_h)
        date_value = "" if t.description == "OPENING BALANCE" else t.date.strftime("%d %b %Y")
        values = [
            "-" if t.description == "OPENING BALANCE" else str(t.serial),
            date_value,
            None,
            t.ref_no,
            f"{t.debit:,.2f}" if t.debit is not None else "",
            f"{t.credit:,.2f}" if t.credit is not None else "",
            f"{t.balance:,.2f}",
        ]
        x = side_margin
        for i, val in enumerate(values):
            col_w = widths[i]
            if i == 2:
                c.setFont(desc_font, desc_font_size)
                text_y = y - 10
                for line in desc_lines:
                    c.drawString(x + 3, text_y, line)
                    text_y -= line_h_pt
                c.setFont("Helvetica", 9.2)
            elif i >= 4:
                c.drawRightString(x + col_w - 3, y - 10, val)
            else:
                c.drawString(x + 3, y - 10, val)
            x += col_w
        y -= row_h

    draw_footer(current_page)

    # Second-last page: summary ABOVE image.
    opening_balance = txns[0].balance if txns else 0.0
    closing_balance = txns[-1].balance if txns else 0.0
    c.showPage()
    current_page += 1
    draw_non_first_header()
    summary_top = page_h - top_margin - page_header_h - 3 * mm
    draw_account_summary_block(opening_balance, closing_balance, y_top=summary_top)

    content_top = summary_top - 38 * mm
    content_bottom = footer_h + 4 * mm
    if second_last_image and second_last_image.exists():
        c.drawImage(
            str(second_last_image),
            side_margin,
            content_bottom,
            width=page_w - (2 * side_margin),
            height=content_top - content_bottom,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )
    draw_footer(current_page)

    # Last page: end image + header + footer.
    c.showPage()
    current_page += 1
    draw_non_first_header()
    image_top = page_h - top_margin - page_header_h
    c.drawImage(
        str(end_image),
        0,
        footer_h,
        width=page_w,
        height=image_top - footer_h,
        preserveAspectRatio=False,
        anchor="sw",
        mask="auto",
    )
    draw_footer(current_page)

    c.save()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a dynamic mock account statement PDF for practice.")
    parser.add_argument("--output", default="mock_statement.pdf", help="Output PDF path")
    parser.add_argument("--seed", type=int, default=2026, help="Random seed for repeatable output")
    parser.add_argument("--start-date", default="2026-01-01", help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end-date", default="2026-04-19", help="End date in YYYY-MM-DD format")
    parser.add_argument("--opening-balance", type=float, default=5432.0, help="Opening balance")
    parser.add_argument("--start-serial", type=int, default=1, help="Starting serial number")
    parser.add_argument("--max-balance", type=float, default=80000.0, help="Maximum allowed balance")
    parser.add_argument("--max-txn-per-day", type=int, default=4, help="Maximum transactions per day")
    base_dir = Path(__file__).resolve().parent
    parser.add_argument("--head-image", default=str(base_dir / "head.png"), help="Image path for first page header")
    parser.add_argument(
        "--second-last-image",
        default=str(base_dir / "second-last-end.png"),
        help="Image path for second-last page",
    )
    parser.add_argument("--end-image", default=str(base_dir / "end.png"), help="Image path for last page")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

    if end_date < start_date:
        raise ValueError("end-date must be on or after start-date")

    txns = generate_transactions(
        start_date=start_date,
        end_date=end_date,
        opening_balance=args.opening_balance,
        start_serial=args.start_serial,
        seed=args.seed,
        max_balance=args.max_balance,
        max_txn_per_day=max(1, args.max_txn_per_day),
    )

    output_path = Path(args.output).resolve()
    draw_statement_pdf(
        output_path=output_path,
        txns=txns,
        head_image=Path(args.head_image).expanduser(),
        second_last_image=Path(args.second_last_image).expanduser(),
        end_image=Path(args.end_image).expanduser(),
    )

    print(f"Generated PDF: {output_path}")
    print(f"Transactions: {len(txns)}")
    print(f"Date range: {args.start_date} to {args.end_date}")
    print("Opening row included with serial '-'")
    print(f"Balance cap control active at: {args.max_balance:,.2f}")


if __name__ == "__main__":
    main()
