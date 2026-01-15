"""
Update Solution A and B main.py files with full compliance data
Solution A: 134 forms (9 investments)
Solution B: 185 forms (15 investments)
"""

import json
import os
import re

# Load generated data
with open('solution_a_data.json', 'r') as f:
    solution_a = json.load(f)

with open('solution_b_data.json', 'r') as f:
    solution_b = json.load(f)

print(f"Solution A: {len(solution_a['investments'])} investments, {len(solution_a['forms'])} forms")
print(f"Solution B: {len(solution_b['investments'])} investments, {len(solution_b['forms'])} forms")

def format_forms_python(forms, indent=4):
    """Format forms as Python list literal"""
    lines = []
    for form in forms:
        form_str = json.dumps(form, ensure_ascii=False)
        lines.append(' ' * indent + form_str + ',')
    return '\n'.join(lines)

def format_investments_python(investments, solution='A'):
    """Format investments as Python list literal"""
    lines = []
    for inv in investments:
        if solution == 'A':
            # Solution A format with CD owners and teams
            inv_dict = {
                'investment_id': inv['investment_id'],
                'uii': inv['uii'],
                'name': inv['name'],
                'short_name': inv['short_name'],
                'description': inv['description'],
                'category': inv['category'],
                'investment_type': inv['investment_type'],
                'lifecycle_stage': inv.get('current_phase', 'control').lower(),
                'appropriation': 'irs-bsm' if inv['category'] == 'MISSION' else 'irs-ops',
                'cd_owner': inv['cd_owner'],
                'cd_title': f"Coordinating Director - {inv['short_name']}",
                'rd_team': inv.get('rd_team', []),
                're_team': inv.get('re_team', []),
                'pm_team': inv.get('pm_team', []),
                'status': 'active',
                'health': inv.get('health', 'green'),
                'budget_fy25': inv['budget_fy25'],
                'actual_spend_ytd': int(inv['budget_fy25'] * 0.4),
                'cost_variance': inv.get('cost_variance', 0),
                'schedule_days': inv.get('schedule_days', 0),
                'sub_projects': inv.get('sub_projects', 5)
            }
        else:
            # Solution B format with category-specific fields
            inv_dict = {
                'investment_id': inv['investment_id'],
                'uii': inv['uii'],
                'name': inv['name'],
                'short_name': inv['short_name'],
                'description': inv['description'],
                'category': inv['category'],
                'investment_type': inv['investment_type'],
                'primary_owner': inv.get('primary_owner', ''),
                'secondary_owner': inv.get('secondary_owner', ''),
                'oversight_cd': inv.get('oversight_cd', ''),
                'budget_fy25': inv['budget_fy25'],
                'current_phase': inv.get('current_phase', 'CONTROL'),
                'health': inv.get('health', 'green'),
                'cost_variance': inv.get('cost_variance', 0),
                'schedule_days': inv.get('schedule_days', 0),
            }
            # Add category-specific fields
            if inv['category'] == 'MAJOR':
                inv_dict['cio_rating'] = inv.get('cio_rating', 3)
                inv_dict['exhibit_300'] = True
                inv_dict['techstat_eligible'] = True
            elif inv['category'] == 'SIGNIFICANT':
                inv_dict['exhibit_53'] = True
            # INFRASTRUCTURE has minimal extra fields

        form_str = json.dumps(inv_dict, ensure_ascii=False)
        lines.append('    ' + form_str + ',')
    return '\n'.join(lines)

# Generate Solution A forms Python code
solution_a_forms_code = """# 134 CPIC Forms aligned with Design Document (Solution A)
# PRESELECT (15) + SELECT (24) + CONTROL (80) + EVALUATE (15) = 134 forms
DEMO_CPIC_FORMS = [
"""
for form in solution_a['forms']:
    # Add description and owner fields for Solution A
    form_with_extras = {
        'form_id': form['form_id'],
        'form_name': form['form_name'],
        'form_code': form['form_code'],
        'functional_area': form['functional_area'],
        'description': f"{form['form_name']} - {form['functional_area']} documentation",
        'investment_id': form['investment_id'],
        'fiscal_year': form['fiscal_year'],
        'budget_millions': 0,
        'status': form['status'],
        'risk_level': form['risk_level'],
        'owner': 'Investment Owner',
        'cpic_phase': form['cpic_phase']
    }
    solution_a_forms_code += '    ' + json.dumps(form_with_extras, ensure_ascii=False) + ',\n'
solution_a_forms_code += ']'

# Generate Solution B forms Python code
solution_b_forms_code = """# 185 CPIC Forms aligned with Design Document (Solution B)
# Category-specific forms: MAJOR (65 with Exhibit 300), SIGNIFICANT (60 with Exhibit 53), INFRASTRUCTURE (60)
DEMO_CPIC_FORMS = [
"""
for form in solution_b['forms']:
    form_with_extras = {
        'form_id': form['form_id'],
        'form_name': form['form_name'],
        'form_code': form['form_code'],
        'functional_area': form['functional_area'],
        'category': form.get('category', 'MAJOR'),
        'description': f"{form['form_name']} - {form['functional_area']} documentation",
        'investment_id': form['investment_id'],
        'fiscal_year': form['fiscal_year'],
        'frequency': form.get('frequency', 'As Needed'),
        'status': form['status'],
        'risk_level': form['risk_level'],
        'cpic_phase': form['cpic_phase']
    }
    # Add category-specific fields
    if form.get('category') == 'MAJOR':
        form_with_extras['cio_rating_applicable'] = True
        form_with_extras['exhibit_300_required'] = True
    elif form.get('category') == 'SIGNIFICANT':
        form_with_extras['exhibit_53_required'] = True
    solution_b_forms_code += '    ' + json.dumps(form_with_extras, ensure_ascii=False) + ',\n'
solution_b_forms_code += ']'

# Save the generated forms code to files for reference
with open('solution_a_forms_code.py', 'w', encoding='utf-8') as f:
    f.write(solution_a_forms_code)
print("Saved solution_a_forms_code.py")

with open('solution_b_forms_code.py', 'w', encoding='utf-8') as f:
    f.write(solution_b_forms_code)
print("Saved solution_b_forms_code.py")

# Now update the actual main.py files
def update_main_py(filepath, new_forms_code, new_investments_code=None):
    """Update main.py file with new forms and optionally new investments"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find and replace the DEMO_CPIC_FORMS section
    # Pattern to match from "# XX CPIC Forms" or "DEMO_CPIC_FORMS = [" to the closing "]" before DEMO_WORKFLOWS
    pattern = r'(# \d+ CPIC Forms.*?)?DEMO_CPIC_FORMS = \[.*?\](?=\s*\n\s*# \d+ Workflows)'

    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, new_forms_code, content, flags=re.DOTALL)
        print(f"Updated DEMO_CPIC_FORMS in {filepath}")
    else:
        print(f"Could not find DEMO_CPIC_FORMS pattern in {filepath}")
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

# Update Solution A main.py
solution_a_path = 'cpic_suggestion_a/backend/main.py'
if os.path.exists(solution_a_path):
    update_main_py(solution_a_path, solution_a_forms_code)
else:
    print(f"File not found: {solution_a_path}")

# Update Solution B main.py
solution_b_path = 'cpic_suggestion_b/backend/main.py'
if os.path.exists(solution_b_path):
    update_main_py(solution_b_path, solution_b_forms_code)
else:
    print(f"File not found: {solution_b_path}")

print("\n=== Update Complete ===")
print(f"Solution A: 134 forms")
print(f"Solution B: 185 forms")
