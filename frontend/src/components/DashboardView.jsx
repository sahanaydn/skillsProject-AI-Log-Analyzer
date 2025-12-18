import React from 'react';
import TimelineChart from './charts/TimelineChart';
import ErrorTypeChart from './charts/ErrorTypeChart';
import HealthDonutChart from './charts/HealthDonutChart';
import { Cpu } from 'lucide-react';

const DashboardView = ({ analysisResult }) => {
    if (!analysisResult) {
        return (
            <div className="placeholder-view">
                <Cpu size={48} />
                <h3>Dashboard Awaiting Data</h3>
                <p>Upload a log file to generate the dashboard.</p>
            </div>
        );
    }

    const healthData = [
        { name: 'ERROR', value: analysisResult.severity_breakdown?.ERROR || 0 },
        { name: 'WARNING', value: analysisResult.severity_breakdown?.WARNING || 0 },
        { name: 'INFO', value: analysisResult.severity_breakdown?.INFO || 0 },
    ].filter(d => d.value > 0);

    const errorTypes = analysisResult.error_types || [];
    const timeSeries = analysisResult.time_series || [];

    return (
        <div className="dashboardContainer">
            <div className="dashboardGrid">
                <div className="chartContainer chartFullWidth">
                    <TimelineChart data={timeSeries} />
                </div>
                <div className="chartContainer">
                    <ErrorTypeChart data={errorTypes} />
                </div>
                <div className="chartContainer">
                    <HealthDonutChart data={healthData} />
                </div>
            </div>
        </div>
    );
};

export default DashboardView;
