import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { BarChart2 } from 'lucide-react';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#EF4444'];

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{ backgroundColor: '#131313', border: '1px solid var(--border-color)', padding: '10px', borderRadius: '8px', fontSize: '12px' }}>
          <p style={{color: 'var(--secondary-text)', marginBottom: '5px'}}>{label}</p>
          {payload.map((p, i) => (<p key={i} style={{ color: p.fill }}>{`${p.name}: ${p.value}`}</p>))}
        </div>
      );
    }
    return null;
};

const ErrorTypeChart = ({ data }) => (
    <div className="chartContainer">
        <h3 className="chartTitle"><BarChart2 size={14} /> Top Error Types</h3>
        <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 30, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                <XAxis type="number" stroke="var(--secondary-text)" tick={{ fontSize: 12 }} />
                <YAxis type="category" dataKey="name" stroke="var(--secondary-text)" tick={{ fontSize: 12 }} interval={0} />
                <Tooltip cursor={{fill: '#ffffff10'}} content={<CustomTooltip />} />
                <Bar dataKey="count" name="Count" fill="#8884d8" radius={[0, 4, 4, 0]}>
                    {data.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                </Bar>
            </BarChart>
        </ResponsiveContainer>
    </div>
);

export default ErrorTypeChart;
