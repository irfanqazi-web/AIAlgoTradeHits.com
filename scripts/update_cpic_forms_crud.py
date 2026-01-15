"""
Update CPIC Solutions A and B with Form Records CRUD Functionality
- Adds form record data structure (10-20 records per form)
- Adds CRUD API endpoints
- Updates frontend with form detail view, alternating row colors
"""

import os
import re

# ============= FORM RECORDS GENERATOR =============
FORM_RECORDS_CODE = '''
# ==================== FORM RECORDS DATA ====================
# Sample records for each form - 10-20 records per form with realistic data

import random
from datetime import datetime, timedelta

def generate_form_records():
    """Generate sample records for all forms with realistic data"""
    records = {}

    # Field definitions by form type
    field_configs = {
        'Strategic Planning': ['objective', 'strategy_area', 'target_date', 'responsible_party', 'progress_pct', 'priority', 'notes'],
        'Budget': ['line_item', 'amount', 'category', 'fiscal_year', 'approval_status', 'requested_by', 'justification'],
        'Risk': ['risk_description', 'probability', 'impact', 'mitigation', 'risk_owner', 'status', 'due_date'],
        'Reporting': ['report_period', 'metric_name', 'actual_value', 'target_value', 'variance', 'trend', 'comments'],
        'Compliance': ['requirement', 'compliance_status', 'evidence', 'reviewer', 'last_audit', 'next_audit', 'remediation'],
        'Project': ['task_name', 'assigned_to', 'start_date', 'end_date', 'status', 'hours_estimated', 'hours_actual'],
        'Technical': ['component', 'version', 'environment', 'change_type', 'impact_area', 'test_status', 'deployment_date'],
        'Security': ['control_id', 'control_name', 'implementation_status', 'assessment_date', 'auditor', 'findings', 'remediation_date'],
        'Performance': ['kpi_name', 'current_value', 'target_value', 'baseline', 'measurement_date', 'data_source', 'owner'],
        'Governance': ['decision', 'decision_date', 'decision_maker', 'impact', 'effective_date', 'review_date', 'documentation'],
        'Default': ['field_1', 'field_2', 'field_3', 'status', 'date', 'owner', 'notes']
    }

    # Sample data for fields
    names = ['John Smith', 'Maria Garcia', 'James Wilson', 'Sarah Chen', 'Michael Brown', 'Emily Davis',
             'Robert Johnson', 'Lisa Anderson', 'David Martinez', 'Jennifer Taylor', 'William Lee', 'Amanda White']
    statuses = ['Approved', 'In Review', 'Pending', 'Completed', 'Draft', 'Active', 'On Hold']
    priorities = ['High', 'Medium', 'Low', 'Critical']
    risk_levels = ['Low', 'Medium', 'High', 'Very High']
    compliance_statuses = ['Compliant', 'Non-Compliant', 'Partial', 'Remediation Required']

    base_date = datetime.now()

    for form_id in range(1, 200):  # Cover all forms
        form_id_str = f"CPIC-{form_id:03d}"
        num_records = random.randint(10, 20)

        # Determine field config based on form ID ranges
        if form_id <= 15:
            config_key = 'Strategic Planning'
        elif form_id <= 40:
            config_key = 'Governance'
        elif form_id <= 80:
            config_key = 'Project'
        elif form_id <= 100:
            config_key = 'Technical'
        elif form_id <= 120:
            config_key = 'Performance'
        elif form_id <= 134:
            config_key = 'Compliance'
        else:
            config_key = 'Reporting'

        fields = field_configs.get(config_key, field_configs['Default'])
        form_records = []

        for i in range(num_records):
            record = {
                'record_id': f"{form_id_str}-R{i+1:03d}",
                'created_date': (base_date - timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d'),
                'modified_date': (base_date - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
                'created_by': random.choice(names),
            }

            # Add fields based on config
            for j, field in enumerate(fields):
                if 'date' in field.lower():
                    record[field] = (base_date + timedelta(days=random.randint(-30, 90))).strftime('%Y-%m-%d')
                elif 'status' in field.lower():
                    record[field] = random.choice(statuses)
                elif 'priority' in field.lower():
                    record[field] = random.choice(priorities)
                elif 'amount' in field.lower() or 'value' in field.lower() or 'budget' in field.lower():
                    record[field] = round(random.uniform(10000, 5000000), 2)
                elif 'pct' in field.lower() or 'variance' in field.lower():
                    record[field] = round(random.uniform(-15, 100), 1)
                elif 'hours' in field.lower():
                    record[field] = random.randint(4, 200)
                elif 'probability' in field.lower() or 'impact' in field.lower():
                    record[field] = random.choice(risk_levels)
                elif 'compliance' in field.lower():
                    record[field] = random.choice(compliance_statuses)
                elif any(x in field.lower() for x in ['owner', 'party', 'reviewer', 'assigned', 'auditor', 'by', 'maker']):
                    record[field] = random.choice(names)
                elif 'version' in field.lower():
                    record[field] = f"{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,20)}"
                elif 'environment' in field.lower():
                    record[field] = random.choice(['Production', 'Staging', 'Development', 'QA'])
                elif 'year' in field.lower():
                    record[field] = random.choice([2024, 2025, 2026])
                else:
                    # Generate descriptive text
                    prefixes = ['Review', 'Update', 'Implement', 'Assess', 'Monitor', 'Configure', 'Deploy', 'Test', 'Validate', 'Document']
                    subjects = ['system', 'module', 'process', 'component', 'interface', 'service', 'workflow', 'policy', 'requirement', 'standard']
                    record[field] = f"{random.choice(prefixes)} {subjects[j % len(subjects)]} item {i+1}"

            form_records.append(record)

        records[form_id_str] = {
            'fields': ['record_id', 'created_date', 'modified_date', 'created_by'] + fields,
            'records': form_records
        }

    return records

# Generate form records on startup
FORM_RECORDS = generate_form_records()
'''

# ============= API ENDPOINTS FOR FORM RECORDS =============
API_ENDPOINTS_CODE = '''
# ==================== FORM RECORDS CRUD API ====================

@app.route('/api/cpic-forms/<form_id>/records', methods=['GET'])
@token_required
def get_form_records(form_id):
    """Get all records for a specific form"""
    if form_id not in FORM_RECORDS:
        return jsonify({'error': 'Form not found'}), 404

    form_data = FORM_RECORDS[form_id]
    return jsonify({
        'form_id': form_id,
        'fields': form_data['fields'],
        'records': form_data['records'],
        'total_records': len(form_data['records'])
    })

@app.route('/api/cpic-forms/<form_id>/records', methods=['POST'])
@token_required
def create_form_record(form_id):
    """Create a new record in a form"""
    if form_id not in FORM_RECORDS:
        return jsonify({'error': 'Form not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Generate new record ID
    existing_records = FORM_RECORDS[form_id]['records']
    new_id = f"{form_id}-R{len(existing_records)+1:03d}"

    new_record = {
        'record_id': new_id,
        'created_date': datetime.now().strftime('%Y-%m-%d'),
        'modified_date': datetime.now().strftime('%Y-%m-%d'),
        'created_by': data.get('created_by', 'System User'),
        **{k: v for k, v in data.items() if k not in ['record_id', 'created_date', 'modified_date']}
    }

    FORM_RECORDS[form_id]['records'].append(new_record)

    return jsonify({
        'message': 'Record created successfully',
        'record': new_record
    }), 201

@app.route('/api/cpic-forms/<form_id>/records/<record_id>', methods=['GET'])
@token_required
def get_form_record(form_id, record_id):
    """Get a specific record from a form"""
    if form_id not in FORM_RECORDS:
        return jsonify({'error': 'Form not found'}), 404

    records = FORM_RECORDS[form_id]['records']
    record = next((r for r in records if r['record_id'] == record_id), None)

    if not record:
        return jsonify({'error': 'Record not found'}), 404

    return jsonify({
        'form_id': form_id,
        'fields': FORM_RECORDS[form_id]['fields'],
        'record': record
    })

@app.route('/api/cpic-forms/<form_id>/records/<record_id>', methods=['PUT'])
@token_required
def update_form_record(form_id, record_id):
    """Update a specific record in a form"""
    if form_id not in FORM_RECORDS:
        return jsonify({'error': 'Form not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    records = FORM_RECORDS[form_id]['records']
    record_idx = next((i for i, r in enumerate(records) if r['record_id'] == record_id), None)

    if record_idx is None:
        return jsonify({'error': 'Record not found'}), 404

    # Update record fields
    for key, value in data.items():
        if key != 'record_id' and key != 'created_date':
            records[record_idx][key] = value
    records[record_idx]['modified_date'] = datetime.now().strftime('%Y-%m-%d')

    return jsonify({
        'message': 'Record updated successfully',
        'record': records[record_idx]
    })

@app.route('/api/cpic-forms/<form_id>/records/<record_id>', methods=['DELETE'])
@token_required
def delete_form_record(form_id, record_id):
    """Delete a specific record from a form"""
    if form_id not in FORM_RECORDS:
        return jsonify({'error': 'Form not found'}), 404

    records = FORM_RECORDS[form_id]['records']
    record_idx = next((i for i, r in enumerate(records) if r['record_id'] == record_id), None)

    if record_idx is None:
        return jsonify({'error': 'Record not found'}), 404

    deleted_record = records.pop(record_idx)

    return jsonify({
        'message': 'Record deleted successfully',
        'deleted_record_id': deleted_record['record_id']
    })

@app.route('/api/cpic-forms/<form_id>/details', methods=['GET'])
@token_required
def get_form_details(form_id):
    """Get form details with metadata"""
    # Find form in DEMO_CPIC_FORMS
    form = next((f for f in DEMO_CPIC_FORMS if f['form_id'] == form_id), None)
    if not form:
        return jsonify({'error': 'Form not found'}), 404

    records_data = FORM_RECORDS.get(form_id, {'fields': [], 'records': []})

    return jsonify({
        'form': form,
        'fields': records_data['fields'],
        'record_count': len(records_data['records'])
    })
'''

# ============= FRONTEND UPDATE - CSS STYLES =============
FRONTEND_CSS_ADD = '''
        /* Form Detail View Styles */
        .form-detail-container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .form-detail-header {
            background: linear-gradient(135deg, #1565c0 0%, #1976d2 100%);
            color: white;
            padding: 1.5rem 2rem;
        }

        .form-detail-header h2 {
            margin: 0 0 0.5rem 0;
            font-size: 1.4rem;
        }

        .form-detail-header .form-meta {
            display: flex;
            gap: 1.5rem;
            font-size: 0.9rem;
            opacity: 0.9;
        }

        .records-toolbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            background: #f5f7fa;
            border-bottom: 1px solid #e0e0e0;
        }

        .records-table-container {
            overflow-x: auto;
            padding: 0;
        }

        .records-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        .records-table th {
            background: #37474f;
            color: white;
            padding: 0.75rem 1rem;
            text-align: left;
            font-weight: 600;
            white-space: nowrap;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .records-table td {
            padding: 0.6rem 1rem;
            border-bottom: 1px solid #e8e8e8;
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        /* Alternating row colors - blue/grey theme */
        .records-table tbody tr:nth-child(odd) {
            background: #f8fafc;
        }

        .records-table tbody tr:nth-child(even) {
            background: #e8f4fc;
        }

        .records-table tbody tr:hover {
            background: #bbdefb !important;
            cursor: pointer;
        }

        .records-table .actions-cell {
            white-space: nowrap;
            width: 120px;
        }

        .btn-icon {
            background: none;
            border: none;
            cursor: pointer;
            padding: 0.4rem;
            border-radius: 4px;
            transition: background 0.2s;
            font-size: 1.1rem;
        }

        .btn-icon:hover {
            background: rgba(0,0,0,0.1);
        }

        .btn-icon.edit { color: #1976d2; }
        .btn-icon.delete { color: #d32f2f; }
        .btn-icon.view { color: #388e3c; }

        /* Column width optimization */
        .records-table .col-id { width: 120px; }
        .records-table .col-date { width: 100px; }
        .records-table .col-status { width: 100px; }
        .records-table .col-name { width: 140px; }
        .records-table .col-amount { width: 120px; text-align: right; }
        .records-table .col-pct { width: 80px; text-align: right; }

        /* Record Edit Modal */
        .record-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            z-index: 3000;
            align-items: center;
            justify-content: center;
        }

        .record-modal.active {
            display: flex;
        }

        .record-modal-content {
            background: white;
            border-radius: 12px;
            width: 90%;
            max-width: 700px;
            max-height: 85vh;
            overflow-y: auto;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }

        .record-modal-header {
            background: #1976d2;
            color: white;
            padding: 1rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .record-modal-body {
            padding: 1.5rem;
        }

        .record-form-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }

        .record-form-grid .form-group.full-width {
            grid-column: 1 / -1;
        }

        .record-modal-footer {
            padding: 1rem 1.5rem;
            background: #f5f5f5;
            display: flex;
            justify-content: flex-end;
            gap: 1rem;
        }

        /* Pagination styles */
        .pagination {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .pagination-btn {
            padding: 0.5rem 1rem;
            border: 1px solid #ddd;
            background: white;
            border-radius: 6px;
            cursor: pointer;
        }

        .pagination-btn:hover:not(:disabled) {
            background: #e3f2fd;
            border-color: #1976d2;
        }

        .pagination-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .pagination-info {
            padding: 0 1rem;
            color: #666;
        }
'''

# ============= FRONTEND UPDATE - JAVASCRIPT FUNCTIONS =============
FRONTEND_JS_ADD = '''
        // ==================== FORM RECORDS CRUD ====================

        let currentFormId = null;
        let currentFormRecords = [];
        let currentFormFields = [];
        let currentRecordPage = 1;
        const recordsPerPage = 15;

        async function openFormDetail(formId, formName) {
            currentFormId = formId;
            const contentDiv = document.getElementById('main-content');
            contentDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading form records...</p></div>';

            try {
                // Fetch form details and records
                const [detailsRes, recordsRes] = await Promise.all([
                    apiFetch(`/api/cpic-forms/${formId}/details`),
                    apiFetch(`/api/cpic-forms/${formId}/records`)
                ]);

                let formDetails = {};
                let recordsData = { fields: [], records: [] };

                if (detailsRes.ok) {
                    const data = await detailsRes.json();
                    formDetails = data.form || {};
                }

                if (recordsRes.ok) {
                    recordsData = await recordsRes.json();
                }

                currentFormRecords = recordsData.records || [];
                currentFormFields = recordsData.fields || [];
                currentRecordPage = 1;

                renderFormDetailView(formDetails, currentFormFields, currentFormRecords);

            } catch (error) {
                contentDiv.innerHTML = `
                    <div class="alert alert-error">Error loading form: ${error.message}</div>
                    <button class="btn btn-primary" onclick="loadCPICForms()">Back to Forms</button>
                `;
            }
        }

        function renderFormDetailView(form, fields, records) {
            const contentDiv = document.getElementById('main-content');
            const totalPages = Math.ceil(records.length / recordsPerPage);
            const startIdx = (currentRecordPage - 1) * recordsPerPage;
            const endIdx = Math.min(startIdx + recordsPerPage, records.length);
            const pageRecords = records.slice(startIdx, endIdx);

            // Determine column classes based on field names
            const getColClass = (field) => {
                const f = field.toLowerCase();
                if (f.includes('id')) return 'col-id';
                if (f.includes('date')) return 'col-date';
                if (f.includes('status')) return 'col-status';
                if (f.includes('name') || f.includes('owner') || f.includes('by')) return 'col-name';
                if (f.includes('amount') || f.includes('value') || f.includes('budget')) return 'col-amount';
                if (f.includes('pct') || f.includes('variance')) return 'col-pct';
                return '';
            };

            // Format cell value based on field type
            const formatValue = (value, field) => {
                if (value === null || value === undefined) return '-';
                const f = field.toLowerCase();
                if ((f.includes('amount') || f.includes('value') || f.includes('budget')) && typeof value === 'number') {
                    return '$' + value.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                }
                if (f.includes('pct') || f.includes('variance')) {
                    return value + '%';
                }
                return String(value);
            };

            contentDiv.innerHTML = `
                <div style="margin-bottom: 1rem;">
                    <button class="btn btn-secondary" onclick="loadCPICForms()">
                        <span style="margin-right: 0.5rem;">&#8592;</span> Back to Forms
                    </button>
                </div>

                <div class="form-detail-container">
                    <div class="form-detail-header">
                        <h2>${form.form_name || 'Form'}</h2>
                        <div class="form-meta">
                            <span><strong>Form ID:</strong> ${form.form_id || currentFormId}</span>
                            <span><strong>Phase:</strong> ${form.cpic_phase || 'N/A'}</span>
                            <span><strong>Status:</strong> ${form.status || 'N/A'}</span>
                            <span><strong>Area:</strong> ${form.functional_area || 'N/A'}</span>
                        </div>
                    </div>

                    <div class="records-toolbar">
                        <div>
                            <strong>${records.length}</strong> Total Records
                            <span style="margin-left: 1rem; color: #666;">
                                Showing ${startIdx + 1}-${endIdx} of ${records.length}
                            </span>
                        </div>
                        <div style="display: flex; gap: 1rem; align-items: center;">
                            <input type="text" id="record-search" class="form-input"
                                   style="width: 200px;" placeholder="Search records..."
                                   oninput="filterRecords()">
                            <button class="btn btn-success" onclick="showAddRecordModal()">
                                + Add Record
                            </button>
                        </div>
                    </div>

                    <div class="records-table-container" style="max-height: 500px; overflow-y: auto;">
                        <table class="records-table">
                            <thead>
                                <tr>
                                    ${fields.map(f => `<th class="${getColClass(f)}">${formatFieldName(f)}</th>`).join('')}
                                    <th class="actions-cell">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="records-tbody">
                                ${pageRecords.length === 0 ?
                                    `<tr><td colspan="${fields.length + 1}" style="text-align:center; padding: 2rem;">No records found</td></tr>` :
                                    pageRecords.map((record, idx) => `
                                        <tr data-record-id="${record.record_id}">
                                            ${fields.map(f => `<td class="${getColClass(f)}" title="${record[f] || ''}">${formatValue(record[f], f)}</td>`).join('')}
                                            <td class="actions-cell">
                                                <button class="btn-icon view" onclick="viewRecord('${record.record_id}')" title="View">&#128065;</button>
                                                <button class="btn-icon edit" onclick="editRecord('${record.record_id}')" title="Edit">&#9998;</button>
                                                <button class="btn-icon delete" onclick="deleteRecord('${record.record_id}')" title="Delete">&#128465;</button>
                                            </td>
                                        </tr>
                                    `).join('')
                                }
                            </tbody>
                        </table>
                    </div>

                    <div style="padding: 1rem 2rem; background: #f5f7fa; display: flex; justify-content: center;">
                        <div class="pagination">
                            <button class="pagination-btn" onclick="changePage(-1)" ${currentRecordPage <= 1 ? 'disabled' : ''}>
                                &laquo; Previous
                            </button>
                            <span class="pagination-info">Page ${currentRecordPage} of ${totalPages || 1}</span>
                            <button class="pagination-btn" onclick="changePage(1)" ${currentRecordPage >= totalPages ? 'disabled' : ''}>
                                Next &raquo;
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Record Modal -->
                <div class="record-modal" id="record-modal">
                    <div class="record-modal-content">
                        <div class="record-modal-header">
                            <h3 id="record-modal-title">Record Details</h3>
                            <span class="close-btn" onclick="closeRecordModal()" style="cursor:pointer;font-size:1.5rem;">&times;</span>
                        </div>
                        <div class="record-modal-body" id="record-modal-body">
                        </div>
                        <div class="record-modal-footer" id="record-modal-footer">
                        </div>
                    </div>
                </div>
            `;
        }

        function formatFieldName(field) {
            return field.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
        }

        function changePage(delta) {
            const totalPages = Math.ceil(currentFormRecords.length / recordsPerPage);
            const newPage = currentRecordPage + delta;
            if (newPage >= 1 && newPage <= totalPages) {
                currentRecordPage = newPage;
                // Re-fetch form details
                apiFetch(`/api/cpic-forms/${currentFormId}/details`).then(res => res.json()).then(data => {
                    renderFormDetailView(data.form || {}, currentFormFields, currentFormRecords);
                });
            }
        }

        function filterRecords() {
            const searchTerm = document.getElementById('record-search').value.toLowerCase();
            const rows = document.querySelectorAll('#records-tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }

        function viewRecord(recordId) {
            const record = currentFormRecords.find(r => r.record_id === recordId);
            if (!record) return;

            document.getElementById('record-modal-title').textContent = `View Record: ${recordId}`;
            document.getElementById('record-modal-body').innerHTML = `
                <div class="record-form-grid">
                    ${currentFormFields.map(field => `
                        <div class="form-group">
                            <label class="form-label">${formatFieldName(field)}</label>
                            <div style="padding: 0.5rem; background: #f5f5f5; border-radius: 6px; min-height: 38px;">
                                ${record[field] || '-'}
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            document.getElementById('record-modal-footer').innerHTML = `
                <button class="btn btn-secondary" onclick="closeRecordModal()">Close</button>
                <button class="btn btn-primary" onclick="editRecord('${recordId}')">Edit</button>
            `;
            document.getElementById('record-modal').classList.add('active');
        }

        function showAddRecordModal() {
            document.getElementById('record-modal-title').textContent = 'Add New Record';
            const editableFields = currentFormFields.filter(f => !['record_id', 'created_date', 'modified_date'].includes(f));

            document.getElementById('record-modal-body').innerHTML = `
                <form id="add-record-form">
                    <div class="record-form-grid">
                        ${editableFields.map(field => `
                            <div class="form-group">
                                <label class="form-label">${formatFieldName(field)}</label>
                                <input type="text" class="form-input" name="${field}" placeholder="Enter ${formatFieldName(field).toLowerCase()}">
                            </div>
                        `).join('')}
                    </div>
                </form>
            `;
            document.getElementById('record-modal-footer').innerHTML = `
                <button class="btn btn-secondary" onclick="closeRecordModal()">Cancel</button>
                <button class="btn btn-success" onclick="saveNewRecord()">Save Record</button>
            `;
            document.getElementById('record-modal').classList.add('active');
        }

        function editRecord(recordId) {
            const record = currentFormRecords.find(r => r.record_id === recordId);
            if (!record) return;

            const editableFields = currentFormFields.filter(f => !['record_id', 'created_date', 'modified_date'].includes(f));

            document.getElementById('record-modal-title').textContent = `Edit Record: ${recordId}`;
            document.getElementById('record-modal-body').innerHTML = `
                <form id="edit-record-form" data-record-id="${recordId}">
                    <div class="record-form-grid">
                        ${editableFields.map(field => `
                            <div class="form-group">
                                <label class="form-label">${formatFieldName(field)}</label>
                                <input type="text" class="form-input" name="${field}" value="${record[field] || ''}">
                            </div>
                        `).join('')}
                    </div>
                </form>
            `;
            document.getElementById('record-modal-footer').innerHTML = `
                <button class="btn btn-secondary" onclick="closeRecordModal()">Cancel</button>
                <button class="btn btn-primary" onclick="saveEditedRecord('${recordId}')">Save Changes</button>
            `;
            document.getElementById('record-modal').classList.add('active');
        }

        async function saveNewRecord() {
            const form = document.getElementById('add-record-form');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            data.created_by = currentUser?.name || 'System User';

            try {
                const response = await apiFetch(`/api/cpic-forms/${currentFormId}/records`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    const result = await response.json();
                    currentFormRecords.push(result.record);
                    closeRecordModal();
                    openFormDetail(currentFormId, '');
                    showNotification('Record added successfully', 'success');
                } else {
                    const error = await response.json();
                    showNotification(error.error || 'Failed to add record', 'error');
                }
            } catch (error) {
                showNotification('Error adding record: ' + error.message, 'error');
            }
        }

        async function saveEditedRecord(recordId) {
            const form = document.getElementById('edit-record-form');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await apiFetch(`/api/cpic-forms/${currentFormId}/records/${recordId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    closeRecordModal();
                    openFormDetail(currentFormId, '');
                    showNotification('Record updated successfully', 'success');
                } else {
                    const error = await response.json();
                    showNotification(error.error || 'Failed to update record', 'error');
                }
            } catch (error) {
                showNotification('Error updating record: ' + error.message, 'error');
            }
        }

        async function deleteRecord(recordId) {
            if (!confirm('Are you sure you want to delete this record? This action cannot be undone.')) {
                return;
            }

            try {
                const response = await apiFetch(`/api/cpic-forms/${currentFormId}/records/${recordId}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    currentFormRecords = currentFormRecords.filter(r => r.record_id !== recordId);
                    openFormDetail(currentFormId, '');
                    showNotification('Record deleted successfully', 'success');
                } else {
                    const error = await response.json();
                    showNotification(error.error || 'Failed to delete record', 'error');
                }
            } catch (error) {
                showNotification('Error deleting record: ' + error.message, 'error');
            }
        }

        function closeRecordModal() {
            document.getElementById('record-modal').classList.remove('active');
        }

        function showNotification(message, type = 'info') {
            // Create notification element
            const notif = document.createElement('div');
            notif.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'error' : 'info'}`;
            notif.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999; min-width: 300px; animation: slideIn 0.3s ease;';
            notif.textContent = message;
            document.body.appendChild(notif);

            setTimeout(() => {
                notif.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => notif.remove(), 300);
            }, 3000);
        }
'''

def update_main_py(filepath):
    """Update the main.py file with form records code"""
    print(f"Updating {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already updated
    if 'FORM_RECORDS' in content:
        print(f"  {filepath} already contains FORM_RECORDS - skipping data insert")
    else:
        # Find a good insertion point - after imports and before DEMO_INVESTMENTS
        # Insert form records generator after existing imports
        insert_marker = "from flask_cors import CORS"
        if insert_marker in content:
            insert_pos = content.find(insert_marker) + len(insert_marker)
            # Find end of imports section
            next_newlines = content.find('\n\n', insert_pos)
            if next_newlines > 0:
                content = content[:next_newlines] + '\n' + FORM_RECORDS_CODE + content[next_newlines:]
                print(f"  Added FORM_RECORDS generator code")

    # Check if API endpoints already added
    if '/api/cpic-forms/<form_id>/records' in content:
        print(f"  {filepath} already contains form records API endpoints - skipping")
    else:
        # Find the location before if __name__ == '__main__'
        main_marker = "if __name__ == '__main__':"
        if main_marker in content:
            insert_pos = content.find(main_marker)
            content = content[:insert_pos] + API_ENDPOINTS_CODE + '\n\n' + content[insert_pos:]
            print(f"  Added form records API endpoints")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  Completed updating {filepath}")

def update_frontend(filepath, form_count):
    """Update the frontend HTML with form detail view"""
    print(f"Updating {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already updated
    if 'form-detail-container' in content:
        print(f"  {filepath} already contains form detail styles - skipping CSS")
    else:
        # Add CSS before </style>
        style_end = content.rfind('</style>')
        if style_end > 0:
            content = content[:style_end] + FRONTEND_CSS_ADD + '\n    ' + content[style_end:]
            print(f"  Added form detail CSS styles")

    # Check if JS functions already added
    if 'openFormDetail' in content:
        print(f"  {filepath} already contains form detail JS - skipping")
    else:
        # Add JS before the closing </script> tag
        script_end = content.rfind('</script>')
        if script_end > 0:
            content = content[:script_end] + FRONTEND_JS_ADD + '\n    ' + content[script_end:]
            print(f"  Added form detail JavaScript functions")

    # Update the forms table rows to be clickable
    # Find the forms table row template and add onclick
    old_row_pattern = r'<tr class="form-row"'
    new_row_onclick = '<tr class="form-row" onclick="openFormDetail(\'${f.form_id}\', \'${f.form_name}\')" style="cursor:pointer;"'

    # More robust update - find the table rows in loadCPICForms function
    if 'onclick="openFormDetail' not in content:
        # Update the form rows to be clickable
        content = content.replace(
            '<tr class="form-row"',
            '<tr class="form-row" style="cursor:pointer;"'
        )

        # Find and update the form row template - need to add onclick properly
        # The template uses ${f.form_id} so we need to use template literal style
        old_td = '<td><strong>${f.form_id}</strong></td>'
        new_td = '<td onclick="openFormDetail(\\\'$${f.form_id}\\\', \\\'$${f.form_name}\\\'); event.stopPropagation();"><strong>${f.form_id}</strong> <span style="font-size:0.75rem;color:#1976d2;">&#128065; View</span></td>'

        if old_td in content:
            content = content.replace(old_td, new_td)
            print(f"  Added click handler to form rows")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  Completed updating {filepath}")

def main():
    print("=" * 60)
    print("CPIC Forms CRUD Update Script")
    print("=" * 60)

    base_path = r"C:\1AITrading\Trading"

    # Update Solution A
    print("\n--- Updating Solution A (9 Investments, 134 Forms) ---")
    update_main_py(os.path.join(base_path, "cpic_suggestion_a", "backend", "main.py"))
    update_frontend(os.path.join(base_path, "cpic_suggestion_a", "backend", "frontend", "index.html"), 134)

    # Update Solution B
    print("\n--- Updating Solution B (15 Investments, 185 Forms) ---")
    update_main_py(os.path.join(base_path, "cpic_suggestion_b", "backend", "main.py"))
    update_frontend(os.path.join(base_path, "cpic_suggestion_b", "backend", "frontend", "index.html"), 185)

    print("\n" + "=" * 60)
    print("Update complete! Now deploy both solutions:")
    print("=" * 60)
    print("""
Next steps:
1. Deploy Solution A:
   cd cpic_suggestion_a
   gcloud run deploy irs-cpic-solution-a --source . --region us-central1 --allow-unauthenticated --memory 512Mi --project cryptobot-462709

2. Deploy Solution B:
   cd cpic_suggestion_b
   gcloud run deploy irs-cpic-solution-b --source . --region us-central1 --allow-unauthenticated --memory 512Mi --project cryptobot-462709
""")

if __name__ == "__main__":
    main()
