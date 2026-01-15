"""
Generate Full Compliance Data for CPIC Solutions A and B
Based on Design Documents:
- Solution A: 9 Investments, 134 Forms
- Solution B: 15 Investments, 185 Forms
"""

import json

# ============================================================================
# SOLUTION A: 9 CONSOLIDATED INVESTMENTS (MODERNIZATION APPROACH)
# ============================================================================

# 9 Investments aligned with IRS IT Organizational Structure
INVESTMENTS_A = [
    # MISSION-FOCUSED INVESTMENTS (4)
    {
        "investment_id": "INV-01", "uii": "015-000000001",
        "name": "Taxpayer Services Modernization", "short_name": "TSM",
        "description": "Digital taxpayer services including Online Account, IRS.gov, Direct File, and self-service tools",
        "category": "MISSION", "investment_type": "major-it",
        "cd_owner": "Jim Keith", "cd_title": "Coordinating Director - Taxpayer Services",
        "rd_team": ["Joe Gibbons"], "re_team": ["Mike Donaldson", "Greg Ellis"], "pm_team": ["John Bursie"],
        "budget_fy25": 456000000, "current_phase": "CONTROL", "health": "green",
        "sub_projects": 12, "cost_variance": -2.1, "schedule_days": 0
    },
    {
        "investment_id": "INV-02", "uii": "015-000000002",
        "name": "Tax Processing Transformation", "short_name": "TPT",
        "description": "Core tax processing including CADE 2, IMF replacement, MeF, and return processing systems",
        "category": "MISSION", "investment_type": "major-it",
        "cd_owner": "Miji Mathews", "cd_title": "Coordinating Director - Tax Processing",
        "rd_team": ["Rangam Subramanian"], "re_team": ["Pavan Vemuri"], "pm_team": ["Lillie Wilburn"],
        "budget_fy25": 389000000, "current_phase": "CONTROL", "health": "green",
        "sub_projects": 15, "cost_variance": 1.5, "schedule_days": 5
    },
    {
        "investment_id": "INV-03", "uii": "015-000000003",
        "name": "Compliance Systems Enhancement", "short_name": "CSE",
        "description": "Examination, collection, ACA, and criminal investigation systems",
        "category": "MISSION", "investment_type": "major-it",
        "cd_owner": "Eric Markow", "cd_title": "Coordinating Director - Compliance",
        "rd_team": ["Andrew Hanna"], "re_team": ["Eric R. Smith", "Mohan Vasa"], "pm_team": ["James Vergauwen"],
        "budget_fy25": 234000000, "current_phase": "CONTROL", "health": "yellow",
        "sub_projects": 8, "cost_variance": 8.2, "schedule_days": 15
    },
    {
        "investment_id": "INV-04", "uii": "015-000000004",
        "name": "Filing Season Infrastructure", "short_name": "FSI",
        "description": "Filing season readiness, legislative changes, refund processing, and annual updates",
        "category": "MISSION", "investment_type": "major-it",
        "cd_owner": "Craig Drake", "cd_title": "Coordinating Director - Filing Season",
        "rd_team": ["Gbemi Acholonu"], "re_team": ["Larry Bullock"], "pm_team": [],
        "budget_fy25": 178000000, "current_phase": "CONTROL", "health": "green",
        "sub_projects": 6, "cost_variance": -1.0, "schedule_days": -3
    },
    # FOUNDATIONAL INVESTMENTS (5)
    {
        "investment_id": "INV-05", "uii": "015-000000005",
        "name": "API Platform & Integration", "short_name": "API",
        "description": "Enterprise APIs, microservices platform, and integration services",
        "category": "FOUNDATIONAL", "investment_type": "major-it",
        "cd_owner": "Rob King", "cd_title": "Coordinating Director - API Platform",
        "rd_team": ["George Contos", "Brian Wright"], "re_team": ["Erek Borowski", "Shane Smith"], "pm_team": ["Tony Antonious"],
        "budget_fy25": 145000000, "current_phase": "CONTROL", "health": "green",
        "sub_projects": 10, "cost_variance": 0.5, "schedule_days": 0
    },
    {
        "investment_id": "INV-06", "uii": "015-000000006",
        "name": "Enterprise Infrastructure", "short_name": "EI",
        "description": "Data centers, cloud services, network, storage, and compute infrastructure",
        "category": "FOUNDATIONAL", "investment_type": "major-it",
        "cd_owner": "Lou Capece", "cd_title": "Coordinating Director - Infrastructure",
        "rd_team": ["Shelderick Bailey", "Babu V."], "re_team": ["Lou Ferraro", "Val Mance"], "pm_team": ["Haren Punatar"],
        "budget_fy25": 312000000, "current_phase": "CONTROL", "health": "green",
        "sub_projects": 14, "cost_variance": 2.0, "schedule_days": 0
    },
    {
        "investment_id": "INV-07", "uii": "015-000000007",
        "name": "Cybersecurity & Privacy", "short_name": "CSP",
        "description": "Security operations, identity management, threat protection, and privacy compliance",
        "category": "FOUNDATIONAL", "investment_type": "major-it",
        "cd_owner": "Houman Rasouli", "cd_title": "Coordinating Director - Cybersecurity",
        "rd_team": ["Shelia Walker"], "re_team": ["Anthony Gillespie", "Jaret Trail"], "pm_team": ["Ajeesh Cherian"],
        "budget_fy25": 267000000, "current_phase": "CONTROL", "health": "yellow",
        "sub_projects": 9, "cost_variance": 12.5, "schedule_days": 10
    },
    {
        "investment_id": "INV-08", "uii": "015-000000008",
        "name": "End User Digital Services", "short_name": "EUDS",
        "description": "Employee workstations, collaboration tools, and productivity suite",
        "category": "FOUNDATIONAL", "investment_type": "non-major-it",
        "cd_owner": "Tanya Chiaravalle", "cd_title": "Coordinating Director - End User Services",
        "rd_team": ["Kafi Grigsby", "Dave Potock"], "re_team": ["Tony Early"], "pm_team": ["LaShawndra Bills"],
        "budget_fy25": 98000000, "current_phase": "CONTROL", "health": "green",
        "sub_projects": 5, "cost_variance": 1.0, "schedule_days": 0
    },
    {
        "investment_id": "INV-09", "uii": "015-000000009",
        "name": "IT Strategy & PMO", "short_name": "SPMO",
        "description": "IT strategy, enterprise architecture, portfolio management, and governance",
        "category": "FOUNDATIONAL", "investment_type": "non-major-it",
        "cd_owner": "Courtney Williams", "cd_title": "Coordinating Director - Strategy & PMO",
        "rd_team": ["Melissa Kaminin"], "re_team": [], "pm_team": ["Folashade Pullen"],
        "budget_fy25": 67000000, "current_phase": "STEADY_STATE", "health": "green",
        "sub_projects": 4, "cost_variance": 0.0, "schedule_days": 0
    }
]

# Investment-Level Forms (6 forms × 9 investments = 54 forms)
INVESTMENT_LEVEL_FORMS_A = [
    {"form_code": "INV-MSR", "form_name": "Investment Monthly Status Report", "frequency": "Monthly", "owner_role": "CD"},
    {"form_code": "INV-BCR", "form_name": "Investment Baseline Change Request", "frequency": "As Needed", "owner_role": "CD"},
    {"form_code": "INV-RAR", "form_name": "Investment Risk Assessment Report", "frequency": "Quarterly", "owner_role": "RD"},
    {"form_code": "INV-BUD", "form_name": "Investment Budget Request", "frequency": "Annual", "owner_role": "CD"},
    {"form_code": "INV-PIR", "form_name": "Investment Post-Implementation Review", "frequency": "Per Release", "owner_role": "CD"},
    {"form_code": "INV-HLT", "form_name": "Investment Health Self-Assessment", "frequency": "Quarterly", "owner_role": "CD"}
]

# Project-Level Forms (5 forms per project, ~83 projects = ~415 instances)
PROJECT_LEVEL_FORMS_A = [
    {"form_code": "PRJ-STS", "form_name": "Project Status Report", "frequency": "Bi-weekly", "owner_role": "PM"},
    {"form_code": "PRJ-EVM", "form_name": "Earned Value Report", "frequency": "Monthly", "owner_role": "PM"},
    {"form_code": "PRJ-RSK", "form_name": "Risk Register Update", "frequency": "Weekly", "owner_role": "RE"},
    {"form_code": "PRJ-CHG", "form_name": "Change Request", "frequency": "As Needed", "owner_role": "PM"},
    {"form_code": "PRJ-QAG", "form_name": "Quality Gate Checklist", "frequency": "Per Milestone", "owner_role": "RE"}
]

# Generate 134 forms for Solution A (as per design: 15 PRESELECT + 24 SELECT + 80 CONTROL + 15 EVALUATE)
def generate_forms_solution_a():
    forms = []
    form_counter = 1

    # PRESELECT Phase Forms (15)
    preselect_forms = [
        ("Strategic Planning Document", "SPD", "Strategy"),
        ("Needs Identification Report", "NIR", "Business Analysis"),
        ("Initial Screening Criteria", "ISC", "Governance"),
        ("Preliminary Business Case", "PBC", "Investment Planning"),
        ("Portfolio Prioritization Request", "PPR", "Strategy"),
        ("Mission Alignment Assessment", "MAA", "Strategy"),
        ("Resource Availability Check", "RAC", "Resource Management"),
        ("Technical Feasibility Study", "TFS", "Enterprise Architecture"),
        ("Budget Authority Request", "BAR", "Financial Analysis"),
        ("Stakeholder Identification", "SID", "Strategy"),
        ("Initial Risk Screening", "IRS", "Risk Management"),
        ("Capability Gap Assessment", "CGA", "Enterprise Architecture"),
        ("Investment Proposal Draft", "IPD", "Investment Planning"),
        ("CIO Endorsement Request", "CER", "Governance"),
        ("IRB Submission Package", "ISP", "Governance")
    ]
    for name, code, area in preselect_forms:
        inv_id = f"INV-0{(form_counter % 9) + 1}"
        forms.append({
            "form_id": f"CPIC-{form_counter:03d}",
            "form_name": name,
            "form_code": f"{code}-001",
            "functional_area": area,
            "investment_id": inv_id,
            "cpic_phase": "Preselect",
            "fiscal_year": 2025,
            "status": "Approved" if form_counter % 3 == 0 else "In Review",
            "risk_level": "Low" if form_counter % 4 != 0 else "Medium"
        })
        form_counter += 1

    # SELECT Phase Forms (24)
    select_forms = [
        ("OMB Exhibit 300 Business Case", "BC-300", "Investment Planning"),
        ("Investment Screening Criteria", "ISC", "Investment Planning"),
        ("Alternatives Analysis", "AA", "Investment Planning"),
        ("Cost-Benefit Analysis", "CBA", "Financial Analysis"),
        ("Risk Assessment Detailed", "RAD", "Risk Management"),
        ("Strategic Alignment Assessment", "SAA", "Strategy"),
        ("Architecture Review Request", "ARR", "Enterprise Architecture"),
        ("Security Requirements Document", "SRD", "Cybersecurity"),
        ("Investment Proposal Final", "IPF", "Investment Planning"),
        ("Stakeholder Analysis Complete", "SAC", "Strategy"),
        ("Capability Gap Analysis Final", "CGAF", "Enterprise Architecture"),
        ("Resource Requirements Plan", "RRP", "Resource Management"),
        ("Procurement Strategy", "PS", "Acquisition"),
        ("Performance Measures Plan", "PMP", "Performance"),
        ("IRB Review Package", "IRP", "Governance"),
        ("EA Compliance Certification", "EAC", "Enterprise Architecture"),
        ("Privacy Impact Assessment Initial", "PIA-I", "Privacy"),
        ("Section 508 Assessment", "S508", "Compliance"),
        ("Budget Formulation Package", "BFP", "Financial Analysis"),
        ("Governance Structure Plan", "GSP", "Governance"),
        ("Communication Plan", "CP", "Strategy"),
        ("Training Needs Assessment", "TNA", "Training"),
        ("Transition Planning Document", "TPD", "Project Management"),
        ("CIO Approval Package", "CAP", "Governance")
    ]
    for name, code, area in select_forms:
        inv_id = f"INV-0{(form_counter % 9) + 1}"
        forms.append({
            "form_id": f"CPIC-{form_counter:03d}",
            "form_name": name,
            "form_code": f"{code}-001",
            "functional_area": area,
            "investment_id": inv_id,
            "cpic_phase": "Select",
            "fiscal_year": 2025,
            "status": "Approved" if form_counter % 2 == 0 else "Completed",
            "risk_level": "Low" if form_counter % 3 != 0 else "Medium"
        })
        form_counter += 1

    # CONTROL Phase Forms (80)
    control_forms = [
        ("Monthly Status Report", "MSR", "Reporting"),
        ("Baseline Change Request", "BCR", "Change Management"),
        ("Earned Value Management Report", "EVM", "Financial Analysis"),
        ("Risk Register Update", "RRU", "Risk Management"),
        ("TechStat Review Preparation", "TSP", "Governance"),
        ("Contractor Performance Report", "CPR", "Acquisition"),
        ("Quality Assurance Report", "QAR", "Quality"),
        ("Security Assessment Report", "SAR", "Cybersecurity"),
        ("Project Schedule Update", "PSU", "Project Management"),
        ("Budget Execution Report", "BER", "Financial Analysis"),
        ("Release Management Plan", "RMP", "Development"),
        ("Infrastructure Change Request", "ICR", "Infrastructure"),
        ("Testing Progress Report", "TPR", "Quality"),
        ("Privacy Impact Assessment", "PIA", "Privacy"),
        ("Authority to Operate Request", "ATO", "Cybersecurity"),
        ("Data Quality Report", "DQR", "Data Management"),
        ("Training Status Report", "TSR", "Training"),
        ("Operational Readiness Review", "ORR", "Operations"),
        ("CIO Evaluation Comments", "CEC", "Governance"),
        ("Treasury DO Report", "TDR", "Reporting"),
        ("OMB ITDB Submission", "ITDB", "Reporting"),
        ("FITARA Compliance Report", "FCR", "Compliance"),
        ("Enterprise License Agreement", "ELA", "Acquisition"),
        ("Cloud Migration Status", "CMS", "Infrastructure"),
        ("DevSecOps Maturity Assessment", "DMA", "Development"),
        ("Incident Response Report", "IRR", "Cybersecurity"),
        ("Accessibility Compliance", "AC", "Compliance"),
        ("API Governance Report", "AGR", "Enterprise Architecture"),
        ("System Health Dashboard", "SHD", "Operations"),
        ("Technical Debt Assessment", "TDA", "Development"),
        ("Workforce Planning Report", "WPR", "Resource Management"),
        ("Disaster Recovery Test Report", "DRT", "Operations"),
        ("Capacity Planning Report", "CAPR", "Infrastructure"),
        ("Change Advisory Board Minutes", "CAB", "Change Management"),
        ("Sprint Review Summary", "SRS", "Development"),
        ("Vendor Performance Scorecard", "VPS", "Acquisition"),
        ("Integration Testing Report", "ITR", "Quality"),
        ("User Acceptance Testing", "UAT", "Quality"),
        ("Deployment Checklist", "DCL", "Operations"),
        ("Configuration Management Report", "CMR", "Operations"),
        ("Performance Baseline Update", "PBU", "Performance"),
        ("Scope Change Impact Analysis", "SCIA", "Change Management"),
        ("Schedule Variance Report", "SVR", "Project Management"),
        ("Cost Variance Report", "CVR", "Financial Analysis"),
        ("Resource Utilization Report", "RUR", "Resource Management"),
        ("Milestone Achievement Report", "MAR", "Project Management"),
        ("Issue Resolution Log", "IRL", "Project Management"),
        ("Decision Log Update", "DLU", "Governance"),
        ("Action Item Tracker", "AIT", "Project Management"),
        ("Communication Status", "CS", "Strategy"),
        ("Stakeholder Engagement Report", "SER", "Strategy"),
        ("Benefits Tracking Report", "BTR", "Performance"),
        ("Quality Metrics Dashboard", "QMD", "Quality"),
        ("Security Posture Report", "SPR", "Cybersecurity"),
        ("Compliance Status Report", "CSR", "Compliance"),
        ("EA Alignment Review", "EAR", "Enterprise Architecture"),
        ("Data Architecture Update", "DAU", "Enterprise Architecture"),
        ("Technology Stack Report", "TSTR", "Development"),
        ("Infrastructure Capacity Report", "ICPR", "Infrastructure"),
        ("Network Performance Report", "NPR", "Infrastructure"),
        ("Database Performance Report", "DPR", "Infrastructure"),
        ("Application Performance Report", "APR", "Development"),
        ("User Experience Report", "UXR", "Development"),
        ("Agile Velocity Report", "AVR", "Development"),
        ("Sprint Burndown Chart", "SBC", "Development"),
        ("Product Backlog Status", "PBS", "Development"),
        ("Feature Completion Report", "FCR2", "Development"),
        ("Bug Resolution Report", "BRR", "Quality"),
        ("Code Review Summary", "CRS", "Development"),
        ("Technical Review Report", "TRR", "Enterprise Architecture"),
        ("Environment Status Report", "ESR", "Infrastructure"),
        ("Release Readiness Report", "RRR", "Development"),
        ("Go-Live Checklist", "GLC", "Operations"),
        ("Hypercare Status Report", "HSR", "Operations"),
        ("Knowledge Base Update", "KBU", "Training"),
        ("Support Ticket Analysis", "STA", "Operations"),
        ("SLA Performance Report", "SLAPR", "Operations"),
        ("Availability Report", "AVL", "Operations"),
        ("SPIKE Submission Package", "SSP", "Reporting"),
        ("Executive Dashboard Update", "EDU", "Reporting")
    ]
    for name, code, area in control_forms:
        inv_id = f"INV-0{(form_counter % 9) + 1}"
        forms.append({
            "form_id": f"CPIC-{form_counter:03d}",
            "form_name": name,
            "form_code": f"{code}-001",
            "functional_area": area,
            "investment_id": inv_id,
            "cpic_phase": "Control",
            "fiscal_year": 2025,
            "status": ["Active", "In Progress", "Completed", "Pending"][form_counter % 4],
            "risk_level": ["Low", "Low", "Medium", "Low"][form_counter % 4]
        })
        form_counter += 1

    # EVALUATE Phase Forms (15)
    evaluate_forms = [
        ("Post-Implementation Review", "PIR", "Evaluation"),
        ("Operational Analysis", "OA", "Evaluation"),
        ("Benefits Realization Report", "BRR2", "Evaluation"),
        ("Customer Satisfaction Survey", "CSS", "Evaluation"),
        ("Performance Metrics Review", "PMR", "Performance"),
        ("Total Cost of Ownership", "TCO", "Financial Analysis"),
        ("Lessons Learned", "LL", "Evaluation"),
        ("Investment Continuation Assessment", "ICA", "Investment Planning"),
        ("Technology Refresh Assessment", "TRA", "Enterprise Architecture"),
        ("Portfolio Optimization Review", "POR", "Strategy"),
        ("Service Level Achievement", "SLA", "Operations"),
        ("Operational Efficiency Report", "OER", "Operations"),
        ("User Adoption Report", "UAR", "Evaluation"),
        ("Business Value Assessment", "BVA", "Evaluation"),
        ("Investment Closeout Report", "ICR2", "Investment Planning")
    ]
    for name, code, area in evaluate_forms:
        inv_id = f"INV-0{(form_counter % 9) + 1}"
        forms.append({
            "form_id": f"CPIC-{form_counter:03d}",
            "form_name": name,
            "form_code": f"{code}-001",
            "functional_area": area,
            "investment_id": inv_id,
            "cpic_phase": "Evaluate",
            "fiscal_year": 2025,
            "status": ["Active", "Scheduled", "Pending", "Draft"][form_counter % 4],
            "risk_level": "Low"
        })
        form_counter += 1

    return forms

# ============================================================================
# SOLUTION B: 15 CURRENT INVESTMENTS (MAINTAIN & OPTIMIZE APPROACH)
# ============================================================================

INVESTMENTS_B = [
    # MAJOR INVESTMENTS (5) - OMB Exhibit 300, CIO Ratings, TechStat Eligible
    {
        "investment_id": "INV-001", "uii": "015-000000001",
        "name": "Customer Account Data Engine 2 (CADE 2)", "short_name": "CADE2",
        "description": "Core tax account database modernization - Individual Master File replacement",
        "category": "MAJOR", "investment_type": "major-it",
        "primary_owner": "Miji Mathews", "secondary_owner": "Rangam Subramanian",
        "oversight_cd": "Tax Processing",
        "budget_fy25": 234500000, "current_phase": "CONTROL", "health": "yellow",
        "cio_rating": 3, "exhibit_300": True, "techstat_eligible": True,
        "cost_variance": 8.5, "schedule_days": 30
    },
    {
        "investment_id": "INV-002", "uii": "015-000000002",
        "name": "Modernized e-File (MeF)", "short_name": "MeF",
        "description": "Electronic tax return filing system modernization",
        "category": "MAJOR", "investment_type": "major-it",
        "primary_owner": "Rangam Subramanian", "secondary_owner": "Pavan Vemuri",
        "oversight_cd": "Tax Processing",
        "budget_fy25": 89300000, "current_phase": "CONTROL", "health": "green",
        "cio_rating": 4, "exhibit_300": True, "techstat_eligible": True,
        "cost_variance": 1.0, "schedule_days": 0
    },
    {
        "investment_id": "INV-003", "uii": "015-000000003",
        "name": "Affordable Care Act Systems", "short_name": "ACA",
        "description": "ACA compliance, reporting, and enforcement systems",
        "category": "MAJOR", "investment_type": "major-it",
        "primary_owner": "Eric Markow", "secondary_owner": "Andrew Hanna",
        "oversight_cd": "Compliance",
        "budget_fy25": 67200000, "current_phase": "CONTROL", "health": "green",
        "cio_rating": 4, "exhibit_300": True, "techstat_eligible": True,
        "cost_variance": 0.5, "schedule_days": 0
    },
    {
        "investment_id": "INV-004", "uii": "015-000000004",
        "name": "Enterprise Case Management (ECC)", "short_name": "ECC",
        "description": "Unified case management for examination, collection, and appeals",
        "category": "MAJOR", "investment_type": "major-it",
        "primary_owner": "Andrew Hanna", "secondary_owner": "Eric R. Smith",
        "oversight_cd": "Compliance",
        "budget_fy25": 78400000, "current_phase": "CONTROL", "health": "yellow",
        "cio_rating": 2, "exhibit_300": True, "techstat_eligible": True,
        "cost_variance": 12.0, "schedule_days": 20
    },
    {
        "investment_id": "INV-005", "uii": "015-000000005",
        "name": "IRS.gov Modernization", "short_name": "IRSGOV",
        "description": "Public website modernization and digital services enhancement",
        "category": "MAJOR", "investment_type": "major-it",
        "primary_owner": "Jim Keith", "secondary_owner": "Joe Gibbons",
        "oversight_cd": "Taxpayer Services",
        "budget_fy25": 45600000, "current_phase": "CONTROL", "health": "green",
        "cio_rating": 4, "exhibit_300": True, "techstat_eligible": True,
        "cost_variance": -1.5, "schedule_days": 0
    },
    # SIGNIFICANT INVESTMENTS (5) - Exhibit 53
    {
        "investment_id": "INV-006", "uii": "015-000000006",
        "name": "Individual Online Account (IOA)", "short_name": "IOA",
        "description": "Taxpayer self-service online account platform",
        "category": "SIGNIFICANT", "investment_type": "significant-it",
        "primary_owner": "Jim Keith", "secondary_owner": "Mike Donaldson",
        "oversight_cd": "Taxpayer Services",
        "budget_fy25": 67800000, "current_phase": "CONTROL", "health": "green",
        "exhibit_53": True, "cost_variance": 2.0, "schedule_days": 5
    },
    {
        "investment_id": "INV-007", "uii": "015-000000007",
        "name": "Business Tax Account (BTA)", "short_name": "BTA",
        "description": "Business taxpayer online account and services",
        "category": "SIGNIFICANT", "investment_type": "significant-it",
        "primary_owner": "Joe Gibbons", "secondary_owner": "Greg Ellis",
        "oversight_cd": "Taxpayer Services",
        "budget_fy25": 45200000, "current_phase": "CONTROL", "health": "green",
        "exhibit_53": True, "cost_variance": 0.0, "schedule_days": 0
    },
    {
        "investment_id": "INV-008", "uii": "015-000000008",
        "name": "W-2/1099 Matching", "short_name": "W2MATCH",
        "description": "Information return matching and verification systems",
        "category": "SIGNIFICANT", "investment_type": "significant-it",
        "primary_owner": "Pavan Vemuri", "secondary_owner": "Lillie Wilburn",
        "oversight_cd": "Tax Processing",
        "budget_fy25": 34100000, "current_phase": "CONTROL", "health": "green",
        "exhibit_53": True, "cost_variance": 1.5, "schedule_days": 0
    },
    {
        "investment_id": "INV-009", "uii": "015-000000009",
        "name": "Refund Processing Systems", "short_name": "REFUND",
        "description": "Tax refund issuance and tracking systems",
        "category": "SIGNIFICANT", "investment_type": "significant-it",
        "primary_owner": "Craig Drake", "secondary_owner": "Gbemi Acholonu",
        "oversight_cd": "Filing Season",
        "budget_fy25": 56700000, "current_phase": "CONTROL", "health": "green",
        "exhibit_53": True, "cost_variance": -0.5, "schedule_days": -3
    },
    {
        "investment_id": "INV-010", "uii": "015-000000010",
        "name": "Compliance Analytics Platform", "short_name": "CAP",
        "description": "Data analytics for compliance and fraud detection",
        "category": "SIGNIFICANT", "investment_type": "significant-it",
        "primary_owner": "Mohan Vasa", "secondary_owner": "James Vergauwen",
        "oversight_cd": "Compliance",
        "budget_fy25": 89400000, "current_phase": "SELECT", "health": "yellow",
        "exhibit_53": True, "cost_variance": 5.0, "schedule_days": 10
    },
    # INFRASTRUCTURE INVESTMENTS (5)
    {
        "investment_id": "INV-011", "uii": "015-000000011",
        "name": "Data Center Consolidation", "short_name": "DCC",
        "description": "Data center modernization and consolidation initiative",
        "category": "INFRASTRUCTURE", "investment_type": "infrastructure",
        "primary_owner": "Lou Capece", "secondary_owner": "Shelderick Bailey",
        "oversight_cd": "Infrastructure",
        "budget_fy25": 78300000, "current_phase": "CONTROL", "health": "green",
        "cost_variance": 0.0, "schedule_days": 0
    },
    {
        "investment_id": "INV-012", "uii": "015-000000012",
        "name": "Enterprise Network Services", "short_name": "ENS",
        "description": "WAN, LAN, and telecommunications infrastructure",
        "category": "INFRASTRUCTURE", "investment_type": "infrastructure",
        "primary_owner": "Lou Ferraro", "secondary_owner": "Val Mance",
        "oversight_cd": "Infrastructure",
        "budget_fy25": 45600000, "current_phase": "CONTROL", "health": "green",
        "cost_variance": 1.5, "schedule_days": 0
    },
    {
        "investment_id": "INV-013", "uii": "015-000000013",
        "name": "Cybersecurity & Privacy", "short_name": "CYBER",
        "description": "Enterprise security operations and privacy compliance",
        "category": "INFRASTRUCTURE", "investment_type": "infrastructure",
        "primary_owner": "Houman Rasouli", "secondary_owner": "Shelia Walker",
        "oversight_cd": "Cybersecurity",
        "budget_fy25": 267000000, "current_phase": "CONTROL", "health": "yellow",
        "cost_variance": 12.5, "schedule_days": 10
    },
    {
        "investment_id": "INV-014", "uii": "015-000000014",
        "name": "Cloud First Initiative", "short_name": "CLOUD",
        "description": "Cloud adoption and migration program",
        "category": "INFRASTRUCTURE", "investment_type": "infrastructure",
        "primary_owner": "Rob King", "secondary_owner": "George Contos",
        "oversight_cd": "API Platform",
        "budget_fy25": 123400000, "current_phase": "SELECT", "health": "green",
        "cost_variance": 3.0, "schedule_days": 0
    },
    {
        "investment_id": "INV-015", "uii": "015-000000015",
        "name": "Enterprise Mail/Document", "short_name": "MAIL",
        "description": "Enterprise mail and document management services",
        "category": "INFRASTRUCTURE", "investment_type": "infrastructure",
        "primary_owner": "Tanya Chiaravalle", "secondary_owner": "Kafi Grigsby",
        "oversight_cd": "End User Services",
        "budget_fy25": 34200000, "current_phase": "EVALUATE", "health": "green",
        "cost_variance": 0.0, "schedule_days": 0
    }
]

# Generate 185 forms for Solution B (75 Major + 50 Significant + 60 Infrastructure)
def generate_forms_solution_b():
    forms = []
    form_counter = 1

    # MAJOR Investment Forms (5 investments × 15 forms = 75 forms)
    major_forms = [
        ("OMB Exhibit 300 Business Case", "MAJ-300", "Investment Planning", "Annual"),
        ("Monthly Status Report", "MAJ-STS", "Reporting", "Monthly"),
        ("Earned Value Management Report", "MAJ-EVM", "Financial Analysis", "Monthly"),
        ("Risk Assessment & Mitigation", "MAJ-RSK", "Risk Management", "Quarterly"),
        ("Baseline Change Request", "MAJ-BCR", "Change Management", "As Needed"),
        ("Quality Gate Certification", "MAJ-QAG", "Quality", "Per Milestone"),
        ("Security Compliance Report", "MAJ-SEC", "Cybersecurity", "Quarterly"),
        ("Vendor Performance Report", "MAJ-VND", "Acquisition", "Quarterly"),
        ("Post-Implementation Review", "MAJ-PIR", "Evaluation", "Per Release"),
        ("CIO Rating Self-Assessment", "MAJ-CIO", "Governance", "Monthly"),
        ("TechStat Preparation Package", "MAJ-TST", "Governance", "As Needed"),
        ("GAO Audit Support Package", "MAJ-GAO", "Compliance", "As Needed"),
        ("Budget Execution Report", "MAJ-BUD", "Financial Analysis", "Monthly"),
        ("Acquisition Status Report", "MAJ-ACQ", "Acquisition", "Monthly"),
        ("Benefits Realization Report", "MAJ-BEN", "Evaluation", "Quarterly")
    ]

    for inv_idx in range(1, 6):  # 5 Major investments
        inv_id = f"INV-{inv_idx:03d}"
        for form_name, form_code, area, freq in major_forms:
            forms.append({
                "form_id": f"CPIC-{form_counter:03d}",
                "form_name": form_name,
                "form_code": f"{form_code}-{inv_idx:03d}",
                "functional_area": area,
                "investment_id": inv_id,
                "category": "MAJOR",
                "frequency": freq,
                "cpic_phase": "Control",
                "fiscal_year": 2025,
                "status": ["Active", "Submitted", "Approved", "Pending"][form_counter % 4],
                "risk_level": ["Low", "Low", "Medium", "Low"][form_counter % 4],
                "cio_rating_applicable": True,
                "exhibit_300_required": True
            })
            form_counter += 1

    # SIGNIFICANT Investment Forms (5 investments × 10 forms = 50 forms)
    significant_forms = [
        ("Exhibit 53 Submission", "SIG-053", "Investment Planning", "Annual"),
        ("Monthly Status Report", "SIG-STS", "Reporting", "Monthly"),
        ("Milestone Tracking Report", "SIG-MLT", "Project Management", "Monthly"),
        ("Risk Register Update", "SIG-RSK", "Risk Management", "Monthly"),
        ("Change Request", "SIG-BCR", "Change Management", "As Needed"),
        ("Quality Gate Checklist", "SIG-QAG", "Quality", "Per Milestone"),
        ("Security Status", "SIG-SEC", "Cybersecurity", "Quarterly"),
        ("Post-Implementation Review", "SIG-PIR", "Evaluation", "Per Release"),
        ("Budget Status", "SIG-BUD", "Financial Analysis", "Monthly"),
        ("Health Self-Assessment", "SIG-HLT", "Governance", "Monthly")
    ]

    for inv_idx in range(6, 11):  # 5 Significant investments
        inv_id = f"INV-{inv_idx:03d}"
        for form_name, form_code, area, freq in significant_forms:
            forms.append({
                "form_id": f"CPIC-{form_counter:03d}",
                "form_name": form_name,
                "form_code": f"{form_code}-{inv_idx:03d}",
                "functional_area": area,
                "investment_id": inv_id,
                "category": "SIGNIFICANT",
                "frequency": freq,
                "cpic_phase": "Control",
                "fiscal_year": 2025,
                "status": ["Active", "Submitted", "Completed", "In Review"][form_counter % 4],
                "risk_level": "Low",
                "exhibit_53_required": True
            })
            form_counter += 1

    # INFRASTRUCTURE Investment Forms (5 investments × 12 forms = 60 forms)
    infrastructure_forms = [
        ("Capacity Planning Report", "INF-CAP", "Infrastructure", "Monthly"),
        ("Service Status Report", "INF-STS", "Operations", "Monthly"),
        ("SLA/SLO Performance Report", "INF-SLA", "Operations", "Monthly"),
        ("Security Posture Assessment", "INF-SEC", "Cybersecurity", "Monthly"),
        ("Change Request (CAB)", "INF-CHG", "Change Management", "As Needed"),
        ("Incident Report", "INF-INC", "Operations", "As Needed"),
        ("DR/BC Validation Report", "INF-DRP", "Operations", "Quarterly"),
        ("Technology Refresh Plan", "INF-REF", "Enterprise Architecture", "Annual"),
        ("Vendor/SLA Review", "INF-VND", "Acquisition", "Monthly"),
        ("Architecture Compliance", "INF-ARC", "Enterprise Architecture", "Quarterly"),
        ("Infrastructure Budget", "INF-BUD", "Financial Analysis", "Monthly"),
        ("Infrastructure Project Status", "INF-PRJ", "Project Management", "Monthly")
    ]

    for inv_idx in range(11, 16):  # 5 Infrastructure investments
        inv_id = f"INV-{inv_idx:03d}"
        for form_name, form_code, area, freq in infrastructure_forms:
            forms.append({
                "form_id": f"CPIC-{form_counter:03d}",
                "form_name": form_name,
                "form_code": f"{form_code}-{inv_idx:03d}",
                "functional_area": area,
                "investment_id": inv_id,
                "category": "INFRASTRUCTURE",
                "frequency": freq,
                "cpic_phase": "Control",
                "fiscal_year": 2025,
                "status": ["Active", "Completed", "In Progress", "Scheduled"][form_counter % 4],
                "risk_level": ["Low", "Low", "Medium", "Low"][form_counter % 4],
                "cab_required": True,
                "sla_monitoring": True
            })
            form_counter += 1

    return forms

# Role Permissions for Solution A
ROLE_PERMISSIONS_A = {
    'CIO': {
        'level': 0,
        'view': ['all_investments', 'all_projects', 'executive_dashboard', 'all_forms'],
        'approve': ['investment_reports', 'irb_submissions', 'budget_requests', 'techstat'],
        'edit': []
    },
    'Coordinating_Director': {
        'level': 1,
        'view': ['own_investment', 'own_projects', 'investment_dashboard', 'investment_forms'],
        'approve': ['project_reports', 'bcr_under_5m', 'risk_medium', 'monthly_reports'],
        'edit': ['own_investment_forms']
    },
    'Resource_Director': {
        'level': 2,
        'view': ['own_investment', 'resource_dashboard', 'resource_forms'],
        'approve': ['resource_allocations', 'project_scope_under_500k'],
        'edit': ['resource_forms', 'project_reports']
    },
    'Responsible_Engineer': {
        'level': 3,
        'view': ['own_projects', 'technical_dashboard', 'technical_forms'],
        'approve': ['technical_reviews', 'quality_gates'],
        'edit': ['technical_forms', 'risk_register']
    },
    'Product_Manager': {
        'level': 4,
        'view': ['own_projects', 'product_dashboard', 'project_forms'],
        'approve': [],
        'edit': ['project_status', 'sprint_reports', 'backlog']
    },
    'Admin': {
        'level': 0,
        'view': ['all'],
        'approve': ['all'],
        'edit': ['all']
    }
}

# Role Permissions for Solution B
ROLE_PERMISSIONS_B = {
    'CIO': {
        'level': 0,
        'view': ['all_15_investments', 'all_categories', 'executive_dashboard', 'all_forms'],
        'approve': ['major_cio_ratings', 'techstat_decisions', 'irb_final', 'exhibit_300'],
        'edit': []
    },
    'Portfolio_Manager': {
        'level': 1,
        'view': ['all_15_investments', 'portfolio_dashboard', 'all_forms'],
        'approve': ['spike_submissions', 'bcr_over_threshold'],
        'edit': ['portfolio_reports']
    },
    'Major_Investment_Owner': {
        'level': 2,
        'view': ['own_major_investment', 'major_dashboard', 'major_forms'],
        'approve': ['exhibit_300', 'evm_reports', 'cio_rating_draft', 'techstat_prep'],
        'edit': ['major_forms']
    },
    'Significant_Investment_Owner': {
        'level': 2,
        'view': ['own_significant_investment', 'significant_dashboard', 'significant_forms'],
        'approve': ['exhibit_53', 'milestone_reports'],
        'edit': ['significant_forms']
    },
    'Infrastructure_Investment_Owner': {
        'level': 2,
        'view': ['own_infrastructure_investment', 'infrastructure_dashboard', 'infrastructure_forms'],
        'approve': ['capacity_plans', 'change_requests_cab', 'sla_reports'],
        'edit': ['infrastructure_forms']
    },
    'Investment_Manager': {
        'level': 3,
        'view': ['assigned_investment', 'operational_dashboard', 'operational_forms'],
        'approve': [],
        'edit': ['status_reports', 'risk_updates']
    },
    'Program_Manager': {
        'level': 4,
        'view': ['assigned_projects', 'project_dashboard', 'project_forms'],
        'approve': ['project_milestones'],
        'edit': ['project_forms', 'schedule_updates']
    },
    'Product_Manager': {
        'level': 5,
        'view': ['assigned_features', 'product_dashboard'],
        'approve': [],
        'edit': ['feature_status', 'backlog']
    },
    'Admin': {
        'level': 0,
        'view': ['all'],
        'approve': ['all'],
        'edit': ['all']
    }
}

# 8 Workflows for both solutions
WORKFLOWS = [
    {
        "id": "WF-01", "name": "Investment Creation & Approval",
        "phase": "PRESELECT-SELECT", "duration": "8-12 weeks",
        "steps": [
            "Strategic Planning", "Needs Identification", "Initial Screening",
            "Preliminary Business Case", "Portfolio Prioritization", "IRB Review", "CIO Approval"
        ],
        "forms_required": ["SPD-001", "NIR-001", "ISC-001", "PBC-001", "PPR-001", "IRB-001"],
        "solution_a": "Full process for sub-projects",
        "solution_b": "Category-specific (Major: Full, Significant: Abbreviated, Infrastructure: Technical)"
    },
    {
        "id": "WF-02", "name": "Baseline Change Request (BCR)",
        "phase": "CONTROL", "duration": "2-4 weeks",
        "steps": [
            "PM identifies need", "BCR Form in SPIKE", "IPM Review",
            "Treasury CPIC Review", "OMB Notification", "IT Dashboard Update"
        ],
        "forms_required": ["BCR-001", "SCIA-001"],
        "thresholds": {"warning": "10% variance", "critical": "30% variance"},
        "solution_a": "Investment-level BCRs",
        "solution_b": "Major: CCB Required, Significant: Manager Approval, Infrastructure: CAB Required"
    },
    {
        "id": "WF-03", "name": "Monthly Reporting Cycle",
        "phase": "CONTROL", "duration": "10-15 days",
        "deadline": "15th of month (internal), 19th of month (SPIKE/OMB)",
        "steps": [
            "Data Collection (1st-15th)", "Portfolio Manager Review (15th-17th)",
            "CIO Comments (17th-18th)", "SPIKE Submission (19th)"
        ],
        "forms_required": ["MSR-001", "EVM-001", "RRU-001", "CEC-001"],
        "solution_a": "9 Investment Reports consolidated",
        "solution_b": "15 Investment Reports (Major + Significant + Infrastructure)"
    },
    {
        "id": "WF-04", "name": "Project Initiation",
        "phase": "SELECT-CONTROL", "duration": "2-3 weeks",
        "steps": [
            "Project Charter", "Kickoff Meeting", "Baseline Establishment",
            "Resource Assignment", "Schedule Creation"
        ],
        "forms_required": ["PCH-001", "RRP-001", "PMP-001"],
        "solution_a": "Sub-project initiation under investment",
        "solution_b": "Major: PMO Full, Significant: PMO Standard, Infrastructure: ITIL Aligned"
    },
    {
        "id": "WF-05", "name": "Risk Escalation & TechStat",
        "phase": "CONTROL", "duration": "1-2 weeks",
        "steps": [
            "Risk Identification", "Impact Assessment", "CIO Notification",
            "TechStat Scheduling", "Evidence Gathering", "Corrective Actions"
        ],
        "forms_required": ["RAD-001", "TSP-001"],
        "thresholds": {"warning": "10% variance", "techstat_trigger": "30% variance"},
        "solution_a": "All investments eligible",
        "solution_b": "TechStat: Major only, Escalation: Significant, Security Focus: Infrastructure"
    },
    {
        "id": "WF-06", "name": "Annual Budget Submission",
        "phase": "PRESELECT", "duration": "6-8 weeks",
        "calendar": {
            "draft": "August", "passback": "January",
            "cj": "February", "msr": "June"
        },
        "steps": [
            "Budget Formulation", "IT Portfolio Summary",
            "Business Case Update", "Treasury Review", "OMB Submission"
        ],
        "forms_required": ["BFP-001", "BC-300-001", "BUD-001"],
        "solution_a": "9 Investment budget packages",
        "solution_b": "Major: Exhibit 300, Significant: Exhibit 53, Infrastructure: Tech Budget"
    },
    {
        "id": "WF-07", "name": "Investment Health Assessment",
        "phase": "CONTROL-EVALUATE", "duration": "3-4 weeks",
        "steps": [
            "Performance Data Collection", "Metric Analysis",
            "Health Score Calculation", "CIO Rating Assignment", "Action Plan Development"
        ],
        "forms_required": ["HLT-001", "PMR-001", "CIO-001"],
        "solution_a": "Investment-level health scores",
        "solution_b": "Major: CIO Rating (1-4), Significant: Standard Scoring, Infrastructure: Capacity Scoring"
    },
    {
        "id": "WF-08", "name": "Treasury Monthly CIO Review",
        "phase": "CONTROL", "duration": "As needed",
        "triggers": [
            "10% variance trending", "Metrics 10-30% out of range",
            "Key metrics 30%+ out of range", "TechStat recommendation"
        ],
        "steps": [
            "Issue Identification", "Evidence Gathering",
            "CIO Briefing", "Action Item Tracking", "Follow-up Verification"
        ],
        "forms_required": ["TDR-001", "CEC-001"],
        "solution_a": "Portfolio-level review",
        "solution_b": "Category-specific reviews (Major: OMB Visibility, Significant: Internal, Infrastructure: Technical)"
    }
]

# Generate all data
if __name__ == "__main__":
    forms_a = generate_forms_solution_a()
    forms_b = generate_forms_solution_b()

    print(f"Solution A Forms Generated: {len(forms_a)}")
    print(f"Solution B Forms Generated: {len(forms_b)}")

    # Save to JSON files for reference
    with open('solution_a_data.json', 'w') as f:
        json.dump({
            'investments': INVESTMENTS_A,
            'forms': forms_a,
            'workflows': WORKFLOWS,
            'role_permissions': ROLE_PERMISSIONS_A
        }, f, indent=2)

    with open('solution_b_data.json', 'w') as f:
        json.dump({
            'investments': INVESTMENTS_B,
            'forms': forms_b,
            'workflows': WORKFLOWS,
            'role_permissions': ROLE_PERMISSIONS_B
        }, f, indent=2)

    print("Data files generated successfully!")
