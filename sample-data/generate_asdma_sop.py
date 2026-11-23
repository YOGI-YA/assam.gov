import pymupdf
from pathlib import Path

output_dir = Path(__file__).resolve().parent
output_dir.mkdir(parents=True, exist_ok=True)

def create_pdf(filename: str, pages_data: list):
    doc = pymupdf.open()
    for page_info in pages_data:
        page = doc.new_page(width=595, height=842) # A4
        # Header banner
        page.draw_rect(pymupdf.Rect(40, 30, 555, 34), color=(0.7, 0.15, 0.15), fill=(0.7, 0.15, 0.15))
        page.insert_text((45, 52), "GOVERNMENT OF ASSAM • ASSAM STATE DISASTER MANAGEMENT AUTHORITY (ASDMA)", fontsize=9.5, fontname="helv", color=(0.1, 0.25, 0.45))
        page.draw_line((40, 60), (555, 60), color=(0.6, 0.2, 0.2), width=1.5)

        # Title
        page.insert_text((45, 95), page_info["title"], fontsize=12.5, fontname="hebo", color=(0.15, 0.1, 0.2))
        page.insert_text((45, 115), page_info.get("subtitle", ""), fontsize=9.5, fontname="hebi", color=(0.3, 0.3, 0.3))
        page.draw_line((40, 125), (555, 125), color=(0.7, 0.7, 0.7), width=0.5)

        # Body text
        y_pos = 145
        for para in page_info["paragraphs"]:
            rect = pymupdf.Rect(45, y_pos, 550, y_pos + 150)
            page.insert_textbox(rect, para, fontsize=9.2, fontname="helv", color=(0.1, 0.1, 0.1), lineheight=1.35)
            lines = len(para) // 68 + 2
            y_pos += max(45, lines * 13 + 14)

        # Footer
        page.draw_line((40, 790), (555, 790), color=(0.7, 0.7, 0.7), width=0.5)
        page.insert_text((45, 805), "ASDMA Disaster Response SOP & SDRF Manual | Revenue & Disaster Management Dept", fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4))
        page.insert_text((500, 805), f"Page {page_info['page_num']}", fontsize=8, fontname="hebo", color=(0.2, 0.2, 0.2))

    target = output_dir / filename
    doc.save(str(target))
    doc.close()
    print(f"Generated: {target} ({len(pages_data)} pages)")

asdma_pages = [
    {
        "page_num": 1,
        "title": "ASDMA DISASTER RESPONSE & EMERGENCY STANDARD OPERATING PROCEDURE (SOP)",
        "subtitle": "Standing Order No. ASDMA/DM/2023/SOP-09 • Citizen Action, Evacuation & Incident Control",
        "paragraphs": [
            "1. Immediate Actions for Citizens Facing a Disaster (Floods, Landslides, Embankment Breach):\nAny person or community facing an active natural disaster, flash flood, embankment breach, or severe landslide in Assam must immediately undertake the following emergency actions:\n(i) Evacuate immediately to the nearest pre-designated Flood Relief Camp, multi-purpose shelter, or raised highland platform designated by the District Disaster Management Authority (DDMA).\n(ii) Contact the 24x7 Emergency Operation Centre: Call the District Emergency Operation Centre (DEOC) on toll-free emergency number 1077, or the State Emergency Operation Centre (SEOC) at Dispur on toll-free number 1070.\n(iii) Alert the local Gaon Burah (Village Headman) and the Field Officer (Disaster Management) of the Revenue Circle for rescue coordination and State Disaster Response Force (SDRF) or National Disaster Response Force (NDRF) boat deployment.\n(iv) Do not cross flooded roads, embankments with active breaches, or walk through flowing floodwaters.",
            "2. Incident Command Structure and Local First Responders:\nThe Revenue Circle Officer (CO) serves as the Sub-Divisional Incident Commander under the Disaster Management Act, 2005. The Circle Officer mobilizes rescue teams, coordinates emergency shelter logistics, deploys mechanized country boats, and arranges medical first aid through Circle Health Officers under the overarching supervision of the Deputy Commissioner cum Chairperson, District Disaster Management Authority (DDMA)."
        ]
    },
    {
        "page_num": 2,
        "title": "ASSAM STATE DISASTER RESPONSE FUND (SDRF) RELIEF ELIGIBILITY & ASSISTANCE NORMS",
        "subtitle": "Notification No. R&DM/SDRF/REVI-2023/45 • Scale of Gratuitous Relief & Financial Grants",
        "paragraphs": [
            "3. Nature, Scope, and Legal Principles of Relief Assistance:\nFinancial and material relief provided under the State Disaster Response Fund (SDRF) and National Disaster Response Fund (NDRF) is gratuitous humanitarian assistance designed exclusively for the immediate relief of distress; it is NOT commercial compensation for damage or loss of property. Relief assistance cannot be claimed as an automatic entitlement by all affected citizens. Assistance is strictly subject to: (a) formal notification of the calamity by the Government of Assam; (b) physical verification by revenue authorities; and (c) fulfillment of specific statutory eligibility criteria under SDRF guidelines.",
            "4. Categories of Relief Assistance and Approved Scales:\n(i) Gratuitous Relief (GR): Free supply of daily food rations (rice, dal, salt, mustard oil), baby food, clean drinking water packets, halogen tablets, cattle fodder, and tarpaulin/polythene sheets to families formally registered as inmates in approved relief camps or marooned habitations.\n(ii) Ex-Gratia Assistance for Loss of Life: ₹4,00,000/- per deceased person paid to the next of kin, subject to mandatory police General Diary (GD) entry, post-mortem report, and formal inquiry certification by the Revenue Circle Officer.\n(iii) Housing Assistance for Damaged Dwellings: Fully damaged or destroyed house: ₹1,20,000/- in hilly/difficult areas and ₹95,100/- in plain areas. Partially damaged pucca house: ₹6,500/-. Partially damaged kutcha house: ₹4,000/-. Subject to joint physical assessment by Revenue Lot Mandal and PWD engineer.\n(iv) Crop Loss Assistance: Agricultural input subsidy provided exclusively to small and marginal farmers whose crop loss exceeds 33% of the total cultivated land holding."
        ]
    },
    {
        "page_num": 3,
        "title": "RELIEF CLAIM PROCEDURE, VERIFICATION PROTOCOL & MANDATORY DOCUMENTATION",
        "subtitle": "Notification No. R&DM/SDRF/08/2024 • Three-Tier Verification & Direct Benefit Transfer (DBT)",
        "paragraphs": [
            "5. Responsible District Authority for Relief Sanction:\nThe apex sanctioning authority for all disaster relief and financial grants in each district is the District Disaster Management Authority (DDMA), headed by the Deputy Commissioner (DC) as Chairperson. No financial disbursement can be executed without the formal approval and sanction order of the DDMA.",
            "6. Three-Tier Field Verification Procedure:\nTo receive SDRF housing, livestock, or agricultural assistance, the citizen must undergo mandatory three-tier verification:\nStep 1 (Field Enumeration): On-ground damage enumeration conducted jointly by the Lot Mandal (Revenue Collector), Gaon Burah, and Field Officer (DM).\nStep 2 (Circle Certification): Scrutiny and formal countersignature of the verified damage list by the Revenue Circle Officer.\nStep 3 (DDMA Sanction & Disbursement): Final approval by the Deputy Commissioner cum DDMA Chairperson and electronic Direct Benefit Transfer (DBT) directly into the beneficiary's Aadhaar-linked bank account.",
            "7. Mandatory Documentation Required for Relief Claims:\nEvery claimant must furnish the following documents:\n(a) Certified Field Damage Verification Report signed jointly by the Lot Mandal and Circle Officer;\n(b) Proof of Identity and Residence (Aadhaar Card, Voter Identity Card, or Ration Card);\n(c) Active Bank Passbook copy showing Account Number and IFSC Code (Aadhaar-seeded for DBT);\n(d) Geo-tagged photographs of the damaged structure or verified relief camp registration inmate slip;\n(e) In cases of loss of life: Police inquest/GD entry, post-mortem certificate, and legal heir certificate issued by the District Magistrate."
        ]
    }
]

if __name__ == "__main__":
    create_pdf("ASDMA_Disaster_Management_SOP_and_Relief_Manual.pdf", asdma_pages)
