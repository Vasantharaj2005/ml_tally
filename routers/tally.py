from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
import httpx
import xml.etree.ElementTree as ET
from typing import Optional, List
import logging
from pydantic import BaseModel

router = APIRouter()

# Configuration
TALLY_URL = "http://100.83.110.70:9000/"  # Adjust if necessary
# TALLY_URL = "http://localhost:9000"  # Adjust if necessary
REQUEST_TIMEOUT = 15  # seconds

# Set up logging
logger = logging.getLogger(__name__)

class VoucherEntry(BaseModel):
    ledger: str
    amount: str
    is_debit: bool

class VoucherData(BaseModel):
    date: str
    voucher_type: str
    reference: str = ""
    narration: str = ""
    ledger_entries: List[VoucherEntry]

@router.get("/company-name")
async def get_company_name():
    """Retrieve list of companies configured in Tally."""
    xml_request = """
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>EXPORT</TALLYREQUEST>
            <TYPE>COLLECTION</TYPE>
            <ID>List of Companies</ID>
        </HEADER>
        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                </STATICVARIABLES>
            </DESC>
        </BODY>
    </ENVELOPE>
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TALLY_URL, 
                data=xml_request, 
                timeout=REQUEST_TIMEOUT,
                headers={"Content-Type": "text/xml"}
            )
            response.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(f"Failed to connect to Tally: {e}")
        return {"error": f"Failed to connect to Tally: {e}"}
    
    try:
        root = ET.fromstring(response.text)
        companies = []
        
        # Primary search path - based on your working code
        company_elements = root.findall(".//COMPANY")
        if company_elements:
            companies = [
                company.find("NAME").text
                for company in company_elements
                if company.find("NAME") is not None
            ]
        
        # Backup paths in case the structure is different
        if not companies:
            paths = [".//COMPANYNAME", ".//COMPANY/DATA/NAME"]
            for path in paths:
                elements = root.findall(path)
                if elements:
                    companies = [element.text for element in elements if element.text]
                    break
        
        return {"company_names": companies}
    except Exception as e:
        logger.error(f"Failed to parse XML: {e}")
        return {"error": f"Failed to parse XML: {e}"}


@router.get("/voucher-codes")
async def get_voucher_codes(
    from_date: Optional[str] = Query(None, description="Start date in YYYYMMDD format"),
    to_date: Optional[str] = Query(None, description="End date in YYYYMMDD format"),
    voucher_type: Optional[str] = Query(None, description="Type of voucher to filter")
):
    """
    Retrieve voucher details from Tally.
    
    If dates are not provided, defaults to current month.
    """
    # Set default date range to current month if not provided
    if not from_date or not to_date:
        today = datetime.now()
        first_day = datetime(today.year, today.month, 1)
        last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        from_date = from_date or first_day.strftime("%Y%m%d")
        to_date = to_date or last_day.strftime("%Y%m%d")
    
    # Build voucher type filter if provided
    voucher_type_filter = f"<VOUCHERTYPENAME>{voucher_type}</VOUCHERTYPENAME>" if voucher_type else ""
    
    # Using your successful format with TDL
    request_xml = f"""
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>Voucher Collection</ID>
        </HEADER>
        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    <EXPLODEFLAG>Yes</EXPLODEFLAG>
                    <SVFROMDATE>{from_date}</SVFROMDATE>
                    <SVTODATE>{to_date}</SVTODATE>
                    {voucher_type_filter}
                </STATICVARIABLES>
                <TDL>
                    <TDLMESSAGE>
                        <COLLECTION NAME="Voucher Collection" ISMODIFY="No">
                            <TYPE>Voucher</TYPE>
                            <FETCH>DATE, VOUCHERNUMBER, VOUCHERTYPENAME, PARTYLEDGERNAME, AMOUNT, NARRATION</FETCH>
                        </COLLECTION>
                    </TDLMESSAGE>
                </TDL>
            </DESC>
        </BODY>
    </ENVELOPE>
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TALLY_URL, 
                data=request_xml, 
                headers={"Content-Type": "text/xml"},
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(f"Failed to connect to Tally: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to connect to Tally: {e}")
    
    try:
        root = ET.fromstring(response.text)
        collection = root.find(".//COLLECTION")
        
        if collection is None:
            return {"vouchers": []}
        
        vouchers = []
        for voucher in collection.findall("VOUCHER"):
            voucher_info = {
                "voucher_number": voucher.findtext("VOUCHERNUMBER", ""),
                "date": voucher.findtext("DATE", ""),
                "type": voucher.findtext("VOUCHERTYPENAME", ""),
                "ledger": voucher.findtext("PARTYLEDGERNAME", ""),
                "amount": voucher.findtext("AMOUNT", "0"),
                "narration": voucher.findtext("NARRATION", ""),
            }
            
            # Only add if we have at least a voucher number
            if voucher_info["voucher_number"]:
                vouchers.append(voucher_info)
        
        return {"vouchers": vouchers}
    
    except Exception as e:
        logger.error(f"Error parsing XML: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing XML: {str(e)}")


@router.get("/ledger-masters")
async def get_ledger_masters():
    """Retrieve all ledger accounts from Tally."""
    # Using TDL approach which seems to work better
    request_xml = """
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>Ledger Collection</ID>
        </HEADER>
        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                </STATICVARIABLES>
                <TDL>
                    <TDLMESSAGE>
                        <COLLECTION NAME="Ledger Collection" ISMODIFY="No">
                            <TYPE>Ledger</TYPE>
                            <FETCH>NAME, PARENT, OPENINGBALANCE, CLOSINGBALANCE</FETCH>
                        </COLLECTION>
                    </TDLMESSAGE>
                </TDL>
            </DESC>
        </BODY>
    </ENVELOPE>
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TALLY_URL, 
                data=request_xml, 
                headers={"Content-Type": "text/xml"},
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(f"Failed to connect to Tally: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to connect to Tally: {e}")
    
    try:
        root = ET.fromstring(response.text)
        collection = root.find(".//COLLECTION")
        
        if collection is None:
            return {"ledgers": []}
        
        ledgers = []
        for ledger in collection.findall("LEDGER"):
            ledger_info = {
                "name": ledger.findtext("NAME", ""),
                "parent": ledger.findtext("PARENT", ""),
                "opening_balance": ledger.findtext("OPENINGBALANCE", "0"),
                "closing_balance": ledger.findtext("CLOSINGBALANCE", "0"),
            }
            
            # Only add if we have a name
            if ledger_info["name"]:
                ledgers.append(ledger_info)
        
        return {"ledgers": ledgers}
    
    except Exception as e:
        logger.error(f"Error parsing XML: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing XML: {str(e)}")


@router.get("/company-info")
async def get_company_info():
    """Retrieve information about the active company in Tally."""
    # Using TDL approach for consistency
    request_xml = """
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>Company Collection</ID>
        </HEADER>
        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                </STATICVARIABLES>
                <TDL>
                    <TDLMESSAGE>
                        <COLLECTION NAME="Company Collection" ISMODIFY="No">
                            <TYPE>Company</TYPE>
                            <FETCH>NAME, ADDRESS, EMAIL, PHONENUMBER, STARTINGFROM, ENDINGAT</FETCH>
                        </COLLECTION>
                    </TDLMESSAGE>
                </TDL>
            </DESC>
        </BODY>
    </ENVELOPE>
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TALLY_URL, 
                data=request_xml, 
                headers={"Content-Type": "text/xml"},
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(f"Failed to connect to Tally: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to connect to Tally: {e}")
    
    try:
        root = ET.fromstring(response.text)
        collection = root.find(".//COLLECTION")
        
        if collection is None:
            return {"error": "No company information found"}
        
        company_element = collection.find("COMPANY")
        if company_element is None:
            return {"error": "No company information found"}
        
        return {
            "company_name": company_element.findtext("NAME", ""),
            "address": company_element.findtext("ADDRESS", ""),
            "email": company_element.findtext("EMAIL", ""),
            "phone": company_element.findtext("PHONENUMBER", ""),
            "financial_year_start": company_element.findtext("STARTINGFROM", ""),
            "financial_year_end": company_element.findtext("ENDINGAT", "")
        }
    
    except Exception as e:
        logger.error(f"Error parsing XML: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing XML: {str(e)}")


@router.post("/create-voucher")
async def create_voucher(voucher_data: VoucherData):
    """
    Create a new voucher in Tally.
    """
    # Format date in YYYYMMDD format if not already
    date_formatted = voucher_data.date
    if len(date_formatted) != 8:
        try:
            # Try to parse and reformat if not in the expected format
            dt = datetime.strptime(date_formatted, "%Y-%m-%d")
            date_formatted = dt.strftime("%Y%m%d")
        except ValueError:
            pass
    
    # Build ledger entries XML for TallyPrime 6
    allledgerentries = ""
    
    for entry in voucher_data.ledger_entries:
        # In TallyPrime 6, we use LIST format and ISDEEMEDPOSITIVE for debit/credit
        is_deemed_positive = "No" if entry.is_debit else "Yes"
        # For proper handling of amounts in TallyPrime 6
        amount_value = entry.amount
        if entry.is_debit:
            # For debits in TallyPrime 6, don't use negative values
            if amount_value.startswith("-"):
                amount_value = amount_value[1:]
        else:
            # For credits, ensure value is positive
            if amount_value.startswith("-"):
                amount_value = amount_value[1:]
        
        allledgerentries += f"""
            <ALLLEDGERENTRIES.LIST>
                <LEDGERNAME>{entry.ledger}</LEDGERNAME>
                <ISDEEMEDPOSITIVE>{is_deemed_positive}</ISDEEMEDPOSITIVE>
                <AMOUNT>{'-' if not entry.is_debit else ''}{amount_value}</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
        """
    
    # TallyPrime 6 compatible XML format
    request_xml = f"""
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Import</TALLYREQUEST>
            <TYPE>Data</TYPE>
            <ID>Vouchers</ID>
        </HEADER>
        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVCURRENTDATE>{date_formatted}</SVCURRENTDATE>
                </STATICVARIABLES>
            </DESC>
            <DATA>
                <TALLYMESSAGE>
                    <VOUCHER>
                        <DATE>{date_formatted}</DATE>
                        <VOUCHERTYPENAME>{voucher_data.voucher_type}</VOUCHERTYPENAME>
                        <REFERENCE>{voucher_data.reference}</REFERENCE>
                        <NARRATION>{voucher_data.narration}</NARRATION>
                        {allledgerentries}
                    </VOUCHER>
                </TALLYMESSAGE>
            </DATA>
        </BODY>
    </ENVELOPE>
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TALLY_URL, 
                data=request_xml, 
                headers={"Content-Type": "text/xml"},
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(f"Failed to connect to Tally: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to connect to Tally: {e}")
    
    # Parse response
    try:
        root = ET.fromstring(response.text)
        # Check if there are any error elements in the response
        errors = root.findall(".//LINEERROR") or root.findall(".//ERROR")
        
        if errors:
            error_messages = [error.text for error in errors if error.text]
            raise HTTPException(status_code=400, detail={"errors": error_messages})
        
        return {"success": True, "message": "Voucher created successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing response: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing response: {str(e)}")


@router.get("/system-status")
async def get_system_status():
    """Check if Tally is accessible and get system status."""
    # Simple request to check connectivity
    request_xml = """
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>EXPORT</TALLYREQUEST>
            <TYPE>COLLECTION</TYPE>
            <ID>List of Companies</ID>
        </HEADER>
        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                </STATICVARIABLES>
            </DESC>
        </BODY>
    </ENVELOPE>
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TALLY_URL, 
                data=request_xml, 
                headers={"Content-Type": "text/xml"},
                timeout=5  # Shorter timeout for status check
            )
            response.raise_for_status()
            
            # If we get here, Tally is responsive
            return {
                "status": "online",
                "message": "Tally is accessible",
                "version": response.headers.get("X-Tally-Version", "Unknown")
            }
            
    except Exception as e:
        logger.error(f"Tally connection check failed: {e}")
        return {
            "status": "offline",
            "message": f"Tally is not accessible: {str(e)}"
        }