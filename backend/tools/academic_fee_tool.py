import pandas as pd
from db import get_db_connection


def academic_fee_summary(status: int, batch=None):
    """
    status:
    0 = all
    1 = paid
    2 = unpaid
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        EXEC dbo.Proc_GetOnlineAdmissionformAdmin2
            @CourseType = NULL,
            @CourseId = NULL,
            @AdmissionSession = NULL,
            @SearchText = NULL,
            @StatusType = 'All',
            @Session = ?,
            @Status = 0
    """, batch)

    columns = [col[0] for col in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()

    # Normalize payment status
    for r in rows:
        r["_payment_status"] = str(r.get("PaymentStatus", "")).strip().lower()

    # 🔹 Apply STATUS filter FIRST (same as table)
    if status == 1:
        filtered_rows = [r for r in rows if r["_payment_status"] == "paid"]
    elif status == 2:
        filtered_rows = [r for r in rows if r["_payment_status"] != "paid"]
    else:
        filtered_rows = rows

    #  COUNTS ONLY FROM FILTERED TABLE DATA
    paid_count = len([r for r in filtered_rows if r["_payment_status"] == "paid"])
    unpaid_count = len([r for r in filtered_rows if r["_payment_status"] != "paid"])

    return {
        "total": len(filtered_rows),   #  table ke equal
        "paid": paid_count,            #  table based
        "unpaid": unpaid_count,        #  table based
        "rows": filtered_rows
    }


def academic_fee_report(status: int, batch=None):
    data = academic_fee_summary(status, batch)
    return pd.DataFrame(data["rows"])
