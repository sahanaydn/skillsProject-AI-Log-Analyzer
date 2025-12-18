import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Clock } from 'lucide-react';

const COLORS = { ERROR: '#EF4444', WARNING: '#F59E0B' };

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{ backgroundColor: '#131313', border: '1px solid var(--border-color)', padding: '10px', borderRadius: '8px', fontSize: '12px' }}>
          <p style={{color: 'var(--secondary-text)', marginBottom: '5px'}}>{label}</p>
          {payload.map((p, i) => (<p key={i} style={{ color: p.color }}>{`${p.name}: ${p.value}`}</p>))}
        </div>
      );
    }
    return null;
};

const TimelineChart = ({ data }) => (
    <div className="chartContainer full-width">
        <h3 className="chartTitle"><Clock size={14} /> Event Timeline</h3>
        <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 0 }}>
                <defs>
                    <linearGradient id="colorError" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={COLORS.ERROR} stopOpacity={0.8}/>
                        <stop offset="95%" stopColor={COLORS.ERROR} stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorWarning" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={COLORS.WARNING} stopOpacity={0.8}/>
                        <stop offset="95%" stopColor={COLORS.WARNING} stopOpacity={0}/>
                    </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                <XAxis dataKey="time" stroke="var(--secondary-text)" tick={{ fontSize: 12 }} />
                <YAxis stroke="var(--secondary-text)" tick={{ fontSize: 12 }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend iconSize={10} wrapperStyle={{fontSize: "12px"}}/>
                <Area type="monotone" dataKey="errors" name="Errors" stroke={COLORS.ERROR} fillOpacity={1} fill="url(#colorError)" />
                <Area type="monotone" dataKey="warnings" name="Warnings" stroke={COLORS.WARNING} fillOpacity={1} fill="url(#colorWarning)" />
            </AreaChart>
        </ResponsiveContainer>
    </div>
);

export default TimelineChart;
