import React from 'react';
import type { MarketStatus } from '../types';
import { LineChart, Line, ResponsiveContainer } from 'recharts';
import { ArrowUp, ArrowDown } from 'lucide-react';
import clsx from 'clsx';

interface Props {
    data: MarketStatus[];
}

// Mock sparkline data generator since we don't have real historical data in the simple API yet
const generateSparklineData = (trend: 'up' | 'down') => {
    const data = [];
    let val = 50;
    for (let i = 0; i < 20; i++) {
        val += (Math.random() - 0.5) * 10 + (trend === 'up' ? 1 : -1);
        data.push({ value: val });
    }
    return data;
};

export const MarketOverview: React.FC<Props> = ({ data }) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {data.map((item) => {
                const isPositive = item.percentChange >= 0;
                const sparklineData = generateSparklineData(isPositive ? 'up' : 'down');

                return (
                    <div key={item.symbol} className="bg-surface rounded-xl p-4 border border-border">
                        <div className="flex justify-between items-start mb-2">
                            <div>
                                <h3 className="text-text font-medium">{item.name}</h3>
                                <span className="text-muted text-xs">{item.symbol}</span>
                            </div>
                            <div className={clsx("flex flex-col items-end text-sm", isPositive ? "text-success" : "text-danger")}>
                                <div className="flex items-center">
                                    {isPositive ? <ArrowUp size={14} /> : <ArrowDown size={14} />}
                                    <span className="ml-1">{Math.abs(item.percentChange).toFixed(2)}%</span>
                                </div>
                                <span>{item.change > 0 ? '+' : ''}{item.change.toFixed(2)}</span>
                            </div>
                        </div>

                        <div className="mt-4">
                            <ResponsiveContainer width="100%" height={64}>
                                <LineChart data={sparklineData}>
                                    <Line
                                        type="monotone"
                                        dataKey="value"
                                        stroke={isPositive ? "#10b981" : "#ef4444"}
                                        strokeWidth={2}
                                        dot={false}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>

                        <div className="mt-2 text-xl font-semibold text-text">
                            {item.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </div>
                    </div>
                );
            })}
        </div>
    );
};
