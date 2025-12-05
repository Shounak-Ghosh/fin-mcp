import React from 'react';
import type { MarketStatus } from '../types';
import { LineChart, Line, ResponsiveContainer, ReferenceArea, ReferenceLine, Tooltip, YAxis } from 'recharts';
import { ArrowUp, ArrowDown } from 'lucide-react';
import clsx from 'clsx';

interface Props {
    data: MarketStatus[];
}

export const MarketOverview: React.FC<Props> = ({ data }) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {data.map((item) => {
                const isPositive = item.percentChange >= 0;
                // Use real history data if available, otherwise empty array
                const sparklineData = item.history || [];

                // Process data for the chart
                const processedData: { time: string; value: number; openValue: number | null; closedValue: number | null }[] = [];
                const ranges: { start: number; end: number }[] = [];
                const daySeparators: number[] = [];
                let currentStart: number | null = null;
                let wasMarketOpen = false;

                // 9:30 AM = 570 min, 4:00 PM = 960 min
                const MARKET_OPEN_MIN = 570;
                const MARKET_CLOSE_MIN = 960;

                let lastDateStr = '';

                sparklineData.forEach((point, index) => {
                    if (!point.time) return;
                    const date = new Date(point.time);

                    // 1. Day Separators
                    const dateStr = date.toLocaleDateString('en-US', { timeZone: 'America/New_York' });
                    if (lastDateStr && dateStr !== lastDateStr) {
                        daySeparators.push(index);
                    }
                    lastDateStr = dateStr;

                    // 2. Market Open Status
                    const etTime = new Intl.DateTimeFormat('en-US', {
                        timeZone: 'America/New_York',
                        hour: 'numeric',
                        minute: 'numeric',
                        hour12: false
                    }).formatToParts(date);

                    const hour = parseInt(etTime.find(p => p.type === 'hour')?.value || '0');
                    const minute = parseInt(etTime.find(p => p.type === 'minute')?.value || '0');
                    const dayName = date.toLocaleDateString('en-US', { timeZone: 'America/New_York', weekday: 'short' });
                    const isWeekend = dayName === 'Sat' || dayName === 'Sun';

                    const totalMinutes = hour * 60 + minute;
                    const isMarketOpenTime = totalMinutes >= MARKET_OPEN_MIN && totalMinutes < MARKET_CLOSE_MIN;
                    const isMarketOpen = !isWeekend && isMarketOpenTime;

                    // Reference Areas for Inactive Hours
                    // Note: Logic in previous version highlighted NON-open times with shading?
                    // Previous logic:
                    // if (isMarketOpen && currentStart === null) currentStart = index (Wait? Looking at previous code...)
                    // Previous code:
                    // if (isMarketOpen && currentStart === null) { currentStart = index }
                    // else if (!isMarketOpen && currentStart !== null) { ranges.push(...) }
                    // Wait, if start is when market is OPEN, then ranges capture OPEN times.
                    // And fill was #10b981 (green) or #3b82f6 (blue) with opacity 0.15.
                    // So it was highlighting ACTIVE hours.
                    // The prompt "shading for market open hours" in previous turn confirms this.
                    // So I will keep this logic (highlighting active hours).
                    if (isMarketOpen && currentStart === null) {
                        currentStart = index;
                    } else if (!isMarketOpen && currentStart !== null) {
                        ranges.push({ start: currentStart, end: index });
                        currentStart = null;
                    }

                    // Line Segmentation
                    let openVal: number | null = null;
                    let closedVal: number | null = null;

                    if (isMarketOpen) {
                        openVal = point.value;
                        // Transition from Closed to Open: Close the gap
                        if (index > 0 && !wasMarketOpen) {
                            closedVal = point.value;
                        }
                    } else {
                        closedVal = point.value;
                        // Transition from Open to Closed: Close the gap
                        if (index > 0 && wasMarketOpen) {
                            openVal = point.value;
                        }
                    }

                    processedData.push({
                        time: point.time,
                        value: point.value,
                        openValue: openVal,
                        closedValue: closedVal
                    });

                    wasMarketOpen = isMarketOpen;
                });

                // Handle the final segment for ranges
                if (currentStart !== null) {
                    ranges.push({ start: currentStart, end: sparklineData.length - 1 });
                }

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
                                <LineChart data={processedData}>
                                    <defs>
                                        <linearGradient id={`gradient-${item.symbol}`} x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor={isPositive ? "#10b981" : "#ef4444"} stopOpacity={0.1} />
                                            <stop offset="95%" stopColor={isPositive ? "#10b981" : "#ef4444"} stopOpacity={0} />
                                        </linearGradient>
                                    </defs>

                                    {ranges.map((range, i) => (
                                        <ReferenceArea
                                            key={`range-${i}`}
                                            x1={range.start}
                                            x2={range.end}
                                            fill={isPositive ? "#10b981" : "#3b82f6"}
                                            fillOpacity={0.15}
                                            strokeOpacity={0}
                                        />
                                    ))}

                                    {daySeparators.map((val, i) => (
                                        <ReferenceLine
                                            key={`sep-${i}`}
                                            x={val}
                                            stroke="#6b7280"
                                            strokeOpacity={0.5}
                                            strokeDasharray="3 3"
                                            ifOverflow="visible"
                                        />
                                    ))}

                                    <Line
                                        type="monotone"
                                        dataKey="openValue"
                                        stroke={isPositive ? "#10b981" : "#ef4444"}
                                        strokeWidth={1.5}
                                        dot={false}
                                        isAnimationActive={false}
                                        connectNulls={false}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="closedValue"
                                        stroke={isPositive ? "#10b981" : "#ef4444"}
                                        strokeWidth={1.5}
                                        strokeDasharray="3 3"
                                        dot={false}
                                        isAnimationActive={false}
                                        connectNulls={false}
                                    />

                                    <YAxis domain={['dataMin', 'dataMax']} hide />
                                    <Tooltip
                                        content={({ active, payload }) => {
                                            if (active && payload && payload.length) {
                                                const data = payload[0].payload;
                                                const date = new Date(data.time);
                                                const timeStr = date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
                                                return (
                                                    <div className="bg-surface border border-border p-2 rounded text-xs shadow-lg">
                                                        <p className="text-muted">{timeStr}</p>
                                                        <p className="font-bold text-text">${Number(data.value).toFixed(2)}</p>
                                                    </div>
                                                );
                                            }
                                            return null;
                                        }}
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
