from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from routers import invoice
# from routers import tally  # <-- Import the new tally router
from routers import forecast # for forecast the sales
from routers import sales_prediction


app = FastAPI()

# Optional CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
# app.include_router(invoice.router, prefix="/invoices", tags=["Invoices"])
# app.include_router(tally.router, prefix="/tally", tags=["Tally"])  # New tally endpoint
app.include_router(forecast.router, prefix="/forecast",tags=["Forecast"])
app.include_router(sales_prediction.router,prefix="/sales-prediction",tags=["Sales Prediction"])

# --------------------------------------------

# import requests

# # Tally Server details
# TALLY_URL = "http://localhost:9000"

# # XML request to get list of companies
# xml_request = """
# <ENVELOPE>
#     <HEADER>
#         <VERSION>1</VERSION>
#         <TALLYREQUEST>EXPORT</TALLYREQUEST>
#         <TYPE>COLLECTION</TYPE>
#         <ID>List of Companies</ID>
#     </HEADER>
#     <BODY>
#         <DESC>
#             <STATICVARIABLES>
#                 <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
#             </STATICVARIABLES>
#         </DESC>
#     </BODY>
# </ENVELOPE>
# """

# # Send request to Tally
# response = requests.post(TALLY_URL, data=xml_request)
# xml_data = response.text

# # Print the response
# print("Raw XML Response:")
# print(xml_data)

# # Optional: Parse with xml.etree.ElementTree
# import xml.etree.ElementTree as ET
# root = ET.fromstring(xml_data)

# print("\nCompany Names:")
# for company in root.findall(".//COMPANY"):
#     name = company.find("NAME")
#     if name is not None:
#         print(name.text)


#---------------------------------
# import requests

# # XML request to fetch voucher data
# xml_request = """<ENVELOPE>
#  <HEADER>
#   <VERSION>1</VERSION>
#   <TALLYREQUEST>Export</TALLYREQUEST>
#   <TYPE>Collection</TYPE>
#   <ID>Voucher Collection</ID>
#  </HEADER>
#  <BODY>
#   <DESC>
#    <STATICVARIABLES>
#     <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
#     <SVFROMDATE>20240101</SVFROMDATE>
#     <SVTODATE>20241231</SVTODATE>
#    </STATICVARIABLES>
#    <TDL>
#     <TDLMESSAGE>
#      <COLLECTION NAME="Voucher Collection" ISMODIFY="No">
#       <TYPE>Voucher</TYPE>
#       <FETCH>DATE</FETCH>
#       <FETCH>VOUCHERNUMBER</FETCH>
#       <FETCH>PARTYLEDGERNAME</FETCH>
#       <FETCH>ALLLEDGERENTRIES.LIST</FETCH>
#       <FILTERS>IsSales</FILTERS> <!-- Sales Filter -->
#      </COLLECTION>
#     </TDLMESSAGE>
#    </TDL>
#   </DESC>
#  </BODY>
# </ENVELOPE>"""

# # Send request to Tally's HTTP server
# response = requests.post("http://localhost:9000", data=xml_request)

# # Print the raw XML response
# print(response.text)
