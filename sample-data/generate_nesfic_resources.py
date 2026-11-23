import pymupdf
from pathlib import Path

output_dir = Path(__file__).resolve().parent
output_dir.mkdir(parents=True, exist_ok=True)

def create_pdf(filename: str, pages_data: list):
    doc = pymupdf.open()
    for page_info in pages_data:
        page = doc.new_page(width=595, height=842) # A4
        # Header banner
        page.draw_rect(pymupdf.Rect(40, 30, 555, 34), color=(0.08, 0.22, 0.38), fill=(0.08, 0.22, 0.38))
        page.insert_text((45, 52), "GOVERNMENT OF ASSAM • NESFIC 2026 OFFICIAL RESOURCE COMPENDIUM", fontsize=10, fontname="helv", color=(0.1, 0.25, 0.45))
        page.draw_line((40, 60), (555, 60), color=(0.2, 0.35, 0.55), width=1.5)

        # Title
        page.insert_text((45, 95), page_info["title"], fontsize=13, fontname="hebo", color=(0.08, 0.15, 0.3))
        page.insert_text((45, 115), page_info.get("subtitle", ""), fontsize=9.5, fontname="hebi", color=(0.3, 0.3, 0.3))
        page.draw_line((40, 125), (555, 125), color=(0.7, 0.7, 0.7), width=0.5)

        # Body text
        y_pos = 145
        for para in page_info["paragraphs"]:
            rect = pymupdf.Rect(45, y_pos, 550, y_pos + 130)
            page.insert_textbox(rect, para, fontsize=9.5, fontname="helv", color=(0.1, 0.1, 0.1), lineheight=1.35)
            lines = len(para) // 68 + 2
            y_pos += max(45, lines * 13 + 12)

        # Footer
        page.draw_line((40, 790), (555, 790), color=(0.7, 0.7, 0.7), width=0.5)
        page.insert_text((45, 805), f"NESFIC 2026 Portal Resources | Startup Assam & Dept. of Science & Technology", fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4))
        page.insert_text((500, 805), f"Page {page_info['page_num']}", fontsize=8, fontname="hebo", color=(0.2, 0.2, 0.2))

    target = output_dir / filename
    doc.save(str(target))
    doc.close()
    print(f"Generated: {target} ({len(pages_data)} pages)")

nesfic_pages = [
    {
        "page_num": 1,
        "title": "NESFIC 2026 — STATE GEOSPATIAL & OPEN DATA PORTALS",
        "subtitle": "Apex Public Portals for Data and Geospatial Research in Assam",
        "paragraphs": [
            "1. Data.gov.in (Open Government Data Platform India — www.data.gov.in):\nData.gov.in is the national open government data portal mandated by the National Data Sharing and Accessibility Policy (NDSAP). It provides high-value public datasets, APIs, and statistical catalogs published by state departments and central ministries, including Assam socio-economic metrics, agricultural yields, and departmental indicators.",
            "2. Geospatial Data Catalogue (catalogue.geospatial.org.in):\nThe National Spatial Data Infrastructure (NSDI) metadata portal provides centralized discovery for geographic information, raster and vector datasets, and spatial thematic layers collected by national and state agencies across the North Eastern region.",
            "3. Bhuvan Geo-Portal (bhuvan.nrsc.gov.in):\nMaintained by the National Remote Sensing Centre (NRSC) / ISRO, Bhuvan provides multi-resolution satellite imagery, thematic spatial datasets, digital elevation models, and real-time disaster support services. For Assam, Bhuvan hosts high-priority flood inundation layers and river basin mappings along the Brahmaputra valley.",
            "4. VEDAS (vedas.sac.gov.in/en/):\nVisualisation of Earth Observation Data and Archival System developed by Space Applications Centre (SAC), ISRO. VEDAS offers environmental applications, vegetation indices, crop monitoring, solar potential, and land degradation mapping across Assam."
        ]
    },
    {
        "page_num": 2,
        "title": "NESFIC 2026 — REGIONAL SPATIAL & METEOROLOGICAL PLATFORMS",
        "subtitle": "Satellite, Climate and Online Mapping Repositories for Assam",
        "paragraphs": [
            "5. MOSDAC (Meteorological & Oceanographic Satellite Data Archival Centre — www.mosdac.gov.in):\nMOSDAC archives satellite missions from INSAT-3D, INSAT-3DR, and Oceansat, delivering operational meteorological forecasts, rainfall estimates, cloud motion vectors, and severe weather warnings for the North Eastern region.",
            "6. Survey of India Online Maps (onlinemaps.surveyofindia.gov.in/):\nThe National Survey and Mapping Organization provides Open Series Maps (OSM) at 1:50,000 scale, geodetic control networks, and digital base maps for administrative boundary demarcations across Assam districts.",
            "7. Assam State Geoportal (gistcp.assam.gov.in/geoportal/index.aspx):\nOperated by the Directorate of Town & Country Planning, Government of Assam, the state geoportal offers GIS base layers, municipal master plans, land-use zoning maps, and spatial planning data for urban and semi-urban growth corridors.",
            "8. North Eastern Spatial Data Repository — Assam (www.nesdr.gov.in/assam/):\nMaintained by North Eastern Space Applications Centre (NESAC), Department of Space, NESDR Assam provides comprehensive spatial layers covering Brahmaputra river embankment monitoring, forest canopy density, wetland boundaries, and tea garden demarcations."
        ]
    },
    {
        "page_num": 3,
        "title": "NESFIC 2026 — STATISTICAL & DISASTER MANAGEMENT AUTHORITIES",
        "subtitle": "Directorate of Economics & Statistics and ASDMA Knowledge Context",
        "paragraphs": [
            "9. Directorate of Economics and Statistics, Assam (des.assam.gov.in/):\nDES Assam is the apex statistical agency of the Government of Assam. It compiles the State Domestic Product (GSDP), Economic Survey of Assam, Statistical Handbooks, Consumer Price Indices (CPI), and district-level demographic surveys necessary for evidence-based governance.",
            "10. Assam State Disaster Management Authority (asdma.assam.gov.in/):\nASDMA coordinates disaster risk reduction, flood mitigation, and emergency response across 35 districts in Assam. ASDMA produces the comprehensive Flood Hazard Atlas of Assam, district disaster management plans (DDMP), early warning integration with ASSAC and CWC, and disaster relief standard operating procedures.",
            "11. Uniform Solution Proposal Requirements (uspr.pdf — startup.assam.gov.in/nesfic26/docs/uspr.pdf):\nMandatory structural guidelines for all NESFIC 2026 challenge submissions, covering Problem Understanding & User Workflow, Solution Architecture, Technical Feasibility, Data & Geospatial Integration, and Implementation Readiness."
        ]
    }
]

if __name__ == "__main__":
    create_pdf("NESFIC_2026_Official_State_Geospatial_and_Open_Data_Resources.pdf", nesfic_pages)
