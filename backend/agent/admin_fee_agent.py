from tools.academic_fee_tool import academic_fee_summary, academic_fee_report
from tools.mess_fee_tool import mess_fee_summary, mess_fee_report
from tools.hostel_fee_tool import hostel_fee_summary, hostel_fee_report
from agent.sort_utils import extract_sorting, apply_sorting

import re

FEE_SYNONYMS = {
    "fees": "fee",
    "charges": "fee",
    "payment": "fee",
    "payments": "fee",
    "amount": "fee"
}

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    words = text.split()
    words = [FEE_SYNONYMS.get(w, w) for w in words]

    return " ".join(words)

def detect_status(q: str) -> str:
    if any(w in q for w in ["unpaid", "due", "pending", "not paid"]):
        return "unpaid"

    if any(w in q for w in ["paid", "completed", "success"]):
        return "captured"

    return "all"

def safe_sort(df, sort_cfg):
    """Prevent crash if df None or column missing"""
    try:
        if df is None or df.empty:
            return df
        return apply_sorting(df, sort_cfg)
    except Exception as e:
        print(" Sorting failed:", e)
        return df


def _counts_from_df(df, paid_value="paid"):
    """Universal helper → counts always from visible table data"""
    if df is None or df.empty:
        return 0, 0, 0

    total = len(df)

    if "_payment_status" in df.columns:
        paid = len(df[df["_payment_status"] == paid_value])
    elif "__payment_status" in df.columns:
        paid = len(df[df["__payment_status"] == paid_value])
    else:
        paid = 0

    unpaid = total - paid
    return total, paid, unpaid


def admin_agent(user_query: str):
    try:
        q = normalize(user_query)
        status = detect_status(q)

        wants_table = any(w in q for w in ["list", "report", "students", "show", "generate", "make"])

        sort_cfg = extract_sorting(q)
        fee_type = sort_cfg.get("fee_type")

        # fallback safety 
        if not fee_type:
            fee_type = "ACADEMIC"

        # ================= Academic ==================
        if fee_type == "ACADEMIC":
            status = 2 if "unpaid" in q else 1 if "paid" in q else 0

            df = academic_fee_report(status) if wants_table else None
            df = safe_sort(df, sort_cfg)

            if df is not None:
                total, paid, unpaid = _counts_from_df(df, "paid")
            else:
                summary = academic_fee_summary(status)
                total, paid, unpaid = summary["total"], summary["paid"], summary["unpaid"]

            text = (
                "Academic Fee Report\n\n"
                f"Total Students : {total}\n"
                f"Paid Students : {paid}\n"
                f"Unpaid Students : {unpaid}\n"
            )
            return text, df

        # ================= Mess =================
        elif fee_type == "MESS":
            status = "unpaid" if "unpaid" in q else "captured" if "paid" in q else ""

            df = mess_fee_report(status) if wants_table else None
            df = safe_sort(df, sort_cfg)

            if df is not None:
                total, paid, unpaid = _counts_from_df(df, "captured")
            else:
                summary = mess_fee_summary(status)
                total, paid, unpaid = summary["total"], summary["paid"], summary["unpaid"]

            text = (
                "Mess Fee Report\n\n"
                f"Total Students : {total}\n"
                f"Paid Students : {paid}\n"
                f"Unpaid Students : {unpaid}\n"
            )
            return text, df

        # ================= Hostel =================
        elif fee_type == "HOSTEL":
            payment_filter = "Unpaid" if "unpaid" in q else "Paid" if "paid" in q else "All"

            df = hostel_fee_report(payment_filter) if wants_table else None
            df = safe_sort(df, sort_cfg)

            if df is not None:
                total, paid, unpaid = _counts_from_df(df, "paid")
            else:
                summary = hostel_fee_summary(payment_filter)
                total, paid, unpaid = summary["total"], summary["paid"], summary["unpaid"]

            text = (
                "Hostel Fee Report\n\n"
                f"Total Students : {total}\n"
                f"Paid Students : {paid}\n"
                f"Unpaid Students : {unpaid}\n"
            )
            return text, df

        return "Ask about Academic, Mess, or Hostel Fee", None

    except Exception as e:
        print(" ADMIN AGENT CRASH:", e)
        return "Something went wrong while processing your request.", None
