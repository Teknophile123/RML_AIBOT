import pandas as pd
from db import get_db_connection


def hostel_fee_summary(
    payment_filter: str = "All",
    batch=None,
    course_type_id=None,
    course_id=None,
    year=None,
    gender=None
):
    """
    payment_filter:
    'All'    → all students
    'Paid'   → submitted hostel fee
    'Unpaid' → not submitted
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        EXEC dbo.proc_GetHostelPaymentReport
            @Batch = ?,
            @CourseTypeId = ?,
            @CourseId = ?,
            @Year = ?,
            @Gender = ?,
            @PaymentFilter = ?
    """, batch, course_type_id, course_id, year, gender, payment_filter)

    columns = [col[0] for col in cursor.description]
    all_rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()

    #  Normalize PaymentStatus ONCE
    for r in all_rows:
        r["_payment_status"] = str(r.get("PaymentStatus", "")).strip().lower()

    paid_rows = [r for r in all_rows if r["_payment_status"] == "paid"]
    unpaid_rows = [r for r in all_rows if r["_payment_status"] == "unpaid"]

    #  Agent-level filtering (FINAL TRUTH)
    pf = payment_filter.lower()
    if pf == "paid":
        filtered_rows = paid_rows
    elif pf == "unpaid":
        filtered_rows = unpaid_rows
    else:
        filtered_rows = all_rows

    return {
        #  context-aware totals (THIS FIXES YOUR PROBLEM)
        "total": len(filtered_rows),
        "paid": len(paid_rows),
        "unpaid": len(unpaid_rows),
        "rows": filtered_rows
    }


def hostel_fee_report(payment_filter="All", **kwargs):
    summary = hostel_fee_summary(payment_filter, **kwargs)
    return pd.DataFrame(summary["rows"])


