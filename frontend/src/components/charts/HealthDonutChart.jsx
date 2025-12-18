import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { PieChart as PieIcon } from 'lucide-react';

const COLORS = { ERROR: '#EF4444', WARNING: '#F59E0B', INFO: '#3B82F6' };

const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{ backgroundColor: '#131313', border: '1px solid var(--border-color)', padding: '10px', borderRadius: '8px', fontSize: '12px' }}>
          {payload.map((p, i) => (<p key={i} style={{ color: p.fill }}>{`${p.name}: ${p.value}`}</p>))}
        </div>
      );
    }
    return null;
};

const HealthDonutChart = ({ data }) => (
    <div className="chartContainer">
        <h3 className="chartTitle"><PieIcon size={14} /> Overall Log Health</h3>
        <ResponsiveContainer width="100%" height="100%">
            <PieChart>
                <Pie 
                    data={data} 
                    cx="50%" 
                    cy="50%" 
                    innerRadius={50} 
                    outerRadius={70} 
                    fill="#8884d8" 
                    paddingAngle={5} 
                    dataKey="value"
                    nameKey="name"
                >
                    {data.map((entry) => <Cell key={`cell-${entry.name}`} fill={COLORS[entry.name]} />)}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend iconSize={10} wrapperStyle={{fontSize: "12px"}}/>
            </PieChart>
        </ResponsiveContainer>
    </div>
);

export default HealthDonutChart;
