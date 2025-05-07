# routers/tally.py

from fastapi import APIRouter
import requests
import xml.etree.ElementTree as ET

router = APIRouter()

TALLY_URL = "http://localhost:9000"  # Adjust if necessary

@router.get("/company-name")
def get_company_name():
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
        response = requests.post(TALLY_URL, data=xml_request, timeout=5)
        response.raise_for_status()
    except Exception as e:
        return {"error": f"Failed to connect to Tally: {e}"}

    try:
        root = ET.fromstring(response.text)
        companies = [
            company.find("NAME").text
            for company in root.findall(".//COMPANY")
            if company.find("NAME") is not None
        ]
        return {"company_names": companies}
    except Exception as e:
        return {"error": f"Failed to parse XML: {e}"}


@router.get("/voucher-codes")
def get_voucher_codes():
    request_xml = """
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
                <SVFROMDATE>20240401</SVFROMDATE>
                <SVTODATE>20250401</SVTODATE>
            </STATICVARIABLES>
            <TDL>
                <TDLMESSAGE>
                    <COLLECTION NAME="Voucher Collection" ISMODIFY="No">
                        <TYPE>Voucher</TYPE>
                        <FETCH>DATE, VOUCHERNUMBER, PARTYLEDGERNAME, AMOUNT, NARRATION</FETCH>
                    </COLLECTION>
                </TDLMESSAGE>
            </TDL>
        </DESC>
    </BODY>
</ENVELOPE>

    """

    try:
        response = requests.post(TALLY_URL, data=request_xml, headers={"Content-Type": "text/xml"})
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to connect to Tally: {e}")

    try:
        root = ET.fromstring(response.text)
        collection = root.find(".//COLLECTION")

        if collection is None:
            return {"Response": []}

        voucher_codes = []

        for voucher in collection.findall("VOUCHER"):
            code = voucher.findtext("VOUCHERNUMBER")
            date = voucher.findtext("DATE")
            ledger = voucher.findtext("PARTYLEDGERNAME")
            if code:
                voucher_codes.append({
                    "voucher_number": code,
                    "date": date,
                    "ledger": ledger
                })

        return {"codes": voucher_codes}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing XML: {str(e)}")
