import React from 'react';
import { FileText } from 'lucide-react';

const SummaryView = ({ summaryReport }) => {
    if (!summaryReport) {
        return (
            <div className="flex justify-center items-center h-full text-gray-500">
                <p>No summary report available. Please upload and analyze a log file.</p>
            </div>
        );
    }

    return (
        <div className="summaryViewContainer">
            <h2 className="summaryTitle">
                <FileText size={24} /> Log Summary Report
            </h2>

            {summaryReport.top_incidents && summaryReport.top_incidents.length > 0 && (
                <div className="mb-8">
                    <h3 className="summarySectionHeading">Top Incidents</h3>
                    <ul className="list-disc pl-5 space-y-3">
                        {summaryReport.top_incidents.map((incident, index) => (
                            <li key={index} className="summaryListItem">
                                <p className="font-medium text-primary-text">{incident.title}</p>
                                {incident.timestamp && <p className="text-sm text-secondary-text">Timestamp: {incident.timestamp}</p>}
                                {incident.severity && <p className="text-sm text-secondary-text">Severity: <span className={`font-bold ${incident.severity === 'ERROR' ? 'text-error-color' : 'text-yellow-500'}`}>{incident.severity}</span></p>}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {summaryReport.recommended_actions && summaryReport.recommended_actions.length > 0 && (
                <div className="mb-8">
                    <h3 className="summarySectionHeading">Recommended Actions</h3>
                    <ul className="list-decimal pl-5 space-y-3">
                        {summaryReport.recommended_actions.map((action, index) => (
                            <li key={index} className="summaryListItem">
                                {action}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {!summaryReport.top_incidents?.length && !summaryReport.recommended_actions?.length && (
                <div className="summaryPlaceholder">
                    <p>No incidents or recommended actions found in the summary report.</p>
                </div>
            )}
        </div>
    );
};

export default SummaryView;
