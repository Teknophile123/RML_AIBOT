import pandas as pd
from db import get_db_connection

def mess_fee_summary(status: str, year=None, quarter=None):
    """
    status:
    ''         = all
    'captured' = paid
    'unpaid'   = unpaid
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        EXEC dbo.Proc_GetMessUserList
            @batch = NULL,
            @courseTypeId = NULL,
            @courseId = NULL,
            @year = ?,
            @quarter = ?,
            @status = ?,
            @HostelId = NULL,
            @GenderId = NULL,
            @Hosteller = 0
    """, year, quarter, status)

    columns = [col[0] for col in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()

    # Normalize payment status
    for r in rows:
        r["__payment_status"] = str(r.get("PaymentStatus", "")).strip().lower()

    paid_rows = [r for r in rows if r["__payment_status"] == "captured"]
    unpaid_rows = [r for r in rows if r["__payment_status"] != "captured"]

    #  FILTER BASED ON QUERY 
    if status == "captured":
        filtered_rows = paid_rows
    elif status == "unpaid":
        filtered_rows = unpaid_rows
    else:
        filtered_rows = rows

    return {
        "total": len(rows),
        "paid": len(paid_rows),
        "unpaid": len(unpaid_rows),
        "rows": filtered_rows
    }


def mess_fee_report(status: str, year=None, quarter=None):
    """
    Returns DataFrame ONLY for requested rows
    """
    data = mess_fee_summary(status, year, quarter)
    return pd.DataFrame(data["rows"])
