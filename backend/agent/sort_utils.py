import pandas as pd
import re


# =========================================================
# GET CURRENT ACADEMIC YEAR (DYNAMIC)
# =========================================================
from datetime import datetime

def _get_current_academic_year():
    now = datetime.now()
    year = now.year
    month = now.month

    # Academic year assumed April → March
    if month >= 4:
        start = year
        end = year + 1
    else:
        start = year - 1
        end = year

    return f"{start}-{str(end)[-2:]}"

# =========================================================
# DETECT STUDENT TYPE
# =========================================================
def _detect_student_type(q: str):
    q = q.lower()

    if "new" in q or "fresh" in q:
        return "New"

    if "old" in q or "existing" in q:
        return "Existing"
    return None


# =========================================================
# NORMALIZE QUERY
# =========================================================
def _normalize(text: str):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# =========================================================
# DETECT COURSE LEVEL
# =========================================================
def _detect_course_level(q: str):
    if "ug" in q:
        return "UG"
    if "pg" in q:
        return "PG"
    if "diploma" in q:
        return "Diploma"
    if "certificate" in q:
        return "Certificate"
    return None

# =========================================================
# DETECT COURSE NAME + SPECIALIZATION
# =========================================================
def _detect_course_name(q: str):
    course_patterns = {
        r"\b(mbbs|m\.?\s*b\.?\s*b\.?\s*s\.?)\b": "MBBS",
        r"\bbsc\s*nursing\b": "BSc Nursing",
        r"\bmd\b": "MD",
        r"\bms\b": "MS",
        r"\bdnb\b": "DNB",
        r"\bmd\s*anesthesia\b": "MD Anesthesia",
        r"\bmd\s*radiology\b": "MD Radiology",
        r"\bmd\s*medicine\b": "MD Medicine",
        r"\bms\s*surgery\b": "MS Surgery",
        r"\bms\s*orthopedic\b": "MS Orthopedic",
        r"\bmsc\b": "MSc",
        r"\bdiploma\b": "Diploma",
        r"\bdiploma\s*in\s*radiotherapy\b": "Diploma in Radiotherapy",
        r"\bdiploma\s*in\s*medical\s*laboratory\s*technology\b": "Diploma in Medical Laboratory Technology",
        r"\bdiploma\s*in\s*x\s*ray\s*technology\b": "Diploma in X-ray Technology",
        r"\bpdcc\b": "PDCC",
        r"\bpdf\b": "PDF",
    }

    for pattern, course in course_patterns.items():
        if re.search(pattern, q, flags=re.IGNORECASE):
            return course
    return None

# =========================================================
# DETECT PAYMENT STATUS
# =========================================================
def _detect_payment_status(q: str):
    if any(k in q for k in ["unpaid", "not paid", "pending", "due"]):
        return "UNPAID"
    if any(k in q for k in ["paid", "completed", "done"]):
        return "PAID"
    return None

# =========================================================
# DETECT ADMIN INTENT
# =========================================================
def _detect_admin_intent(q: str):
    q = q.lower()

    # COUNT highest priority
    if any(k in q for k in ["how many", "count", "total number"]):
        return "COUNT"

    # REPORT keywords (generate bhi yahin)
    if any(k in q for k in ["report", "generate", "create", "make", "data"]):
        return "REPORT"

    # SUMMARY
    if any(k in q for k in ["summary", "overview", "status"]):
        return "SUMMARY"

    # LIST explicit
    if "list" in q or "show" in q:
        return "LIST"

    # default
    return "REPORT"

# =========================================================
# DETECT BATCH YEAR
# =========================================================
def _detect_batch(q: str):
    match = re.search(r"\b(20\d{2})\b", q)
    return match.group(1) if match else None

# =========================================================
# DETECT FEE TYPE
# =========================================================
def _detect_fee_type(q: str):
    q = q.lower()

    if "quarter" in q or re.search(r"\bq[1-4]\b", q):
        return "MESS"

    if any(k in q for k in ["mess", "food", "canteen"]):
        return "MESS"

    if any(k in q for k in ["hostel", "room"]):
        return "HOSTEL"

    # default academic when only fee/fees written
    if any(k in q for k in ["academic", "tuition", "college", "fee", "fees"]):
        return "ACADEMIC"

    return None



# =========================================================
# DETECT QUARTER FROM QUERY
# =========================================================
def _detect_quarter_from_query(q: str):
    q = q.lower()
    match = re.search(r"(?:quarter\s*)?(q[1-4]|[1-4](?:st|nd|rd|th)?|first|second|third|fourth)", q)
    if match:
        val = match.group(1)
        mapping = {
            "1":"1","2":"2","3":"3","4":"4",
            "first":"1","second":"2","third":"3","fourth":"4",
            "q1":"1","q2":"2","q3":"3","q4":"4",
            "1st":"1","2nd":"2","3rd":"3","4th":"4"
        }
        return int(mapping[val])
    return None

# =========================================================
# DETECT STUDENT NAME FROM QUERY (FIXED)
# =========================================================
def _detect_student_name(query: str):
    words = re.findall(r"[a-zA-Z]+", query.lower())

    ignore = {
        "show","report","summary","count","total","students",
        "paid","unpaid","mess","hostel","academic","fee",
        "of","the","for","in","quarter","batch","ug","pg",
        "list","status","overview", "generate", "create", "make",

        #  course words remove
        "mbbs","md","ms","dnb","pdcc","pdf","msc",
        "bsc","nursing","diploma","certificate",
        "first","second","third","fourth"

        # ⭐ NEW IMPORTANT IGNORES
        "alphabet","alphabetical","order","name","sort","a","to","z",
        "latest","recent","date","wise"
    }

    names = [w for w in words if w not in ignore and len(w) > 2]

    return " ".join(names) if names else None

# =========================================================
# EXTRACT CONFIG FROM QUERY
# =========================================================
def extract_sorting(query: str):
    q = _normalize(query)
    return {
        "by_batch": "batch" in q,
        "by_name": any(k in q for k in ["name", "alphabet", "alphabetical"]),
        "by_date": any(k in q for k in ["date", "latest", "recent"]),
        "by_quarter": "quarter" in q,
        "course_level": _detect_course_level(q),
        "course_name": _detect_course_name(q),
        "payment_status": _detect_payment_status(q),
        "batch_year": _detect_batch(q),
        "fee_type": _detect_fee_type(q),
        "intent": _detect_admin_intent(q),
        "quarter_num": _detect_quarter_from_query(query),
        "student_name": _detect_student_name(query),


    }

# =========================================================
# SAFE COLUMN FINDER
# =========================================================
def _find_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None

# =========================================================
# APPLY FILTERING + SORTING
# =========================================================
def apply_sorting(df: pd.DataFrame, cfg: dict, query: str = ""):
    if df is None or df.empty:
        return df
    df = df.copy()

    # ---------------- HOSTEL VERIFICATION FILTER (NEW, SAFE) ----------------
    if cfg.get("fee_type") == "HOSTEL":
        ver_col = _find_column(df, ["VerificationStatus", "HostelStatus", "Status"])
        if ver_col:
            df = df[df[ver_col].astype(str).str.lower().str.strip() == "verified"]
    

    # ---------------- COURSE FILTER ----------------
    course_cols = [c for c in ["CourseType","Course","Program","CourseName","Specialization","Branch","Department"] if c in df.columns]
    if course_cols:
        df["_course_norm"] = (
            df[course_cols]
            .astype(str)
            .agg(" ".join, axis=1)
            .str.lower()
            .str.replace(r"[^a-z0-9\s]", " ", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        if cfg.get("course_level"):
            df = df[df["_course_norm"].str.contains(cfg["course_level"].lower(), na=False)]
        if cfg.get("course_name"):
            course = cfg["course_name"].lower()
            if course == "mbbs":
                pattern = r"\bmbbs\b|\bm\s*b\s*b\s*s\b|bachelor\s*of\s*medicine\s*and\s*surgery"
            elif course == "ms":
                pattern = r"\bms\b"
            elif course == "md":
                pattern = r"\bmd\b"
            elif course == "dnb":
                pattern = r"\bdnb\b"
            elif course == "pdcc":
                pattern = r"\bpdcc\b"
            elif course == "pdf":
                pattern = r"\bpdf\b"
                df = df[df["_course_norm"].str.contains(r"\bcertificate\b", na=False)]
            elif course == "msc":
                pattern = r"\bmsc\b"
            else:
                pattern = "|".join(course.split())
            df = df[df["_course_norm"].str.contains(pattern, na=False)]
    
    # ================= ADD HERE =================
# ---------------- STUDENT NAME FILTER (FINAL CORRECT POSITION) ----------------
    if cfg["student_name"] and not cfg.get("course_name"):

        name_col = _find_column(df, ["StudentName", "Name", "FullName"])

        if not name_col and {"FirstName", "LastName"}.issubset(df.columns):
            df["FullName"] = (
                df["FirstName"].fillna("") + " " + df["LastName"].fillna("")
            ).str.strip()
            name_col = "FullName"

        if name_col:
            search_name = cfg["student_name"].lower().strip()
            name_series = df[name_col].astype(str).str.lower().str.strip()

            # FULL NAME → exact match
            if " " in search_name:
                df = df[name_series == search_name]

            # SINGLE WORD → word boundary partial match
            else:
                df = df[name_series.str.contains(rf"\b{re.escape(search_name)}\b", na=False)]

# ============================================
    # ---------------- BATCH FILTER ----------------
    if cfg.get("batch_year"):
        batch_col = _find_column(df, ["BatchSession", "BatchYear", "Batch"])
        if batch_col:
            df = df[df[batch_col].astype(str).str.contains(cfg["batch_year"], na=False)]


    # ---------------- PAYMENT FILTER (FIXED) ----------------
    if cfg.get("payment_status"):
        status_col = _find_column(df, ["PaymentStatus", "Status", "IsPaid", "FeeStatus"])
        if status_col:
            status_series = df[status_col].astype(str).str.lower().str.strip()

            paid_values = {"paid","completed","done","success","captured","1","true"}
            unpaid_values = {"unpaid","pending","due","failed","0","false","not paid"}

            if cfg["payment_status"] == "PAID":
                df = df[status_series.isin(paid_values)]
            else:
                df = df[status_series.isin(unpaid_values)]
    
    # ---------------- QUARTER FILTER + SORTING (MESS ONLY) ----------------
    if cfg["fee_type"] == "MESS":
        quarter_col = _find_column(df, ["Quarter", "QuarterName", "QuarterId"])
        if quarter_col:
            def parse_quarter(val):
                if val is None: return None
                val = str(val).lower().strip()
                mapping = {
                    "1":1,"q1":1,"1st":1,"first":1,"1st quarter":1,"first quarter":1,
                    "2":2,"q2":2,"2nd":2,"second":2,"2nd quarter":2,"second quarter":2,
                    "3":3,"q3":3,"3rd":3,"third":3,"3rd quarter":3,"third quarter":3,
                    "4":4,"q4":4,"4th":4,"fourth":4,"4th quarter":4,"fourth quarter":4,
                }
                return mapping.get(val, None)

            df["_quarter_num"] = df[quarter_col].apply(parse_quarter)

            if cfg.get("quarter_num"):
                df = df[df["_quarter_num"] == cfg["quarter_num"]]

            df = df.sort_values(by="_quarter_num", ascending=True, na_position="last")
            df.drop(columns="_quarter_num", inplace=True)

    # ---------------- OTHER SORTING Techniques ----------------
    sort_cols, ascending = [], []
    if cfg["by_date"]:
        date_col = _find_column(df, ["ApplicationDate", "CreatedDate", "CreatedOn", "PaymentDate"])
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            sort_cols.append(date_col)
            ascending.append(False)
    if cfg["by_batch"]:
        batch_col = _find_column(df, ["BatchSession", "BatchYear", "Batch"])
        if batch_col:
            df[batch_col] = pd.to_numeric(df[batch_col], errors="coerce")
            sort_cols.append(batch_col)
            ascending.append(True)
    if cfg["by_name"]:
        name_col = _find_column(df, ["StudentName", "Name", "FullName"])

    if not name_col and {"FirstName","LastName"}.issubset(df.columns):
        df["FullName"] = (
            df["FirstName"].fillna("").astype(str) + " " +
            df["LastName"].fillna("").astype(str)
        ).str.strip()
        name_col = "FullName"

    if name_col:
        df[name_col] = df[name_col].astype(str)
        df = df.sort_values(by=name_col, key=lambda x: x.str.lower(), na_position="last")


    if sort_cols:
        df = df.sort_values(by=sort_cols, ascending=ascending, na_position="last")

    if "_course_norm" in df.columns:
        df.drop(columns="_course_norm", inplace=True)

    # ---------------- ADD DYNAMIC ACADEMIC YEAR COLUMN ----------------
    if "AcademicYear" not in df.columns:
        df["AcademicYear"] = _get_current_academic_year()

    return df
# =========================================================
# MAIN ADMIN RESPONSE
# =========================================================
def generate_admin_response(df_dict: dict, query: str):
    cfg = extract_sorting(query)
    fee_type = cfg["fee_type"] or "ACADEMIC"
    df = df_dict.get(fee_type)

    if df is None or df.empty:
        return {"type": "NO_RESULT", "message": f"No data found for {fee_type} fee"}

    filtered_df = apply_sorting(df, cfg, query=query)

    if filtered_df.empty:
        return {"type": "NO_RESULT", "message": "No matching students found"}

    intent = cfg["intent"]

    # ---------------- COUNT ----------------
    if intent == "COUNT":
        return {"type":"COUNT","total_students":len(filtered_df)}

    # ---------------- SUMMARY / REPORT (FIXED COUNTS) ----------------
    if intent in ["SUMMARY","REPORT"]:
        status_col = _find_column(filtered_df, ["PaymentStatus","Status","IsPaid","FeeStatus"])
        paid = unpaid = None

        if status_col:
            status_series = filtered_df[status_col].astype(str).str.lower().str.strip()
            paid = filtered_df[status_series.isin({"paid","completed","done","success","captured","1","true"})]
            unpaid = filtered_df[status_series.isin({"unpaid","pending","due","failed","0","false","not paid"})]

        return {
            "type": intent,
            "total_students": len(filtered_df),
            "paid_students": len(paid) if paid is not None else 0,
            "unpaid_students": len(unpaid) if unpaid is not None else 0,

            #  IMPORTANT — tables for frontend
            "paid_data": paid if intent == "REPORT" else None,
            "unpaid_data": unpaid if intent == "REPORT" else None,

            # optional full table
            "data": filtered_df if intent == "REPORT" else None,
}

    # ---------------- DEFAULT LIST ----------------
    return {"type":"LIST","total_students":len(filtered_df),"data":filtered_df}
