import React, { useState, useCallback } from 'react';

// Organization data structure with personnel details
const organizationData = {
  mission: "Transform financial markets through AI-powered algorithmic trading, delivering superior returns while maintaining the highest standards of risk management and regulatory compliance.",
  vision: "To be the leading AI-driven trading platform that democratizes institutional-grade trading strategies for all investors.",
  values: ["Innovation", "Integrity", "Excellence", "Transparency", "Client-First"],

  departments: [
    {
      id: 'exec',
      name: 'Executive Leadership',
      head: 'CEO',
      color: '#1a365d',
      personnel: [
        {
          id: 'ceo',
          name: 'Irfan Qazi',
          title: 'Chief Executive Officer',
          email: 'irfan.qazi@aialgotradehits.com',
          phone: '+1-555-CEO-0001',
          location: 'HQ - New York',
          reportsTo: null,
          directReports: ['cto', 'cfo', 'coo', 'cio'],
          responsibilities: [
            'Overall company strategy and direction',
            'Board relations and investor communications',
            'Key partnership negotiations',
            'Final approval on major investments'
          ],
          kpis: ['Revenue growth', 'Market share', 'Shareholder value', 'Strategic milestones'],
          schedule: { workHours: '7:00 AM - 7:00 PM', timezone: 'EST' }
        }
      ]
    },
    {
      id: 'tech',
      name: 'Technology',
      head: 'CTO',
      color: '#2c5282',
      personnel: [
        {
          id: 'cto',
          name: 'M. Saleem Ahmad',
          title: 'Chief Technology Officer',
          email: 'saleem@aialgotradehits.com',
          phone: '+1-555-CTO-0001',
          location: 'HQ - New York',
          reportsTo: 'ceo',
          directReports: ['vp-engineering', 'vp-data', 'vp-infra'],
          responsibilities: [
            'Technology strategy and roadmap',
            'AI/ML model development oversight',
            'System architecture decisions',
            'Tech team hiring and development'
          ],
          kpis: ['System uptime (99.99%)', 'Model accuracy', 'Development velocity', 'Tech debt ratio'],
          schedule: { workHours: '8:00 AM - 6:00 PM', timezone: 'EST' }
        },
        {
          id: 'vp-engineering',
          name: 'TBD',
          title: 'VP of Engineering',
          email: 'vp.engineering@aialgotradehits.com',
          reportsTo: 'cto',
          directReports: ['lead-backend', 'lead-frontend', 'lead-devops'],
          responsibilities: [
            'Engineering team management',
            'Sprint planning and delivery',
            'Code quality standards',
            'Technical debt management'
          ],
          kpis: ['Sprint velocity', 'Bug resolution time', 'Code coverage', 'Team satisfaction'],
          status: 'Open Position'
        },
        {
          id: 'vp-data',
          name: 'TBD',
          title: 'VP of Data Science',
          email: 'vp.data@aialgotradehits.com',
          reportsTo: 'cto',
          directReports: ['lead-ml', 'lead-analytics', 'lead-quant'],
          responsibilities: [
            'ML model development',
            'Trading strategy research',
            'Data pipeline architecture',
            'Model performance monitoring'
          ],
          kpis: ['Model accuracy', 'Prediction latency', 'Strategy alpha', 'Data freshness'],
          status: 'Open Position'
        },
        {
          id: 'lead-backend',
          name: 'TBD',
          title: 'Lead Backend Engineer',
          reportsTo: 'vp-engineering',
          responsibilities: ['API development', 'Database optimization', 'Microservices architecture'],
          status: 'Open Position'
        },
        {
          id: 'lead-frontend',
          name: 'TBD',
          title: 'Lead Frontend Engineer',
          reportsTo: 'vp-engineering',
          responsibilities: ['UI/UX implementation', 'React component library', 'Performance optimization'],
          status: 'Open Position'
        },
        {
          id: 'lead-devops',
          name: 'TBD',
          title: 'Lead DevOps Engineer',
          reportsTo: 'vp-engineering',
          responsibilities: ['CI/CD pipelines', 'Cloud infrastructure', 'Security compliance'],
          status: 'Open Position'
        }
      ]
    },
    {
      id: 'finance',
      name: 'Finance',
      head: 'CFO',
      color: '#276749',
      personnel: [
        {
          id: 'cfo',
          name: 'TBD',
          title: 'Chief Financial Officer',
          reportsTo: 'ceo',
          directReports: ['controller', 'fp-manager', 'treasury-manager'],
          responsibilities: [
            'Financial strategy and planning',
            'Investor relations',
            'Regulatory compliance',
            'Risk management'
          ],
          kpis: ['Profitability', 'Cash flow', 'Compliance rate', 'Budget variance'],
          status: 'Open Position'
        }
      ]
    },
    {
      id: 'operations',
      name: 'Operations',
      head: 'COO',
      color: '#744210',
      personnel: [
        {
          id: 'coo',
          name: 'TBD',
          title: 'Chief Operating Officer',
          reportsTo: 'ceo',
          directReports: ['vp-ops', 'vp-support', 'vp-compliance'],
          responsibilities: [
            'Day-to-day operations',
            'Process optimization',
            'Vendor management',
            'Operational excellence'
          ],
          kpis: ['Operational efficiency', 'SLA compliance', 'Cost reduction', 'Process improvement'],
          status: 'Open Position'
        }
      ]
    },
    {
      id: 'investment',
      name: 'Investment',
      head: 'CIO',
      color: '#553c9a',
      personnel: [
        {
          id: 'cio',
          name: 'TBD',
          title: 'Chief Investment Officer',
          reportsTo: 'ceo',
          directReports: ['pm-equities', 'pm-crypto', 'pm-forex', 'risk-manager'],
          responsibilities: [
            'Investment strategy',
            'Portfolio construction',
            'Risk oversight',
            'Performance attribution'
          ],
          kpis: ['Portfolio returns', 'Sharpe ratio', 'Max drawdown', 'Risk-adjusted alpha'],
          status: 'Open Position'
        },
        {
          id: 'pm-equities',
          name: 'TBD',
          title: 'Portfolio Manager - Equities',
          reportsTo: 'cio',
          responsibilities: ['Stock selection', 'Sector allocation', 'Equity derivatives'],
          status: 'Open Position'
        },
        {
          id: 'pm-crypto',
          name: 'TBD',
          title: 'Portfolio Manager - Crypto',
          reportsTo: 'cio',
          responsibilities: ['Crypto asset selection', 'DeFi strategies', 'Blockchain analysis'],
          status: 'Open Position'
        },
        {
          id: 'pm-forex',
          name: 'TBD',
          title: 'Portfolio Manager - Forex',
          reportsTo: 'cio',
          responsibilities: ['Currency pair trading', 'Macro analysis', 'FX derivatives'],
          status: 'Open Position'
        },
        {
          id: 'risk-manager',
          name: 'TBD',
          title: 'Head of Risk Management',
          reportsTo: 'cio',
          responsibilities: ['Risk modeling', 'Position limits', 'Stress testing', 'VaR calculations'],
          status: 'Open Position'
        }
      ]
    }
  ]
};

// Portfolio Lifecycle Steps (17 steps like IRS)
const portfolioLifecycle = [
  {
    step: 1,
    phase: 'Initiation',
    name: 'Strategic Alignment',
    description: 'Align portfolio with organizational mission and investment objectives',
    deliverables: ['Investment Policy Statement', 'Strategic Objectives Document'],
    duration: '2 weeks',
    responsible: 'CEO, CIO',
    gate: 'Strategy Approval Gate'
  },
  {
    step: 2,
    phase: 'Initiation',
    name: 'Portfolio Chartering',
    description: 'Define portfolio scope, governance structure, and success criteria',
    deliverables: ['Portfolio Charter', 'Governance Framework'],
    duration: '1 week',
    responsible: 'CIO, COO',
    gate: 'Charter Approval'
  },
  {
    step: 3,
    phase: 'Planning',
    name: 'Asset Allocation Strategy',
    description: 'Determine target asset allocation across classes',
    deliverables: ['Asset Allocation Model', 'Risk Budget'],
    duration: '2 weeks',
    responsible: 'CIO, Risk Manager',
    gate: 'Allocation Approval'
  },
  {
    step: 4,
    phase: 'Planning',
    name: 'Investment Universe Definition',
    description: 'Define eligible securities, exchanges, and instruments',
    deliverables: ['Investment Universe Document', 'Eligibility Criteria'],
    duration: '1 week',
    responsible: 'CIO, Compliance',
    gate: 'Universe Approval'
  },
  {
    step: 5,
    phase: 'Planning',
    name: 'Model Development',
    description: 'Develop AI/ML models for trading signals and predictions',
    deliverables: ['Model Specifications', 'Backtesting Results'],
    duration: '4 weeks',
    responsible: 'CTO, VP Data Science',
    gate: 'Model Validation Gate'
  },
  {
    step: 6,
    phase: 'Planning',
    name: 'Risk Framework Setup',
    description: 'Establish risk limits, monitoring systems, and controls',
    deliverables: ['Risk Limits Document', 'Monitoring Dashboard'],
    duration: '2 weeks',
    responsible: 'Risk Manager, CTO',
    gate: 'Risk Framework Approval'
  },
  {
    step: 7,
    phase: 'Execution',
    name: 'System Integration',
    description: 'Integrate trading systems, data feeds, and execution platforms',
    deliverables: ['Integration Test Results', 'System Architecture'],
    duration: '3 weeks',
    responsible: 'CTO, VP Engineering',
    gate: 'System Readiness Gate'
  },
  {
    step: 8,
    phase: 'Execution',
    name: 'Paper Trading',
    description: 'Simulate trading strategies without real capital',
    deliverables: ['Paper Trading Report', 'Performance Metrics'],
    duration: '4 weeks',
    responsible: 'CIO, Portfolio Managers',
    gate: 'Paper Trading Validation'
  },
  {
    step: 9,
    phase: 'Execution',
    name: 'Pilot Deployment',
    description: 'Deploy with limited capital to validate real-world performance',
    deliverables: ['Pilot Results Report', 'Issue Log'],
    duration: '4 weeks',
    responsible: 'CIO, Risk Manager',
    gate: 'Pilot Approval Gate'
  },
  {
    step: 10,
    phase: 'Execution',
    name: 'Full Production Launch',
    description: 'Scale to full production with target capital allocation',
    deliverables: ['Launch Checklist', 'Go-Live Report'],
    duration: '1 week',
    responsible: 'CEO, CIO, CTO',
    gate: 'Production Gate'
  },
  {
    step: 11,
    phase: 'Monitoring',
    name: 'Daily Operations',
    description: 'Monitor daily trading activity, P&L, and system health',
    deliverables: ['Daily Reports', 'Alert Logs'],
    duration: 'Ongoing',
    responsible: 'Operations Team',
    gate: 'Daily Review'
  },
  {
    step: 12,
    phase: 'Monitoring',
    name: 'Performance Attribution',
    description: 'Analyze sources of portfolio returns and risk',
    deliverables: ['Attribution Report', 'Factor Analysis'],
    duration: 'Weekly',
    responsible: 'CIO, Risk Manager',
    gate: 'Weekly Review'
  },
  {
    step: 13,
    phase: 'Monitoring',
    name: 'Risk Monitoring',
    description: 'Track risk metrics, exposures, and limit breaches',
    deliverables: ['Risk Dashboard', 'Limit Breach Reports'],
    duration: 'Continuous',
    responsible: 'Risk Manager',
    gate: 'Risk Review'
  },
  {
    step: 14,
    phase: 'Optimization',
    name: 'Model Recalibration',
    description: 'Retrain and optimize AI models based on market conditions',
    deliverables: ['Recalibration Report', 'Updated Model'],
    duration: 'Monthly',
    responsible: 'VP Data Science',
    gate: 'Model Update Approval'
  },
  {
    step: 15,
    phase: 'Optimization',
    name: 'Strategy Enhancement',
    description: 'Research and test new trading strategies',
    deliverables: ['Strategy Research Report', 'Backtesting Results'],
    duration: 'Quarterly',
    responsible: 'CIO, Portfolio Managers',
    gate: 'Strategy Approval'
  },
  {
    step: 16,
    phase: 'Reporting',
    name: 'Stakeholder Reporting',
    description: 'Generate reports for investors, regulators, and management',
    deliverables: ['Investor Reports', 'Regulatory Filings'],
    duration: 'Monthly/Quarterly',
    responsible: 'CFO, Compliance',
    gate: 'Report Approval'
  },
  {
    step: 17,
    phase: 'Governance',
    name: 'Portfolio Review & Rebalancing',
    description: 'Strategic review of portfolio and rebalancing decisions',
    deliverables: ['Review Report', 'Rebalancing Plan'],
    duration: 'Quarterly',
    responsible: 'CEO, CIO, Board',
    gate: 'Quarterly Review Gate'
  }
];

// Meeting templates
const meetingTemplates = [
  {
    id: 'daily-standup',
    name: 'Daily Trading Standup',
    duration: 15,
    recurrence: 'Daily',
    time: '8:30 AM',
    attendees: ['CIO', 'Portfolio Managers', 'Risk Manager'],
    agenda: ['Market overview', 'Position review', 'Day plan']
  },
  {
    id: 'weekly-risk',
    name: 'Weekly Risk Review',
    duration: 60,
    recurrence: 'Weekly',
    day: 'Monday',
    time: '9:00 AM',
    attendees: ['CIO', 'Risk Manager', 'Portfolio Managers'],
    agenda: ['Risk metrics review', 'Limit utilization', 'Action items']
  },
  {
    id: 'weekly-tech',
    name: 'Technology Sprint Review',
    duration: 60,
    recurrence: 'Weekly',
    day: 'Friday',
    time: '2:00 PM',
    attendees: ['CTO', 'VP Engineering', 'VP Data Science'],
    agenda: ['Sprint progress', 'Blockers', 'Next sprint planning']
  },
  {
    id: 'monthly-perf',
    name: 'Monthly Performance Review',
    duration: 90,
    recurrence: 'Monthly',
    week: 'First',
    day: 'Monday',
    time: '10:00 AM',
    attendees: ['CEO', 'CIO', 'CFO', 'Risk Manager'],
    agenda: ['Performance attribution', 'Risk analysis', 'Strategy review']
  },
  {
    id: 'quarterly-board',
    name: 'Quarterly Board Meeting',
    duration: 180,
    recurrence: 'Quarterly',
    attendees: ['Board Members', 'C-Suite'],
    agenda: ['Financial review', 'Strategic initiatives', 'Risk overview', 'Next quarter plan']
  }
];

const OrganizationChart = () => {
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [activeTab, setActiveTab] = useState('org');
  const [selectedPhase, setSelectedPhase] = useState('all');
  const [selectedMeeting, setSelectedMeeting] = useState(null);

  const phases = ['Initiation', 'Planning', 'Execution', 'Monitoring', 'Optimization', 'Reporting', 'Governance'];

  const getPhaseColor = (phase) => {
    const colors = {
      'Initiation': '#3182ce',
      'Planning': '#38a169',
      'Execution': '#d69e2e',
      'Monitoring': '#805ad5',
      'Optimization': '#dd6b20',
      'Reporting': '#319795',
      'Governance': '#e53e3e'
    };
    return colors[phase] || '#718096';
  };

  const renderOrgChart = () => (
    <div className="space-y-6">
      {/* Mission & Vision */}
      <div className="bg-gradient-to-r from-blue-900 to-blue-700 rounded-lg p-6 text-white">
        <h3 className="text-xl font-bold mb-2">Mission</h3>
        <p className="text-blue-100 mb-4">{organizationData.mission}</p>
        <h3 className="text-xl font-bold mb-2">Vision</h3>
        <p className="text-blue-100 mb-4">{organizationData.vision}</p>
        <div className="flex flex-wrap gap-2">
          <span className="font-semibold">Core Values:</span>
          {organizationData.values.map((value, i) => (
            <span key={i} className="bg-blue-600 px-3 py-1 rounded-full text-sm">{value}</span>
          ))}
        </div>
      </div>

      {/* Org Chart */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Organization Structure</h3>

        {organizationData.departments.map((dept) => (
          <div key={dept.id} className="mb-6">
            <div
              className="text-white px-4 py-2 rounded-t-lg font-semibold"
              style={{ backgroundColor: dept.color }}
            >
              {dept.name}
            </div>
            <div className="border border-gray-200 rounded-b-lg p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {dept.personnel.map((person) => (
                <div
                  key={person.id}
                  className={`p-4 rounded-lg cursor-pointer transition-all ${
                    person.status === 'Open Position'
                      ? 'bg-yellow-50 border-2 border-dashed border-yellow-400 hover:bg-yellow-100'
                      : 'bg-gray-50 border border-gray-200 hover:shadow-md hover:border-blue-400'
                  }`}
                  onClick={() => setSelectedPerson(person)}
                >
                  <div className="font-semibold text-gray-800">{person.name}</div>
                  <div className="text-sm text-gray-600">{person.title}</div>
                  {person.status === 'Open Position' && (
                    <span className="inline-block mt-2 text-xs bg-yellow-200 text-yellow-800 px-2 py-1 rounded">
                      Open Position
                    </span>
                  )}
                  {person.email && !person.status && (
                    <div className="text-xs text-gray-500 mt-1">{person.email}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Person Details Modal */}
      {selectedPerson && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">{selectedPerson.name}</h2>
                  <p className="text-lg text-gray-600">{selectedPerson.title}</p>
                </div>
                <button
                  onClick={() => setSelectedPerson(null)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  &times;
                </button>
              </div>

              {selectedPerson.status !== 'Open Position' && (
                <div className="grid grid-cols-2 gap-4 mb-6 text-sm">
                  {selectedPerson.email && (
                    <div>
                      <span className="text-gray-500">Email:</span>
                      <div className="font-medium">{selectedPerson.email}</div>
                    </div>
                  )}
                  {selectedPerson.phone && (
                    <div>
                      <span className="text-gray-500">Phone:</span>
                      <div className="font-medium">{selectedPerson.phone}</div>
                    </div>
                  )}
                  {selectedPerson.location && (
                    <div>
                      <span className="text-gray-500">Location:</span>
                      <div className="font-medium">{selectedPerson.location}</div>
                    </div>
                  )}
                  {selectedPerson.schedule && (
                    <div>
                      <span className="text-gray-500">Work Hours:</span>
                      <div className="font-medium">{selectedPerson.schedule.workHours} ({selectedPerson.schedule.timezone})</div>
                    </div>
                  )}
                </div>
              )}

              {selectedPerson.responsibilities && (
                <div className="mb-4">
                  <h4 className="font-semibold text-gray-700 mb-2">Key Responsibilities</h4>
                  <ul className="list-disc list-inside text-gray-600 space-y-1">
                    {selectedPerson.responsibilities.map((resp, i) => (
                      <li key={i}>{resp}</li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedPerson.kpis && (
                <div className="mb-4">
                  <h4 className="font-semibold text-gray-700 mb-2">KPIs</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedPerson.kpis.map((kpi, i) => (
                      <span key={i} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                        {kpi}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedPerson.directReports && selectedPerson.directReports.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">Direct Reports</h4>
                  <div className="text-gray-600">{selectedPerson.directReports.length} direct reports</div>
                </div>
              )}

              {selectedPerson.status === 'Open Position' && (
                <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
                  <h4 className="font-semibold text-yellow-800 mb-2">Position Available</h4>
                  <p className="text-yellow-700">This position is currently open. Contact HR for more details.</p>
                  <button className="mt-2 bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700">
                    Apply Now
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderLifecycle = () => (
    <div className="space-y-6">
      {/* Phase Filter */}
      <div className="flex flex-wrap gap-2 mb-4">
        <button
          className={`px-4 py-2 rounded-lg ${selectedPhase === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          onClick={() => setSelectedPhase('all')}
        >
          All Phases
        </button>
        {phases.map((phase) => (
          <button
            key={phase}
            className={`px-4 py-2 rounded-lg ${selectedPhase === phase ? 'text-white' : 'bg-gray-200'}`}
            style={{ backgroundColor: selectedPhase === phase ? getPhaseColor(phase) : undefined }}
            onClick={() => setSelectedPhase(phase)}
          >
            {phase}
          </button>
        ))}
      </div>

      {/* Lifecycle Steps */}
      <div className="space-y-4">
        {portfolioLifecycle
          .filter(step => selectedPhase === 'all' || step.phase === selectedPhase)
          .map((step) => (
            <div
              key={step.step}
              className="bg-white rounded-lg shadow-md overflow-hidden"
            >
              <div
                className="px-4 py-3 text-white flex items-center justify-between"
                style={{ backgroundColor: getPhaseColor(step.phase) }}
              >
                <div className="flex items-center gap-3">
                  <span className="bg-white bg-opacity-30 px-3 py-1 rounded-full text-sm font-bold">
                    Step {step.step}
                  </span>
                  <span className="font-semibold">{step.name}</span>
                </div>
                <span className="text-sm bg-white bg-opacity-20 px-3 py-1 rounded">
                  {step.phase}
                </span>
              </div>
              <div className="p-4">
                <p className="text-gray-700 mb-4">{step.description}</p>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="text-gray-500 font-medium">Duration</div>
                    <div className="text-gray-800">{step.duration}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 font-medium">Responsible</div>
                    <div className="text-gray-800">{step.responsible}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 font-medium">Gate</div>
                    <div className="text-gray-800">{step.gate}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 font-medium">Deliverables</div>
                    <ul className="list-disc list-inside text-gray-800">
                      {step.deliverables.map((d, i) => (
                        <li key={i} className="text-xs">{d}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          ))}
      </div>
    </div>
  );

  const renderMeetings = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Meeting Schedule Templates</h3>
        <p className="text-gray-600 mb-6">
          Standard meeting templates for portfolio management. Export to Outlook for calendar integration.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {meetingTemplates.map((meeting) => (
            <div
              key={meeting.id}
              className="border rounded-lg p-4 hover:shadow-md cursor-pointer transition-all"
              onClick={() => setSelectedMeeting(meeting)}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-semibold text-gray-800">{meeting.name}</h4>
                  <p className="text-sm text-gray-600">{meeting.recurrence} - {meeting.duration} min</p>
                </div>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                  {meeting.time || 'TBD'}
                </span>
              </div>
              <div className="mt-2 text-sm text-gray-500">
                {meeting.attendees.length} attendees
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Calendar View */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Weekly Calendar View</h3>
        <div className="grid grid-cols-7 gap-2">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
            <div key={day} className="text-center font-semibold text-gray-600 py-2 border-b">
              {day}
            </div>
          ))}
          {Array(35).fill(0).map((_, i) => {
            const dayNum = i - 3 + 1;
            const isToday = dayNum === new Date().getDate();
            const hasMeeting = [2, 6, 9, 13, 16, 20, 23, 27].includes(dayNum);

            return (
              <div
                key={i}
                className={`min-h-[80px] p-2 border rounded ${
                  dayNum > 0 && dayNum <= 31
                    ? isToday
                      ? 'bg-blue-50 border-blue-400'
                      : 'bg-white'
                    : 'bg-gray-50'
                }`}
              >
                {dayNum > 0 && dayNum <= 31 && (
                  <>
                    <div className={`text-sm ${isToday ? 'font-bold text-blue-600' : 'text-gray-600'}`}>
                      {dayNum}
                    </div>
                    {hasMeeting && (
                      <div className="text-xs bg-green-100 text-green-800 px-1 py-0.5 rounded mt-1">
                        Meeting
                      </div>
                    )}
                  </>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Meeting Detail Modal */}
      {selectedMeeting && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-lg w-full">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-xl font-bold text-gray-800">{selectedMeeting.name}</h2>
                <button
                  onClick={() => setSelectedMeeting(null)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  &times;
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-gray-500 text-sm">Recurrence</span>
                    <div className="font-medium">{selectedMeeting.recurrence}</div>
                  </div>
                  <div>
                    <span className="text-gray-500 text-sm">Duration</span>
                    <div className="font-medium">{selectedMeeting.duration} minutes</div>
                  </div>
                  <div>
                    <span className="text-gray-500 text-sm">Time</span>
                    <div className="font-medium">{selectedMeeting.time || 'To be scheduled'}</div>
                  </div>
                  {selectedMeeting.day && (
                    <div>
                      <span className="text-gray-500 text-sm">Day</span>
                      <div className="font-medium">{selectedMeeting.day}</div>
                    </div>
                  )}
                </div>

                <div>
                  <span className="text-gray-500 text-sm">Attendees</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {selectedMeeting.attendees.map((att, i) => (
                      <span key={i} className="bg-gray-100 px-3 py-1 rounded-full text-sm">
                        {att}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <span className="text-gray-500 text-sm">Agenda</span>
                  <ul className="list-disc list-inside mt-1">
                    {selectedMeeting.agenda.map((item, i) => (
                      <li key={i} className="text-gray-700">{item}</li>
                    ))}
                  </ul>
                </div>

                <div className="flex gap-2 mt-6">
                  <button className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    Export to Outlook
                  </button>
                  <button className="flex-1 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                    Schedule Now
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderDeliverables = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Goals & Deliverables Tracking</h3>

        {/* Strategic Goals */}
        <div className="mb-8">
          <h4 className="font-semibold text-gray-700 mb-4">Strategic Goals (Annual)</h4>
          <div className="space-y-4">
            {[
              { goal: 'Achieve 25% annual return', progress: 68, status: 'On Track' },
              { goal: 'Reduce max drawdown to <10%', progress: 85, status: 'On Track' },
              { goal: 'Launch crypto trading module', progress: 100, status: 'Complete' },
              { goal: 'Onboard 100 beta users', progress: 45, status: 'At Risk' },
              { goal: 'Achieve regulatory compliance', progress: 75, status: 'On Track' },
            ].map((item, i) => (
              <div key={i} className="border rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium text-gray-800">{item.goal}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    item.status === 'Complete' ? 'bg-green-100 text-green-800' :
                    item.status === 'On Track' ? 'bg-blue-100 text-blue-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {item.status}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      item.progress === 100 ? 'bg-green-500' :
                      item.progress >= 60 ? 'bg-blue-500' :
                      'bg-yellow-500'
                    }`}
                    style={{ width: `${item.progress}%` }}
                  ></div>
                </div>
                <div className="text-right text-sm text-gray-500 mt-1">{item.progress}%</div>
              </div>
            ))}
          </div>
        </div>

        {/* Quarterly Deliverables */}
        <div>
          <h4 className="font-semibold text-gray-700 mb-4">Q4 2025 Deliverables</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left p-3">Deliverable</th>
                  <th className="text-left p-3">Owner</th>
                  <th className="text-left p-3">Due Date</th>
                  <th className="text-left p-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { name: 'AI Model v2.0 Release', owner: 'VP Data Science', due: 'Dec 15', status: 'In Progress' },
                  { name: 'Risk Dashboard Enhancement', owner: 'VP Engineering', due: 'Dec 1', status: 'Complete' },
                  { name: 'Forex Module Launch', owner: 'CIO', due: 'Dec 20', status: 'In Progress' },
                  { name: 'Annual Performance Report', owner: 'CFO', due: 'Dec 31', status: 'Not Started' },
                  { name: 'Infrastructure Upgrade', owner: 'CTO', due: 'Nov 30', status: 'Complete' },
                ].map((item, i) => (
                  <tr key={i} className="border-b">
                    <td className="p-3 font-medium">{item.name}</td>
                    <td className="p-3 text-gray-600">{item.owner}</td>
                    <td className="p-3 text-gray-600">{item.due}</td>
                    <td className="p-3">
                      <span className={`text-xs px-2 py-1 rounded ${
                        item.status === 'Complete' ? 'bg-green-100 text-green-800' :
                        item.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {item.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Portfolio Management System</h1>
        <p className="text-gray-600 mb-6">Organization, Lifecycle, Meetings & Deliverables</p>

        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6 border-b">
          {[
            { id: 'org', label: 'Organization Chart' },
            { id: 'lifecycle', label: 'Portfolio Lifecycle (17 Steps)' },
            { id: 'meetings', label: 'Meetings & Calendar' },
            { id: 'deliverables', label: 'Goals & Deliverables' },
          ].map((tab) => (
            <button
              key={tab.id}
              className={`px-4 py-3 font-medium transition-all ${
                activeTab === tab.id
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-blue-600'
              }`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'org' && renderOrgChart()}
        {activeTab === 'lifecycle' && renderLifecycle()}
        {activeTab === 'meetings' && renderMeetings()}
        {activeTab === 'deliverables' && renderDeliverables()}
      </div>
    </div>
  );
};

export default OrganizationChart;
