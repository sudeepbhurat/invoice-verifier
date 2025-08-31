# ==============================================
# Invoice Verifier Backend (FastAPI) - Vercel Compatible
# ==============================================
# This version is optimized for Vercel deployment
# Handles serverless environment and Vercel's Python runtime
# ==============================================

from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi import HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from datetime import datetime, date
from dateutil import parser as dateparser
import re
import io
import os
import json

# ----------- Vercel-compatible setup -----------
# Remove SQLite for Vercel (serverless environment)
# Use in-memory storage or external database for production

# ----------- Helpers: India GSTIN validation -----------
# State code mapping (partial common ones); extend as needed
STATE_CODES = {
    "01": "Jammu & Kashmir", "02": "Himachal Pradesh", "03": "Punjab", "04": "Chandigarh",
    "05": "Uttarakhand", "06": "Haryana", "07": "Delhi", "08": "Rajasthan",
    "09": "Uttar Pradesh", "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh",
    "13": "Nagaland", "14": "Manipur", "15": "Mizoram", "16": "Tripura",
    "17": "Meghalaya", "18": "Assam", "19": "West Bengal", "20": "Jharkhand",
    "21": "Odisha", "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
    "27": "Maharashtra", "29": "Karnataka", "30": "Goa", "32": "Kerala",
    "33": "Tamil Nadu", "36": "Telangana", "37": "Andhra Pradesh",
}

BASE36 = {ch: i for i, ch in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")}


def gstin_checksum_calc(gstin14: str) -> str:
    """Compute the 15th GSTIN checksum character from first 14 chars."""
    total = 0
    for idx, ch in enumerate(gstin14):
        val = BASE36.get(ch, -1)
        if val < 0:
            return "?"
        weight = 1 if (idx % 2 == 0) else 2
        prod = val * weight
        quotient, remainder = divmod(prod, 36)
        total += quotient + remainder
    check_val = (36 - (total % 36)) % 36
    for k, v in BASE36.items():
        if v == check_val:
            return k
    return "?"


def validate_gstin_structure(gstin: str) -> Dict[str, Any]:
    info = {"raw": gstin, "valid": False, "errors": [], "state": None, "pan": None}
    if not gstin:
        info["errors"].append("Missing GSTIN")
        return info
    gstin = gstin.strip().upper()
    info["normalized"] = gstin
    
    if not re.fullmatch(r"[0-9A-Z]{15}", gstin or ""):
        info["errors"].append("GSTIN must be 15 alphanumeric (uppercase)")
        return info
    
    state = gstin[:2]
    if state not in STATE_CODES:
        info["errors"].append(f"Unknown/invalid state code: {state}")
    else:
        info["state"] = {"code": state, "name": STATE_CODES[state]}
    
    pan = gstin[2:12]
    if not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan):
        info["errors"].append("Embedded PAN structure invalid (AAAAA9999A)")
    else:
        info["pan"] = pan
    
    if gstin[12] not in "0ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789":
        info["errors"].append("13th entity code looks invalid")
    
    if gstin[13] != "Z":
        info["errors"].append("14th char must be 'Z'")
    
    exp_check = gstin_checksum_calc(gstin[:14])
    if gstin[14] != exp_check:
        info["errors"].append("Checksum mismatch")
        info["expected_checksum"] = exp_check
    
    info["valid"] = len(info["errors"]) == 0
    return info


def validate_invoice_number(inv_no: str) -> Dict[str, Any]:
    info = {"raw": inv_no, "valid": False, "errors": []}
    if not inv_no:
        info["errors"].append("Missing invoice number")
        return info
    inv_no = inv_no.strip()
    info["normalized"] = inv_no
    
    if not re.fullmatch(r"^[A-Za-z0-9\-/]{1,16}$", inv_no):
        info["errors"].append("Invoice no. must be ≤16 chars; only letters, digits, '-' or '/'")
    
    info["valid"] = len(info["errors"]) == 0
    return info


def india_fy_for(d: date) -> str:
    year = d.year
    if d.month < 4:
        start = year - 1
        end = year
    else:
        start = year
        end = year + 1
    return f"{start}-{str(end)[-2:]}"


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        from pdfminer.high_level import extract_text
    except ImportError:
        raise HTTPException(status_code=500, detail="pdfminer.six not installed")
    
    with io.BytesIO(file_bytes) as f:
        return extract_text(f)


FIELD_PATTERNS = {
    "gstin": re.compile(r"GSTIN\s*[:\-]?\s*([0-9A-Z]{15})", re.I),
    "invoice_no": re.compile(r"Invoice\s*(No\.?|Number)\s*[:\-]?\s*([A-Za-z0-9\-/]{1,30})", re.I),
    "invoice_date": re.compile(r"Invoice\s*Date\s*[:\-]?\s*([0-9]{1,2}[^\n]{0,12}[0-9]{2,4})", re.I),
    "place_of_supply": re.compile(r"Place\s*of\s*Supply\s*[:\-]?\s*([^\n]+)", re.I),
    "hsn": re.compile(r"HSN\s*[/:]?\s*([0-9]{4,8})", re.I),
    "taxable_value": re.compile(r"Taxable\s*Value\s*[:\-]?\s*([₹Rs\.\s]*[0-9,]+\.?[0-9]*)", re.I),
    "cgst": re.compile(r"CGST\s*([0-9]+\.?[0-9]*)%\s*([₹Rs\.\s]*[0-9,]+\.?[0-9]*)", re.I),
    "sgst": re.compile(r"SGST\s*([0-9]+\.?[0-9]*)%\s*([₹Rs\.\s]*[0-9,]+\.?[0-9]*)", re.I),
    "igst": re.compile(r"IGST\s*([0-9]+\.?[0-9]*)%\s*([₹Rs\.\s]*[0-9,]+\.?[0-9]*)", re.I),
    "total": re.compile(r"Total\s*[:\-]?\s*([₹Rs\.\s]*[0-9,]+\.?[0-9]*)", re.I),
}

CURRENCY_SAN = re.compile(r"[^0-9.]")


def to_amount(s: Optional[str]) -> Optional[float]:
    if not s:
        return None
    s2 = CURRENCY_SAN.sub("", s)
    try:
        return float(s2) if s2 else None
    except ValueError:
        return None


class CheckResult(BaseModel):
    name: str
    status: str  # PASS, WARN, FAIL, INFO
    message: str
    data: Optional[Dict[str, Any]] = None


class VerifyResponse(BaseModel):
    verdict: str
    score: int
    checks: List[CheckResult]
    extracted: Dict[str, Any]


def verify_invoice_core(extracted: Dict[str, Any]) -> VerifyResponse:
    checks: List[CheckResult] = []
    
    gstin = extracted.get("gstin")
    inv_no = extracted.get("invoice_no")
    inv_date_str = extracted.get("invoice_date")
    place_of_supply = extracted.get("place_of_supply")
    hsn = extracted.get("hsn")
    
    # 1) GSTIN structure
    gst_info = validate_gstin_structure(gstin or "")
    if gst_info["valid"]:
        checks.append(CheckResult(
            name="GSTIN Structure", 
            status="PASS", 
            message="GSTIN structure & checksum valid",
            data=gst_info
        ))
    else:
        checks.append(CheckResult(
            name="GSTIN Structure", 
            status="FAIL", 
            message="; ".join(gst_info["errors"]) or "Invalid GSTIN",
            data=gst_info
        ))
    
    # 2) Invoice number rule
    inv_info = validate_invoice_number(inv_no or "")
    if inv_info["valid"]:
        checks.append(CheckResult(
            name="Invoice Number Format", 
            status="PASS", 
            message="Complies with Rule 46 character/length constraints",
            data=inv_info
        ))
    else:
        checks.append(CheckResult(
            name="Invoice Number Format", 
            status="FAIL", 
            message="; ".join(inv_info["errors"]) or "Invalid format",
            data=inv_info
        ))
    
    # 3) Date parse + FY determination
    fy = None
    if inv_date_str:
        try:
            d = dateparser.parse(inv_date_str, dayfirst=True, fuzzy=True).date()
            fy = india_fy_for(d)
            checks.append(CheckResult(
                name="Invoice Date", 
                status="PASS", 
                message=f"Parsed date {d.isoformat()} (FY {fy})"
            ))
        except Exception:
            checks.append(CheckResult(
                name="Invoice Date", 
                status="FAIL", 
                message="Could not parse invoice date"
            ))
    else:
        checks.append(CheckResult(
            name="Invoice Date", 
            status="FAIL", 
            message="Missing invoice date"
        ))
    
    # 4) Place of supply vs GST state code
    if place_of_supply and gst_info.get("state"):
        state_name = gst_info["state"]["name"]
        if state_name.lower()[:5] in (place_of_supply or "").lower():
            checks.append(CheckResult(
                name="Place of Supply Consistency", 
                status="PASS", 
                message="Place of supply aligns with GSTIN state"
            ))
        else:
            checks.append(CheckResult(
                name="Place of Supply Consistency", 
                status="WARN", 
                message="Place of supply may differ from GSTIN state (can be valid for inter‑state supplies)"
            ))
    else:
        checks.append(CheckResult(
            name="Place of Supply Consistency", 
            status="INFO", 
            message="Insufficient info to compare"
        ))
    
    # 5) HSN sanity
    if hsn:
        if re.fullmatch(r"[0-9]{4,8}", hsn):
            checks.append(CheckResult(
                name="HSN Format", 
                status="PASS", 
                message="HSN format looks valid (4–8 digits)"
            ))
        else:
            checks.append(CheckResult(
                name="HSN Format", 
                status="FAIL", 
                message="HSN must be 4–8 digits"
            ))
    else:
        checks.append(CheckResult(
            name="HSN Format", 
            status="INFO", 
            message="HSN not found"
        ))
    
    # 6) Math checks
    taxable = to_amount(extracted.get("taxable_value"))
    cgst_rate, cgst_amt = extracted.get("cgst_rate"), to_amount(extracted.get("cgst_amount"))
    sgst_rate, sgst_amt = extracted.get("sgst_rate"), to_amount(extracted.get("sgst_amount"))
    igst_rate, igst_amt = extracted.get("igst_rate"), to_amount(extracted.get("igst_amount"))
    total = to_amount(extracted.get("total"))
    
    math_msgs = []
    math_ok = True
    
    def approx_equal(a: Optional[float], b: Optional[float], tol=0.05):
        if a is None or b is None:
            return False
        return abs(a - b) <= tol
    
    tax_sum = None
    if taxable is not None:
        expected_cgst = expected_sgst = expected_igst = None
        
        if cgst_rate:
            expected_cgst = round(taxable * float(cgst_rate) / 100.0, 2)
            if cgst_amt is not None and not approx_equal(cgst_amt, expected_cgst):
                math_ok = False
                math_msgs.append(f"CGST mismatch: got {cgst_amt}, expected ~{expected_cgst}")
        
        if sgst_rate:
            expected_sgst = round(taxable * float(sgst_rate) / 100.0, 2)
            if sgst_amt is not None and not approx_equal(sgst_amt, expected_sgst):
                math_ok = False
                math_msgs.append(f"SGST mismatch: got {sgst_amt}, expected ~{expected_sgst}")
        
        if igst_rate:
            expected_igst = round(taxable * float(igst_rate) / 100.0, 2)
            if igst_amt is not None and not approx_equal(igst_amt, expected_igst):
                math_ok = False
                math_msgs.append(f"IGST mismatch: got {igst_amt}, expected ~{expected_igst}")
        
        tax_sum = (cgst_amt or 0) + (sgst_amt or 0) + (igst_amt or 0)
        
        if total is not None and tax_sum is not None:
            expected_total = round(taxable + tax_sum, 2)
            if not approx_equal(total, expected_total):
                math_ok = False
                math_msgs.append(f"Total mismatch: got {total}, expected ~{expected_total}")
    else:
        math_msgs.append("Taxable value not available; partial math checks only")
    
    if math_ok:
        checks.append(CheckResult(
            name="Arithmetic Checks", 
            status="PASS", 
            message="Taxes and totals consistent within tolerance",
            data={"taxable": taxable, "tax_sum": tax_sum, "total": total}
        ))
    else:
        checks.append(CheckResult(
            name="Arithmetic Checks", 
            status="FAIL", 
            message="; ".join(math_msgs),
            data={"taxable": taxable, "tax_sum": tax_sum, "total": total}
        ))
    
    # 7) Duplicate check (simplified for Vercel)
    checks.append(CheckResult(
        name="Duplicate Check (Local)", 
        status="INFO", 
        message="Duplicate checking disabled in serverless environment"
    ))
    
    # 8) Score & verdict
    score = 0
    weights = {
        "GSTIN Structure": 25,
        "Invoice Number Format": 15,
        "Invoice Date": 10,
        "Place of Supply Consistency": 5,
        "HSN Format": 5,
        "Arithmetic Checks": 30,
        "Duplicate Check (Local)": 10,
    }
    
    for c in checks:
        w = weights.get(c.name, 0)
        if c.status == "PASS":
            score += w
        elif c.status == "WARN":
            score += int(w * 0.5)
    
    verdict = "PASS" if score >= 80 else ("REVIEW" if score >= 60 else "FAIL")
    
    return VerifyResponse(verdict=verdict, score=score, checks=checks, extracted=extracted)


def extract_fields_from_text(txt: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    
    # pull simple fields
    m = FIELD_PATTERNS["gstin"].search(txt)
    if m:
        out["gstin"] = m.group(1).upper()
    
    m = FIELD_PATTERNS["invoice_no"].search(txt)
    if m:
        out["invoice_no"] = m.group(2).strip()
    
    m = FIELD_PATTERNS["invoice_date"].search(txt)
    if m:
        out["invoice_date"] = m.group(1).strip()
    
    m = FIELD_PATTERNS["place_of_supply"].search(txt)
    if m:
        out["place_of_supply"] = m.group(1).strip()
    
    m = FIELD_PATTERNS["hsn"].search(txt)
    if m:
        out["hsn"] = m.group(1).strip()
    
    # amounts
    m = FIELD_PATTERNS["taxable_value"].search(txt)
    if m:
        out["taxable_value"] = m.group(1)
    
    m = FIELD_PATTERNS["cgst"].search(txt)
    if m:
        out["cgst_rate"], out["cgst_amount"] = m.group(1), m.group(2)
    
    m = FIELD_PATTERNS["sgst"].search(txt)
    if m:
        out["sgst_rate"], out["cgst_amount"] = m.group(1), m.group(2)
    
    m = FIELD_PATTERNS["igst"].search(txt)
    if m:
        out["igst_rate"], out["igst_amount"] = m.group(1), m.group(2)
    
    # total (use last match if multiple)
    totals = list(FIELD_PATTERNS["total"].finditer(txt))
    if totals:
        out["total"] = totals[-1].group(1)
    
    return out


# ----------- FastAPI app -----------
app = FastAPI(title="Invoice Verifier Backend", version="0.1.0")


class JSONInvoice(BaseModel):
    vendor_gstin: Optional[str] = None
    invoice_no: Optional[str] = None
    invoice_date: Optional[str] = None
    place_of_supply: Optional[str] = None
    hsn: Optional[str] = None
    taxable_value: Optional[str] = None
    cgst_rate: Optional[float] = None
    cgst_amount: Optional[str] = None
    sgst_rate: Optional[float] = None
    sgst_amount: Optional[str] = None
    igst_rate: Optional[float] = None
    igst_amount: Optional[str] = None
    total: Optional[str] = None


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/")
async def root():
    return {"message": "Invoice Verifier API", "version": "0.1.0", "status": "running"}


@app.post("/verify", response_model=VerifyResponse)
async def verify(
    file: Optional[UploadFile] = File(default=None, description="PDF or image invoice"),
    record: bool = Form(default=False, description="Store invoice number for duplicate checks"),
    json_invoice: Optional[str] = Form(default=None, description="Optional JSON string with fields to override/augment extraction"),
):
    extracted: Dict[str, Any] = {}
    
    if file:
        content = await file.read()
        if file.filename.lower().endswith(".pdf"):
            txt = extract_text_from_pdf(content)
        else:
            raise HTTPException(status_code=400, detail="Only PDF supported in this quickstart. Send JSON if needed.")
        extracted.update(extract_fields_from_text(txt))
    else:
        if not json_invoice:
            raise HTTPException(status_code=400, detail="Provide a PDF file or json_invoice fields")
    
    # Merge/override with provided JSON fields if any
    if json_invoice:
        try:
            payload = json.loads(json_invoice)
            if not isinstance(payload, dict):
                raise ValueError
            extracted.update(payload)
        except Exception:
            raise HTTPException(status_code=400, detail="json_invoice must be a JSON object string")
    
    # Map vendor_gstin if provided
    if extracted.get("vendor_gstin") and not extracted.get("gstin"):
        extracted["gstin"] = extracted["vendor_gstin"]
    
    # Perform verification
    result = verify_invoice_core(extracted)
    
    # Note: Record functionality disabled for Vercel (serverless)
    return result


@app.post("/verify-json", response_model=VerifyResponse)
async def verify_json(payload: JSONInvoice, record: bool = False):
    extracted = payload.dict(exclude_none=True)
    
    # normalize key for gstin
    if extracted.get("vendor_gstin") and not extracted.get("gstin"):
        extracted["gstin"] = extracted["vendor_gstin"]
    
    result = verify_invoice_core(extracted)
    
    # Note: Record functionality disabled for Vercel (serverless)
    return result


# Vercel compatibility - export the app
# This is required for Vercel to recognize the FastAPI app
app.debug = False  # Disable debug mode for production
