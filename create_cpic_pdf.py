"""
Create comprehensive PDF document for IRS CPIC Management System
"""

from fpdf import FPDF

class CPICPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 8, 'IRS CPIC Management System - Complete Reference Guide', 0, 1, 'C')
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(0, 51, 102)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, title, 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_fill_color(200, 200, 200)
        self.cell(0, 8, title, 0, 1, 'L', True)
        self.ln(1)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 5, text)
        self.ln(1)

pdf = CPICPDF()
pdf.set_auto_page_break(auto=True, margin=15)

# Title Page
pdf.add_page()
pdf.set_font('Helvetica', 'B', 24)
pdf.ln(40)
pdf.cell(0, 15, 'IRS CPIC Management System', 0, 1, 'C')
pdf.set_font('Helvetica', 'B', 18)
pdf.cell(0, 12, 'Complete Reference Guide', 0, 1, 'C')
pdf.ln(10)
pdf.set_font('Helvetica', '', 12)
pdf.cell(0, 8, 'Forms, Workflows, and Dashboards', 0, 1, 'C')
pdf.ln(20)
pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, 'Application URLs:', 0, 1, 'C')
pdf.set_font('Helvetica', '', 10)
pdf.cell(0, 6, 'Solution A: https://irs-cpic-solution-a-252370699783.us-central1.run.app', 0, 1, 'C')
pdf.cell(0, 6, 'Solution B: https://irs-cpic-solution-b-252370699783.us-central1.run.app', 0, 1, 'C')
pdf.ln(10)
pdf.cell(0, 6, 'Login: khaja.syed@irs.gov / cpic2025', 0, 1, 'C')
pdf.ln(30)
pdf.set_font('Helvetica', 'I', 10)
pdf.cell(0, 6, 'Document Generated: December 2, 2025', 0, 1, 'C')

# Table of Contents
pdf.add_page()
pdf.chapter_title('Table of Contents')
pdf.set_font('Helvetica', '', 11)
toc = [
    ('1. Executive Summary', 3),
    ('2. Solution A - 9 Investments, 134 Forms', 4),
    ('   2.1 Investments', 4),
    ('   2.2 PRESELECT Phase Forms (15)', 5),
    ('   2.3 SELECT Phase Forms (24)', 6),
    ('   2.4 CONTROL Phase Forms (80)', 7),
    ('   2.5 EVALUATE Phase Forms (15)', 10),
    ('3. Solution B - 15 Investments, 185 Forms', 11),
    ('   3.1 MAJOR Investments (5)', 11),
    ('   3.2 SIGNIFICANT Investments (5)', 11),
    ('   3.3 INFRASTRUCTURE Investments (5)', 12),
    ('   3.4 Forms by Category', 12),
    ('4. Workflows (8)', 13),
    ('5. Dashboards', 15),
    ('6. Role Permissions', 16),
    ('7. API Endpoints', 17),
    ('8. Functional Areas (22)', 18),
]
for item, page in toc:
    pdf.cell(0, 6, f'{item}', 0, 1)

# Executive Summary
pdf.add_page()
pdf.chapter_title('1. Executive Summary')
pdf.body_text('''The IRS CPIC (Capital Planning and Investment Control) Management System provides comprehensive
investment lifecycle management for IT investments. The system is available in two solution configurations:

Solution A: Designed for consolidated investment management with 9 investments organized into Mission (4)
and Foundational (5) categories, tracking 134 forms across the CPIC lifecycle phases.

Solution B: Designed for federal compliance with 15 investments organized into MAJOR (5), SIGNIFICANT (5),
and INFRASTRUCTURE (5) categories, tracking 185 forms with OMB Exhibit 300/53 requirements.

Both solutions support 8 core workflows aligned with Treasury SPIKE tool reporting requirements.''')

pdf.section_title('Key Statistics')
pdf.set_font('Helvetica', '', 10)
stats = [
    ['Component', 'Solution A', 'Solution B'],
    ['Investments', '9', '15'],
    ['Forms', '134', '185'],
    ['Workflows', '8', '8'],
    ['Dashboards', '5', '8'],
    ['Functional Areas', '22', '22'],
]
col_widths = [60, 40, 40]
for row in stats:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 7, cell, 1, 0, 'C')
    pdf.ln()

# Solution A Investments
pdf.add_page()
pdf.chapter_title('2. Solution A - 9 Investments, 134 Forms')
pdf.section_title('2.1 Mission-Focused Investments (4)')

investments_mission = [
    ['ID', 'Name', 'CD Owner', 'Budget', 'Health'],
    ['INV-01', 'Taxpayer Services Modernization', 'Jim Keith', '$456M', 'Green'],
    ['INV-02', 'Tax Processing Transformation', 'Miji Mathews', '$389M', 'Green'],
    ['INV-03', 'Compliance Systems Enhancement', 'Eric Markow', '$234M', 'Yellow'],
    ['INV-04', 'Filing Season Infrastructure', 'Craig Drake', '$178M', 'Green'],
]
col_widths = [20, 70, 40, 25, 20]
pdf.set_font('Helvetica', 'B', 9)
for cell in investments_mission[0]:
    pdf.cell(col_widths[investments_mission[0].index(cell)], 7, cell, 1, 0, 'C')
pdf.ln()
pdf.set_font('Helvetica', '', 9)
for row in investments_mission[1:]:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 6, cell, 1, 0, 'L' if i == 1 else 'C')
    pdf.ln()

pdf.ln(5)
pdf.section_title('Foundational Investments (5)')
investments_found = [
    ['ID', 'Name', 'CD Owner', 'Budget', 'Health'],
    ['INV-05', 'API Platform & Integration', 'Rob King', '$145M', 'Green'],
    ['INV-06', 'Enterprise Infrastructure', 'Lou Capece', '$312M', 'Green'],
    ['INV-07', 'Cybersecurity & Privacy', 'Houman Rasouli', '$267M', 'Yellow'],
    ['INV-08', 'End User Digital Services', 'Tanya Chiaravalle', '$98M', 'Green'],
    ['INV-09', 'IT Strategy & PMO', 'Courtney Williams', '$67M', 'Green'],
]
pdf.set_font('Helvetica', 'B', 9)
for cell in investments_found[0]:
    pdf.cell(col_widths[investments_found[0].index(cell)], 7, cell, 1, 0, 'C')
pdf.ln()
pdf.set_font('Helvetica', '', 9)
for row in investments_found[1:]:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 6, cell, 1, 0, 'L' if i == 1 else 'C')
    pdf.ln()

# PRESELECT Forms
pdf.add_page()
pdf.section_title('2.2 PRESELECT Phase Forms (15)')
preselect_forms = [
    ['CPIC-001', 'Strategic Planning Document', 'SPD-001', 'Strategy'],
    ['CPIC-002', 'Needs Identification Report', 'NIR-001', 'Business Analysis'],
    ['CPIC-003', 'Initial Screening Criteria', 'ISC-001', 'Governance'],
    ['CPIC-004', 'Preliminary Business Case', 'PBC-001', 'Investment Planning'],
    ['CPIC-005', 'Portfolio Prioritization Request', 'PPR-001', 'Strategy'],
    ['CPIC-006', 'Mission Alignment Assessment', 'MAA-001', 'Strategy'],
    ['CPIC-007', 'Resource Availability Check', 'RAC-001', 'Resource Management'],
    ['CPIC-008', 'Technical Feasibility Study', 'TFS-001', 'Enterprise Architecture'],
    ['CPIC-009', 'Budget Authority Request', 'BAR-001', 'Financial Analysis'],
    ['CPIC-010', 'Stakeholder Identification', 'SID-001', 'Strategy'],
    ['CPIC-011', 'Initial Risk Screening', 'IRS-001', 'Risk Management'],
    ['CPIC-012', 'Capability Gap Assessment', 'CGA-001', 'Enterprise Architecture'],
    ['CPIC-013', 'Investment Proposal Draft', 'IPD-001', 'Investment Planning'],
    ['CPIC-014', 'CIO Endorsement Request', 'CER-001', 'Governance'],
    ['CPIC-015', 'IRB Submission Package', 'ISP-001', 'Governance'],
]
col_widths = [22, 65, 25, 50]
pdf.set_font('Helvetica', 'B', 8)
pdf.cell(col_widths[0], 6, 'Form ID', 1, 0, 'C')
pdf.cell(col_widths[1], 6, 'Form Name', 1, 0, 'C')
pdf.cell(col_widths[2], 6, 'Code', 1, 0, 'C')
pdf.cell(col_widths[3], 6, 'Functional Area', 1, 1, 'C')
pdf.set_font('Helvetica', '', 8)
for row in preselect_forms:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 5, cell, 1, 0, 'L')
    pdf.ln()

# SELECT Forms
pdf.ln(5)
pdf.section_title('2.3 SELECT Phase Forms (24)')
select_forms = [
    ['CPIC-016', 'OMB Exhibit 300 Business Case', 'BC-300-001', 'Investment Planning'],
    ['CPIC-017', 'Investment Screening Criteria', 'ISC-001', 'Investment Planning'],
    ['CPIC-018', 'Alternatives Analysis', 'AA-001', 'Investment Planning'],
    ['CPIC-019', 'Cost-Benefit Analysis', 'CBA-001', 'Financial Analysis'],
    ['CPIC-020', 'Risk Assessment Detailed', 'RAD-001', 'Risk Management'],
    ['CPIC-021', 'Strategic Alignment Assessment', 'SAA-001', 'Strategy'],
    ['CPIC-022', 'Architecture Review Request', 'ARR-001', 'Enterprise Architecture'],
    ['CPIC-023', 'Security Requirements Document', 'SRD-001', 'Cybersecurity'],
    ['CPIC-024', 'Investment Proposal Final', 'IPF-001', 'Investment Planning'],
    ['CPIC-025', 'Stakeholder Analysis Complete', 'SAC-001', 'Strategy'],
    ['CPIC-026', 'Capability Gap Analysis Final', 'CGAF-001', 'Enterprise Architecture'],
    ['CPIC-027', 'Resource Requirements Plan', 'RRP-001', 'Resource Management'],
    ['CPIC-028', 'Procurement Strategy', 'PS-001', 'Acquisition'],
    ['CPIC-029', 'Performance Measures Plan', 'PMP-001', 'Performance'],
    ['CPIC-030', 'IRB Review Package', 'IRP-001', 'Governance'],
    ['CPIC-031', 'EA Compliance Certification', 'EAC-001', 'Enterprise Architecture'],
    ['CPIC-032', 'Privacy Impact Assessment Initial', 'PIA-I-001', 'Privacy'],
    ['CPIC-033', 'Section 508 Assessment', 'S508-001', 'Compliance'],
    ['CPIC-034', 'Budget Formulation Package', 'BFP-001', 'Financial Analysis'],
    ['CPIC-035', 'Governance Structure Plan', 'GSP-001', 'Governance'],
    ['CPIC-036', 'Communication Plan', 'CP-001', 'Strategy'],
    ['CPIC-037', 'Training Needs Assessment', 'TNA-001', 'Training'],
    ['CPIC-038', 'Transition Planning Document', 'TPD-001', 'Project Management'],
    ['CPIC-039', 'CIO Approval Package', 'CAP-001', 'Governance'],
]
pdf.set_font('Helvetica', 'B', 8)
pdf.cell(col_widths[0], 6, 'Form ID', 1, 0, 'C')
pdf.cell(col_widths[1], 6, 'Form Name', 1, 0, 'C')
pdf.cell(col_widths[2], 6, 'Code', 1, 0, 'C')
pdf.cell(col_widths[3], 6, 'Functional Area', 1, 1, 'C')
pdf.set_font('Helvetica', '', 8)
for row in select_forms:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 5, cell, 1, 0, 'L')
    pdf.ln()

# CONTROL Forms (Page 1)
pdf.add_page()
pdf.section_title('2.4 CONTROL Phase Forms (80) - Part 1')
control_forms_1 = [
    ['CPIC-040', 'Monthly Status Report', 'MSR-001', 'Reporting'],
    ['CPIC-041', 'Baseline Change Request', 'BCR-001', 'Change Management'],
    ['CPIC-042', 'Earned Value Management Report', 'EVM-001', 'Financial Analysis'],
    ['CPIC-043', 'Risk Register Update', 'RRU-001', 'Risk Management'],
    ['CPIC-044', 'TechStat Review Preparation', 'TSP-001', 'Governance'],
    ['CPIC-045', 'Contractor Performance Report', 'CPR-001', 'Acquisition'],
    ['CPIC-046', 'Quality Assurance Report', 'QAR-001', 'Quality'],
    ['CPIC-047', 'Security Assessment Report', 'SAR-001', 'Cybersecurity'],
    ['CPIC-048', 'Project Schedule Update', 'PSU-001', 'Project Management'],
    ['CPIC-049', 'Budget Execution Report', 'BER-001', 'Financial Analysis'],
    ['CPIC-050', 'Release Management Plan', 'RMP-001', 'Development'],
    ['CPIC-051', 'Infrastructure Change Request', 'ICR-001', 'Infrastructure'],
    ['CPIC-052', 'Testing Progress Report', 'TPR-001', 'Quality'],
    ['CPIC-053', 'Privacy Impact Assessment', 'PIA-001', 'Privacy'],
    ['CPIC-054', 'Authority to Operate Request', 'ATO-001', 'Cybersecurity'],
    ['CPIC-055', 'Data Quality Report', 'DQR-001', 'Data Management'],
    ['CPIC-056', 'Training Status Report', 'TSR-001', 'Training'],
    ['CPIC-057', 'Operational Readiness Review', 'ORR-001', 'Operations'],
    ['CPIC-058', 'CIO Evaluation Comments', 'CEC-001', 'Governance'],
    ['CPIC-059', 'Treasury DO Report', 'TDR-001', 'Reporting'],
    ['CPIC-060', 'OMB ITDB Submission', 'ITDB-001', 'Reporting'],
    ['CPIC-061', 'FITARA Compliance Report', 'FCR-001', 'Compliance'],
    ['CPIC-062', 'Enterprise License Agreement', 'ELA-001', 'Acquisition'],
    ['CPIC-063', 'Cloud Migration Status', 'CMS-001', 'Infrastructure'],
    ['CPIC-064', 'DevSecOps Maturity Assessment', 'DMA-001', 'Development'],
    ['CPIC-065', 'Incident Response Report', 'IRR-001', 'Cybersecurity'],
    ['CPIC-066', 'Accessibility Compliance', 'AC-001', 'Compliance'],
    ['CPIC-067', 'API Governance Report', 'AGR-001', 'Enterprise Architecture'],
    ['CPIC-068', 'System Health Dashboard', 'SHD-001', 'Operations'],
    ['CPIC-069', 'Technical Debt Assessment', 'TDA-001', 'Development'],
    ['CPIC-070', 'Workforce Planning Report', 'WPR-001', 'Resource Management'],
    ['CPIC-071', 'Disaster Recovery Test Report', 'DRT-001', 'Operations'],
    ['CPIC-072', 'Capacity Planning Report', 'CAPR-001', 'Infrastructure'],
    ['CPIC-073', 'Change Advisory Board Minutes', 'CAB-001', 'Change Management'],
    ['CPIC-074', 'Sprint Review Summary', 'SRS-001', 'Development'],
    ['CPIC-075', 'Vendor Performance Scorecard', 'VPS-001', 'Acquisition'],
    ['CPIC-076', 'Integration Testing Report', 'ITR-001', 'Quality'],
    ['CPIC-077', 'User Acceptance Testing', 'UAT-001', 'Quality'],
    ['CPIC-078', 'Deployment Checklist', 'DCL-001', 'Operations'],
    ['CPIC-079', 'Configuration Management Report', 'CMR-001', 'Operations'],
]
pdf.set_font('Helvetica', 'B', 8)
pdf.cell(col_widths[0], 6, 'Form ID', 1, 0, 'C')
pdf.cell(col_widths[1], 6, 'Form Name', 1, 0, 'C')
pdf.cell(col_widths[2], 6, 'Code', 1, 0, 'C')
pdf.cell(col_widths[3], 6, 'Functional Area', 1, 1, 'C')
pdf.set_font('Helvetica', '', 8)
for row in control_forms_1:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 5, cell, 1, 0, 'L')
    pdf.ln()

# CONTROL Forms (Page 2)
pdf.add_page()
pdf.section_title('CONTROL Phase Forms - Part 2')
control_forms_2 = [
    ['CPIC-080', 'Performance Baseline Update', 'PBU-001', 'Performance'],
    ['CPIC-081', 'Scope Change Impact Analysis', 'SCIA-001', 'Change Management'],
    ['CPIC-082', 'Schedule Variance Report', 'SVR-001', 'Project Management'],
    ['CPIC-083', 'Cost Variance Report', 'CVR-001', 'Financial Analysis'],
    ['CPIC-084', 'Resource Utilization Report', 'RUR-001', 'Resource Management'],
    ['CPIC-085', 'Milestone Achievement Report', 'MAR-001', 'Project Management'],
    ['CPIC-086', 'Issue Resolution Log', 'IRL-001', 'Project Management'],
    ['CPIC-087', 'Decision Log Update', 'DLU-001', 'Governance'],
    ['CPIC-088', 'Action Item Tracker', 'AIT-001', 'Project Management'],
    ['CPIC-089', 'Communication Status', 'CS-001', 'Strategy'],
    ['CPIC-090', 'Stakeholder Engagement Report', 'SER-001', 'Strategy'],
    ['CPIC-091', 'Benefits Tracking Report', 'BTR-001', 'Performance'],
    ['CPIC-092', 'Quality Metrics Dashboard', 'QMD-001', 'Quality'],
    ['CPIC-093', 'Security Posture Report', 'SPR-001', 'Cybersecurity'],
    ['CPIC-094', 'Compliance Status Report', 'CSR-001', 'Compliance'],
    ['CPIC-095', 'EA Alignment Review', 'EAR-001', 'Enterprise Architecture'],
    ['CPIC-096', 'Data Architecture Update', 'DAU-001', 'Enterprise Architecture'],
    ['CPIC-097', 'Technology Stack Report', 'TSTR-001', 'Development'],
    ['CPIC-098', 'Infrastructure Capacity Report', 'ICPR-001', 'Infrastructure'],
    ['CPIC-099', 'Network Performance Report', 'NPR-001', 'Infrastructure'],
    ['CPIC-100', 'Database Performance Report', 'DPR-001', 'Infrastructure'],
    ['CPIC-101', 'Application Performance Report', 'APR-001', 'Development'],
    ['CPIC-102', 'User Experience Report', 'UXR-001', 'Development'],
    ['CPIC-103', 'Agile Velocity Report', 'AVR-001', 'Development'],
    ['CPIC-104', 'Sprint Burndown Chart', 'SBC-001', 'Development'],
    ['CPIC-105', 'Product Backlog Status', 'PBS-001', 'Development'],
    ['CPIC-106', 'Feature Completion Report', 'FCR2-001', 'Development'],
    ['CPIC-107', 'Bug Resolution Report', 'BRR-001', 'Quality'],
    ['CPIC-108', 'Code Review Summary', 'CRS-001', 'Development'],
    ['CPIC-109', 'Technical Review Report', 'TRR-001', 'Enterprise Architecture'],
    ['CPIC-110', 'Environment Status Report', 'ESR-001', 'Infrastructure'],
    ['CPIC-111', 'Release Readiness Report', 'RRR-001', 'Development'],
    ['CPIC-112', 'Go-Live Checklist', 'GLC-001', 'Operations'],
    ['CPIC-113', 'Hypercare Status Report', 'HSR-001', 'Operations'],
    ['CPIC-114', 'Knowledge Base Update', 'KBU-001', 'Training'],
    ['CPIC-115', 'Support Ticket Analysis', 'STA-001', 'Operations'],
    ['CPIC-116', 'SLA Performance Report', 'SLAPR-001', 'Operations'],
    ['CPIC-117', 'Availability Report', 'AVL-001', 'Operations'],
    ['CPIC-118', 'SPIKE Submission Package', 'SSP-001', 'Reporting'],
    ['CPIC-119', 'Executive Dashboard Update', 'EDU-001', 'Reporting'],
]
pdf.set_font('Helvetica', 'B', 8)
pdf.cell(col_widths[0], 6, 'Form ID', 1, 0, 'C')
pdf.cell(col_widths[1], 6, 'Form Name', 1, 0, 'C')
pdf.cell(col_widths[2], 6, 'Code', 1, 0, 'C')
pdf.cell(col_widths[3], 6, 'Functional Area', 1, 1, 'C')
pdf.set_font('Helvetica', '', 8)
for row in control_forms_2:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 5, cell, 1, 0, 'L')
    pdf.ln()

# EVALUATE Forms
pdf.add_page()
pdf.section_title('2.5 EVALUATE Phase Forms (15)')
evaluate_forms = [
    ['CPIC-120', 'Post-Implementation Review', 'PIR-001', 'Evaluation'],
    ['CPIC-121', 'Operational Analysis', 'OA-001', 'Evaluation'],
    ['CPIC-122', 'Benefits Realization Report', 'BRR2-001', 'Evaluation'],
    ['CPIC-123', 'Customer Satisfaction Survey', 'CSS-001', 'Evaluation'],
    ['CPIC-124', 'Performance Metrics Review', 'PMR-001', 'Performance'],
    ['CPIC-125', 'Total Cost of Ownership', 'TCO-001', 'Financial Analysis'],
    ['CPIC-126', 'Lessons Learned', 'LL-001', 'Evaluation'],
    ['CPIC-127', 'Investment Continuation Assessment', 'ICA-001', 'Investment Planning'],
    ['CPIC-128', 'Technology Refresh Assessment', 'TRA-001', 'Enterprise Architecture'],
    ['CPIC-129', 'Portfolio Optimization Review', 'POR-001', 'Strategy'],
    ['CPIC-130', 'Service Level Achievement', 'SLA-001', 'Operations'],
    ['CPIC-131', 'Operational Efficiency Report', 'OER-001', 'Operations'],
    ['CPIC-132', 'User Adoption Report', 'UAR-001', 'Evaluation'],
    ['CPIC-133', 'Business Value Assessment', 'BVA-001', 'Evaluation'],
    ['CPIC-134', 'Investment Closeout Report', 'ICR2-001', 'Investment Planning'],
]
pdf.set_font('Helvetica', 'B', 8)
pdf.cell(col_widths[0], 6, 'Form ID', 1, 0, 'C')
pdf.cell(col_widths[1], 6, 'Form Name', 1, 0, 'C')
pdf.cell(col_widths[2], 6, 'Code', 1, 0, 'C')
pdf.cell(col_widths[3], 6, 'Functional Area', 1, 1, 'C')
pdf.set_font('Helvetica', '', 8)
for row in evaluate_forms:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 5, cell, 1, 0, 'L')
    pdf.ln()

# Solution B
pdf.add_page()
pdf.chapter_title('3. Solution B - 15 Investments, 185 Forms')
pdf.section_title('3.1 MAJOR Investments (5) - OMB Exhibit 300, CIO Ratings')
major_inv = [
    ['ID', 'Name', 'Owner', 'Budget', 'CIO Rating'],
    ['MAJ-01', 'Integrated Enterprise Portal', 'Miji Mathews', '$520M', '4'],
    ['MAJ-02', 'Customer Account Data Engine 2', 'Terry Jackson', '$680M', '3'],
    ['MAJ-03', 'Integrated Submission & Remittance', 'Raymond Barnes', '$420M', '4'],
    ['MAJ-04', 'Enterprise Case Management', 'Eric Corbin', '$380M', '2'],
    ['MAJ-05', 'Enterprise Cybersecurity Program', 'Patricia Farrell', '$450M', '4'],
]
col_widths = [20, 70, 40, 25, 25]
pdf.set_font('Helvetica', 'B', 9)
for i, cell in enumerate(major_inv[0]):
    pdf.cell(col_widths[i], 7, cell, 1, 0, 'C')
pdf.ln()
pdf.set_font('Helvetica', '', 9)
for row in major_inv[1:]:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 6, cell, 1, 0, 'L' if i == 1 else 'C')
    pdf.ln()

pdf.ln(5)
pdf.section_title('3.2 SIGNIFICANT Investments (5) - OMB Exhibit 53')
sig_inv = [
    ['ID', 'Name', 'Owner', 'Budget'],
    ['SIG-01', 'Return Review Program', 'Kevin McQuighan', '$180M'],
    ['SIG-02', 'Enterprise Learning Management', 'Sandra Wilson', '$95M'],
    ['SIG-03', 'Document Management System', 'Marcus Taylor', '$120M'],
    ['SIG-04', 'Practitioner Services Platform', 'Lisa Chen', '$85M'],
    ['SIG-05', 'Data Analytics Platform', 'James Mitchell', '$110M'],
]
col_widths = [20, 80, 50, 30]
pdf.set_font('Helvetica', 'B', 9)
for i, cell in enumerate(sig_inv[0]):
    pdf.cell(col_widths[i], 7, cell, 1, 0, 'C')
pdf.ln()
pdf.set_font('Helvetica', '', 9)
for row in sig_inv[1:]:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 6, cell, 1, 0, 'L' if i == 1 else 'C')
    pdf.ln()

pdf.ln(5)
pdf.section_title('3.3 INFRASTRUCTURE Investments (5) - Technical Budget')
inf_inv = [
    ['ID', 'Name', 'Owner', 'Budget'],
    ['INF-01', 'Enterprise Network Services', 'Robert Anderson', '$280M'],
    ['INF-02', 'Enterprise Data Centers', 'Michael Brown', '$320M'],
    ['INF-03', 'Enterprise Cloud Services', 'Jennifer Lee', '$240M'],
    ['INF-04', 'Enterprise Security Operations', 'David Kim', '$180M'],
    ['INF-05', 'IT Service Management', 'William Davis', '$150M'],
]
pdf.set_font('Helvetica', 'B', 9)
for i, cell in enumerate(inf_inv[0]):
    pdf.cell(col_widths[i], 7, cell, 1, 0, 'C')
pdf.ln()
pdf.set_font('Helvetica', '', 9)
for row in inf_inv[1:]:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 6, cell, 1, 0, 'L' if i == 1 else 'C')
    pdf.ln()

pdf.ln(5)
pdf.section_title('3.4 Forms by Category (185 Total)')
pdf.body_text('''MAJOR Category (65 Forms): 13 forms per investment including OMB Exhibit 300, Monthly Status,
EVM Reports, Risk Assessment, BCR, Quality Gates, Security Compliance, Vendor Performance, PIR,
CIO Rating Self-Assessment, TechStat Prep, GAO Audit Support, Budget Execution.

SIGNIFICANT Category (60 Forms): 12 forms per investment including Exhibit 53, Project Status,
Cost Performance, Risk Register, Scope Change, Testing Status, Security Assessment, Contract Management,
Resource Allocation, Benefits Tracking, Operational Metrics, Quarterly Review.

INFRASTRUCTURE Category (60 Forms): 12 forms per investment including Technical Budget, Operations Status,
Capacity Planning, Maintenance Schedule, Service Level, Incident Summary, Change Implementation,
Configuration Status, DR Status, Security Posture, Network Performance, Infrastructure Metrics.''')

# Workflows
pdf.add_page()
pdf.chapter_title('4. Workflows (8)')

workflows = [
    ('WF-01: Investment Creation & Approval', 'PRESELECT-SELECT', '8-12 weeks',
     'Complete investment proposal through governance approval',
     ['Draft Business Case', 'Investment Screening', 'Alternatives Analysis', 'IRB Review', 'CIO Approval']),
    ('WF-02: Baseline Change Request (BCR)', 'CONTROL', '2-4 weeks',
     'Process for requesting baseline scope, cost, or schedule changes',
     ['PM identifies change', 'BCR Form in SPIKE', 'IPM Review', 'Treasury CPIC Review', 'OMB Notification']),
    ('WF-03: Monthly Reporting Cycle', 'CONTROL', '10-15 days',
     'Monthly investment status reporting to Treasury/OMB (Due: 19th)',
     ['Data Collection (1st-15th)', 'PM Review (15th-17th)', 'CIO Comments (17th-18th)', 'SPIKE Submission (19th)']),
    ('WF-04: Project Initiation', 'SELECT-CONTROL', '2-3 weeks',
     'Transition from approved investment to active project execution',
     ['Project Charter', 'Kickoff Meeting', 'Baseline Establishment', 'Resource Assignment', 'Schedule Creation']),
    ('WF-05: Risk Escalation & TechStat', 'CONTROL', '1-2 weeks',
     'Risk escalation and TechStat reviews (Trigger: >=30% variance)',
     ['Risk Identification', 'Impact Assessment', 'CIO Notification', 'TechStat Scheduling', 'Corrective Actions']),
    ('WF-06: Annual Budget Submission', 'PRESELECT', '6-8 weeks',
     'Annual IT budget development and submission process',
     ['Budget Formulation', 'IT Portfolio Summary', 'Business Case Update', 'Treasury Review', 'OMB Submission']),
    ('WF-07: Investment Health Assessment', 'CONTROL-EVALUATE', '3-4 weeks',
     'Periodic investment health evaluation with CIO ratings (1-4 scale)',
     ['Performance Data Collection', 'Metric Analysis', 'CIO Rating Assignment', 'Action Plan Development']),
    ('WF-08: Treasury Monthly CIO Review', 'CONTROL', 'As needed',
     'Treasury-led monthly investment performance reviews',
     ['Issue Identification', 'Evidence Gathering', 'CIO Briefing', 'Action Item Tracking']),
]

for wf in workflows:
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 7, wf[0], 0, 1)
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 5, f'Phase: {wf[1]} | Duration: {wf[2]}', 0, 1)
    pdf.cell(0, 5, f'Description: {wf[3]}', 0, 1)
    pdf.cell(0, 5, 'Steps: ' + ' -> '.join(wf[4]), 0, 1)
    pdf.ln(3)

# Dashboards
pdf.add_page()
pdf.chapter_title('5. Dashboards')

pdf.section_title('Solution A Dashboards (5)')
dashboards_a = [
    ['Executive Dashboard', '/api/dashboard/executive', 'Portfolio overview for CIO/executives'],
    ['Treasury Dashboard', '/api/dashboard/treasury', 'SPIKE tool integration and reporting'],
    ['Category Dashboard', '/api/dashboard/category/<cat>', 'Investment by MISSION/FOUNDATIONAL'],
    ['CD Dashboard', '/api/dashboard/cd/<owner>', 'Coordinating Director portfolio'],
    ['Stats Dashboard', '/api/dashboard/stats', 'Statistical overview'],
]
col_widths = [50, 60, 70]
pdf.set_font('Helvetica', 'B', 9)
pdf.cell(col_widths[0], 7, 'Dashboard', 1, 0, 'C')
pdf.cell(col_widths[1], 7, 'Endpoint', 1, 0, 'C')
pdf.cell(col_widths[2], 7, 'Description', 1, 1, 'C')
pdf.set_font('Helvetica', '', 9)
for row in dashboards_a:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 6, cell, 1, 0, 'L')
    pdf.ln()

pdf.ln(5)
pdf.section_title('Solution B Dashboards (8)')
dashboards_b = [
    ['Executive Dashboard', '/api/dashboard/executive', 'Portfolio overview'],
    ['Treasury Dashboard', '/api/dashboard/treasury', 'SPIKE integration'],
    ['Exhibit 300 Dashboard', '/api/dashboard/exhibit-300', 'MAJOR investments'],
    ['Exhibit 53 Dashboard', '/api/dashboard/exhibit-53', 'SIGNIFICANT investments'],
    ['Infrastructure Dashboard', '/api/dashboard/infrastructure', 'INFRASTRUCTURE status'],
    ['CIO Ratings Dashboard', '/api/dashboard/cio-ratings', 'Rating distribution (1-4)'],
    ['TechStat Dashboard', '/api/dashboard/techstat', 'TechStat eligible investments'],
    ['Category Dashboard', '/api/dashboard/category/<cat>', 'By category'],
]
pdf.set_font('Helvetica', 'B', 9)
pdf.cell(col_widths[0], 7, 'Dashboard', 1, 0, 'C')
pdf.cell(col_widths[1], 7, 'Endpoint', 1, 0, 'C')
pdf.cell(col_widths[2], 7, 'Description', 1, 1, 'C')
pdf.set_font('Helvetica', '', 9)
for row in dashboards_b:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 6, cell, 1, 0, 'L')
    pdf.ln()

# Role Permissions
pdf.add_page()
pdf.chapter_title('6. Role Permissions')
roles = [
    ['Role', 'Level', 'View Access', 'Approve', 'Edit'],
    ['CIO', '0', 'All investments, executive', 'IRB, budget, TechStat', '-'],
    ['Coordinating Director', '1', 'Own investment', 'BCR <$5M, monthly', 'Own forms'],
    ['Resource Director', '2', 'Own investment', 'Resources, <$500K', 'Resource forms'],
    ['Responsible Engineer', '3', 'Own projects', 'Tech reviews, QA', 'Tech forms'],
    ['Product Manager', '4', 'Own projects', '-', 'Status, sprints'],
    ['Admin', '0', 'All', 'All', 'All'],
]
col_widths = [45, 15, 50, 40, 30]
pdf.set_font('Helvetica', 'B', 9)
for i, cell in enumerate(roles[0]):
    pdf.cell(col_widths[i], 7, cell, 1, 0, 'C')
pdf.ln()
pdf.set_font('Helvetica', '', 8)
for row in roles[1:]:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 6, cell, 1, 0, 'L')
    pdf.ln()

# API Endpoints
pdf.ln(10)
pdf.chapter_title('7. API Endpoints')
endpoints = [
    ['Category', 'Endpoint', 'Method', 'Description'],
    ['Auth', '/api/auth/login', 'POST', 'User login'],
    ['Auth', '/api/auth/register', 'POST', 'Register user'],
    ['Auth', '/api/auth/me', 'GET', 'Current user'],
    ['Investments', '/api/investments', 'GET/POST', 'List/Create'],
    ['Investments', '/api/investments/<id>', 'GET/PUT', 'Get/Update'],
    ['Forms', '/api/cpic-forms', 'GET', 'List all forms'],
    ['Forms', '/api/cpic-forms/<id>', 'GET', 'Form details'],
    ['Forms', '/api/cpic-forms/summary', 'GET', 'Forms summary'],
    ['Reports', '/api/monthly-reports', 'GET/POST', 'Monthly reports'],
    ['Projects', '/api/projects', 'GET/POST', 'Projects'],
    ['Risks', '/api/risks', 'GET/POST', 'Risks'],
    ['Workflows', '/api/demo/workflows', 'GET', 'All workflows'],
    ['Admin', '/api/admin/users', 'GET', 'User list'],
    ['Health', '/health', 'GET', 'Health check'],
]
col_widths = [30, 55, 25, 70]
pdf.set_font('Helvetica', 'B', 8)
for i, cell in enumerate(endpoints[0]):
    pdf.cell(col_widths[i], 7, cell, 1, 0, 'C')
pdf.ln()
pdf.set_font('Helvetica', '', 8)
for row in endpoints[1:]:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 5, cell, 1, 0, 'L')
    pdf.ln()

# Functional Areas
pdf.add_page()
pdf.chapter_title('8. Functional Areas (22)')
areas = [
    ['1. Investment Planning', '2. Financial Analysis', '3. Risk Management'],
    ['4. Governance', '5. Reporting', '6. Cybersecurity'],
    ['7. Enterprise Architecture', '8. Project Management', '9. Acquisition'],
    ['10. Quality', '11. Compliance', '12. Operations'],
    ['13. Development', '14. Infrastructure', '15. Training'],
    ['16. Strategy', '17. Resource Management', '18. Change Management'],
    ['19. Privacy', '20. Data Management', '21. Performance'],
    ['22. Evaluation', '', ''],
]
pdf.set_font('Helvetica', '', 10)
col_width = 60
for row in areas:
    for cell in row:
        pdf.cell(col_width, 8, cell, 1, 0, 'L')
    pdf.ln()

pdf.ln(10)
pdf.section_title('Treasury SPIKE Tool Integration')
pdf.body_text('''Monthly Reporting Deadlines:
- 1st-15th: Data collection from investment teams
- 15th-17th: Portfolio Manager review
- 17th-18th: CIO comments and approval
- 19th: SPIKE submission to OMB

CIO Rating Scale (Solution B MAJOR Investments):
- 4: On Track - Meets all performance expectations
- 3: Minor Issues - Some concerns, actively managed
- 2: Significant Issues - Requires management attention
- 1: Critical Issues - Immediate action required

TechStat Triggers:
- Cost variance >= 30%
- Schedule variance >= 30%
- Key metrics >= 30% out of range''')

# Save PDF
pdf.output('C:/1AITrading/Trading/IRS_CPIC_COMPLETE_REFERENCE.pdf')
print('PDF created successfully!')
