import pymupdf  # PyMuPDF
from pathlib import Path

output_dir = Path(__file__).resolve().parent
output_dir.mkdir(parents=True, exist_ok=True)

def create_pdf(filename: str, pages_data: list):
    doc = pymupdf.open()
    for page_info in pages_data:
        page = doc.new_page(width=595, height=842) # A4
        # Header banner
        page.draw_rect(pymupdf.Rect(40, 30, 555, 34), color=(0.1, 0.25, 0.45), fill=(0.1, 0.25, 0.45))
        page.insert_text((45, 52), "GOVERNMENT OF ASSAM — OFFICIAL ADMINISTRATIVE RECORD", fontsize=11, fontname="helv", color=(0.1, 0.25, 0.45))
        page.draw_line((40, 60), (555, 60), color=(0.2, 0.35, 0.55), width=1.5)

        # Title
        page.insert_text((45, 95), page_info["title"], fontsize=13, fontname="hebo", color=(0.08, 0.15, 0.3))
        page.insert_text((45, 115), page_info.get("subtitle", ""), fontsize=9.5, fontname="hebi", color=(0.3, 0.3, 0.3))
        page.draw_line((40, 125), (555, 125), color=(0.7, 0.7, 0.7), width=0.5)

        # Body text with dynamic height
        y_pos = 140
        for para in page_info["paragraphs"]:
            # Count actual lines and wrapped lines
            line_count = sum(max(1, len(l) // 68 + 1) for l in para.split("\n"))
            box_height = line_count * 14 + 18
            rect = pymupdf.Rect(45, y_pos, 550, min(780, y_pos + box_height))
            page.insert_textbox(rect, para, fontsize=9.0, fontname="helv", color=(0.1, 0.1, 0.1), lineheight=1.28)
            y_pos += box_height + 10

        # Official seal / footer
        page.draw_line((40, 790), (555, 790), color=(0.7, 0.7, 0.7), width=0.5)
        page.insert_text((45, 805), f"Document: {filename} | NESFIC-D-36 MVP Demonstration Dataset", fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4))
        page.insert_text((500, 805), f"Page {page_info['page_num']}", fontsize=8, fontname="hebo", color=(0.2, 0.2, 0.2))

    target = output_dir / filename
    doc.save(str(target))
    doc.close()
    print(f"Generated: {target} ({len(pages_data)} pages)")

# 1. Assam Secretariat Manual of Office Procedure
p1_pages = [
    {
        "page_num": 1,
        "title": "ASSAM SECRETARIAT MANUAL OF OFFICE PROCEDURE",
        "subtitle": "Chapter II: Receipt, Registration and Diarisation of Dak (Notification No. AAP.12/2024/31)",
        "paragraphs": [
            "1. Diarisation of Official Communications:\nAll official communications, including letters, memoranda, circulars, and electronic dak addressed to any department of the Assam Secretariat, must be stamped and entered into the Central Dak Register within 24 hours of receipt. The Central Diarising Section shall assign a distinct computer-generated Receipt Number to each communication.",
            "2. Allocation and Movement of Files:\nNo paper shall remain unmarked on an officer's table for more than two consecutive working days. Where inter-departmental reference is necessary, the originating department must clearly flag the precise rule or provision under which the consultation is sought.",
            "3. Marking of Urgent Papers:\nPapers marked 'Immediate' or 'Priority' shall take precedence over ordinary dak. Section Officers are personally responsible for tracking the custody of files marked with Red Urgent Slips."
        ]
    },
    {
        "page_num": 2,
        "title": "ASSAM SECRETARIAT MANUAL OF OFFICE PROCEDURE",
        "subtitle": "Chapter IV: Drafting of Official Notes and Letters (Rule 18 to Rule 24)",
        "paragraphs": [
            "18. Style and Structure of Notes:\nOfficial notes must be concise, objective, and arranged into numbered paragraphs. Paragraph 1 shall state the subject matter and the precise question submitted for orders. Subsequent paragraphs shall recite relevant background facts, statutory rules, precedent cases, and financial implications.",
            "19. Green Note Sheet Integrity:\nAll notes leading to executive decisions shall be drafted exclusively on official green note sheets. No officer shall write running notes on margins of routine communications or omit the date beside their signature.",
            "20. Referencing and Cross-Referencing:\nEvery reference to previously recorded files or gazette notifications must specify the file number, date, and exact page number of the correspondence file (cf. Rule 21(a)). Speculative statements without documentary evidence are strictly prohibited in Secretariat notes."
        ]
    },
    {
        "page_num": 3,
        "title": "ASSAM SECRETARIAT MANUAL OF OFFICE PROCEDURE",
        "subtitle": "Chapter VII: Delegation of Financial and Administrative Powers",
        "paragraphs": [
            "34. Financial Sanction Thresholds:\nUnder the Delegation of Financial Power Rules (DFPR) Assam, Head of Departments may sanction contingent expenditure up to Rs. 2,50,000 per annum without prior concurrence of Finance Department, provided budget allotment under the concerned head is available.",
            "35. Disposal of Obsolete Office Equipment:\nCondemnation of office IT equipment, servers, and computers must follow the recommendations of the Departmental Condemnation Committee comprising the Joint Secretary, Senior Finance Advisor, and a technical representative from AMTRON or NIC.",
            "36. Inspection and Record Preservation:\nSecretariat files classified as 'Category A' (Permanent Records) shall be preserved indefinitely in the State Archives, Dispur. Files classified as 'Category C' may be weeded out after 5 years with the written approval of the Secretary of the concerned department."
        ]
    }
]

# 2. DST & ASSAC Remote Sensing Notification
p2_pages = [
    {
        "page_num": 1,
        "title": "DEPARTMENT OF SCIENCE & TECHNOLOGY — NOTIFICATION",
        "subtitle": "Establishment of State Geo-Spatial Data Repository at ASSAC (No. DST.88/2025/14)",
        "paragraphs": [
            "1. Constitution of Nodal Repository:\nThe Governor of Assam is pleased to designate the Assam State Space Application Centre (ASSAC), Guwahati, as the apex State Nodal Agency for all satellite remote sensing, GIS mapping, and geo-spatial data applications across all state government departments.",
            "2. Mandate of ASSAC:\nASSAC shall maintain the Assam Geo-Spatial Data Infrastructure (AGDI). All drone surveys, river embankment flood vulnerability mappings along the Brahmaputra and Barak rivers, and digital forest land boundaries must be deposited in the central repository managed by ASSAC.",
            "3. Data Sharing Protocol:\nDepartmental users seeking high-resolution satellite imagery or spatial data layers shall submit an official requisition signed by an officer not below the rank of Deputy Secretary. Public domain map services shall be provided through the state geo-portal without commercial charges."
        ]
    },
    {
        "page_num": 2,
        "title": "DEPARTMENT OF SCIENCE & TECHNOLOGY — GUIDELINES",
        "subtitle": "Standard Operating Procedure for Inter-Departmental Drone Surveys (Annexure II)",
        "paragraphs": [
            "4. Clearance for Aerial Surveys:\nAny department commissioning drone or UAV surveys for infrastructure projects or disaster management must obtain prior security clearance through the Home & Political Department and technical vetting by ASSAC.",
            "5. Quality Standards and Coordinate Systems:\nAll spatial data generated for Assam Government projects must adhere strictly to the WGS84 Datum and UTM projection. Digital elevation models (DEM) must maintain a vertical accuracy within 0.5 meters for flood inundation analysis.",
            "6. Data Custody and Security:\nUnder no circumstances shall raw point cloud data or survey outputs be hosted on foreign or uncertified cloud servers. Data must reside within MeghRaj or state-approved data centers in Guwahati."
        ]
    }
]

# 3. AASC Training Policy Guidelines
p3_pages = [
    {
        "page_num": 1,
        "title": "ASSAM ADMINISTRATIVE STAFF COLLEGE (AASC)",
        "subtitle": "State Training Policy & Capacity Building Directives for State Civil Services (AASC/TRG/2025/08)",
        "paragraphs": [
            "1. Mandatory Training Requirement:\nIn pursuance of the State Training Policy, every gazetted officer of the Government of Assam, including Assam Civil Service (ACS) and Assam Police Service (APS), must undergo a minimum of 10 working days of in-service capacity building training at AASC Khanapara every two years.",
            "2. Focus Areas for Digital Governance:\nSpecial mandatory modules on e-Office, cyber security compliance, citizen service delivery under the Assam Right to Public Services Act (ARTPS), and AI-driven document intelligence must be incorporated into all foundational and mid-career training programs.",
            "3. Nomination and Attendance Protocol:\nDeputing departments must relieve nominated officers on duty for the entire duration of the course. Unauthorized absence or leave during training sessions shall be reported directly to the Personnel Department for entry into the officer's Annual Performance Appraisal Report (APAR)."
        ]
    },
    {
        "page_num": 2,
        "title": "ASSAM ADMINISTRATIVE STAFF COLLEGE (AASC)",
        "subtitle": "Guidelines on Departmental Inquiries and Disciplinary Proceedings (Module IV)",
        "paragraphs": [
            "4. Procedure for Disciplinary Enquiries:\nInquiries under Rule 9 of the Assam Services (Discipline & Appeal) Rules, 1964 must be completed within six months from the date of appointment of the Inquiring Authority. Delay beyond this period requires formal extension from the Disciplinary Authority with recorded reasons.",
            "5. Right of Representation:\nThe delinquent government servant must be provided all relied-upon documents along with the statement of allegations. Failure to supply copies of official records listed in the charge sheet vitiates the inquiry on grounds of natural justice.",
            "6. Penalty Guidelines:\nMajor penalties, including compulsory retirement, removal, or dismissal from service, can only be imposed with the concurrence of the Assam Public Service Commission (APPSC) where statutory consultation is mandated."
        ]
    }
]

# 4. Assam Services Pension Rules Circular
p4_pages = [
    {
        "page_num": 1,
        "title": "GOVERNMENT OF ASSAM - PENSION & PUBLIC GRIEVANCES DEPT.",
        "subtitle": "Circular on Timely Settlement of Pensionary Benefits and Gratuity (No. PPG(P) 142/2024/5)",
        "paragraphs": [
            "1. Strict Adherence to Timelines:\nUnder the Assam Services (Pension) Rules, 1969, the processing of pension papers must commence exactly two years prior to the date of superannuation of the government employee. The Head of Office shall ensure that the verified service book and Form 1 are forwarded to the Accountant General (A&E) Assam at least six months before retirement.",
            "2. Death-cum-Retirement Gratuity (DCRG):\nThe maximum ceiling for Death-cum-Retirement Gratuity for Assam State Government employees has been revised to Rs. 20,00,000 (Rupees Twenty Lakhs) with effect from the notified cutoff date.",
            "3. Provisional Pension Authorization:\nWhere final pension cannot be determined prior to retirement due to pending departmental verification of qualifying service, the Head of Office is empowered to sanction 100% Provisional Pension for a period not exceeding six months, ensuring that retired employees do not suffer financial hardship."
        ]
    }
]

# 5. Assam Pension Rules, 2024
p5_pages = [
    {
        "page_num": 1,
        "title": "ASSAM SERVICES (PENSION) RULES, 2024",
        "subtitle": "Chapter III: Pension Sanction Procedure & Documents Checklist (Notification No. PPG.2024/PR-01)",
        "paragraphs": [
            "3. Processing of Pension",
            "3.1 Initiation of Pension Processing:\nThe Head of Office shall initiate the preparation of pension papers of every government servant exactly two years (24 months) prior to the anticipated date of retirement on superannuation.",
            "3.2 Documents required. - The following documents shall be furnished for processing a pension case:\n(i) Service record of the employee (complete and up to date);\n(ii) Retirement order / relieving order issued by the appointing authority;\n(iii) Pension application in the prescribed form (Form 1);\n(iv) Last pay certificate and other emolument details;\n(v) No dues certificate / No demand certificate (as applicable);\n(vi) Bank account details (Aadhaar-seeded) for pension payment."
        ]
    },
    {
        "page_num": 2,
        "title": "ASSAM SERVICES (PENSION) RULES, 2024",
        "subtitle": "Chapter III: Verification, Incomplete Records & Forwarding Mandates",
        "paragraphs": [
            "3.3 Verification of Qualifying Service:\nThe Head of Office shall verify the qualifying service of the retiring employee with reference to the entries in the service book at least 24 months prior to the date of superannuation.",
            "3.4 Procedure when Service Book or Record is Incomplete:\nWhere any period of qualifying service cannot be verified from the service book or where entries are missing, the Head of Office shall not return the pension case to the employee. The Head of Office shall initiate collateral reconstruction using appointment letters, establishment pay rolls, or an affidavit by the employee attested by two gazetted colleagues. Pending reconstruction of the qualifying service, the Head of Office is empowered to sanction 100% Provisional Pension for a period not exceeding six months.",
            "3.5 Forwarding Authority and Six-Month Deadline:\nThe Head of Office shall act as the forwarding authority, ensuring that the verified service book and Form 1 pension papers are forwarded to the Accountant General (A&E) Assam at least six months before retirement."
        ]
    }
]

# 6. Pension Processing Guidelines (OM)
p6_pages = [
    {
        "page_num": 1,
        "title": "OFFICE MEMORANDUM - PENSION PROCESSING GUIDELINES",
        "subtitle": "Department of Pension & Public Grievances (No. PPG(P).92/2024/18) - Prescribed Checklist",
        "paragraphs": [
            "Para 1 - Standardized Timeline: Every department under the Government of Assam must adhere strictly to the timelines for superannuation settlement. The pension preparation must commence 24 months before retirement, and the final dossier must be forwarded to the Accountant General (A&E) Assam not later than six months prior to the date of superannuation.",
            "Para 2 - List of required documents:\nFor speedy settlement of superannuation pension and timely issuance of Pension Payment Orders (PPO), the applicant employee and the sanctioning authority must attach all prerequisite documents including:\n(i) Verified Service Book complete with all annual verification certificates and leave accounts;\n(ii) Formal Retirement Order / Superannuation Notification issued by the competent appointing authority;\n(iii) Pension Application in prescribed Form 1 along with Form 1A (Family Details);\n(iv) Last Pay Certificate (LPC) duly countersigned by the Drawing and Disbursing Officer (DDO);\n(v) No Demand / No Dues Certificate from Government Estates and departmental stores;\n(vi) Three copies of joint passport photographs with spouse and attested specimen signatures / left-hand thumb impressions;\n(vii) Duly executed Nomination Forms for Death-cum-Retirement Gratuity (DCRG) and Commutation Application (Form 2);\n(viii) Active Bank Passbook copy showing Account Number and IFSC Code for electronic Direct Benefit Transfer (DBT).\nAll Treasury Officers and Disbursing Authorities across Assam must ensure compliance without demanding redundant certificates."
        ]
    },
    {
        "page_num": 2,
        "title": "OFFICE MEMORANDUM - PENSION PROCESSING GUIDELINES",
        "subtitle": "Department of Pension & Public Grievances (No. PPG(P).92/2024/18) - Part II: Irregularities & Transmission",
        "paragraphs": [
            "Para 3 - Action on Incomplete Service Records:\nIf the Service Book of a retiring employee is incomplete or missing verification stamps for certain periods, the pension sanctioning authority shall proceed with collateral verification on the basis of pay acquittance rolls or written employee declaration. The Head of Office shall not withhold the case and shall sanction 100% Provisional Pension and provisional gratuity for up to six months so that the pensioner receives immediate sustenance without interruption.",
            "Para 4 - Forwarding Authority:\nThe Head of Office (HOO) / Appointing Authority is the statutory forwarding authority and shall directly transmit the verified pension dossier and Form 1 to the Director of Pension, Assam or the Accountant General (A&E) Assam."
        ]
    }
]

if __name__ == "__main__":
    create_pdf("Assam_Secretariat_Manual_of_Office_Procedure.pdf", p1_pages)
    create_pdf("DST_ASSAC_Remote_Sensing_Notification.pdf", p2_pages)
    create_pdf("AASC_State_Training_Policy_Guidelines.pdf", p3_pages)
    create_pdf("Assam_Pension_Rules_Circular_No_142.pdf", p4_pages)
    create_pdf("Assam_Pension_Rules,_2024.pdf", p5_pages)
    create_pdf("Pension_Processing_Guidelines_(OM).pdf", p6_pages)
