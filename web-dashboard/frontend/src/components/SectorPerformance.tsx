import React from 'react';
import type { SectorItem } from '../types';
import clsx from 'clsx';

interface Props {
    data: SectorItem[];
}

export const SectorPerformance: React.FC<Props> = ({ data }) => {
    return (
        <div className="bg-surface rounded-xl p-6 border border-border">
            <h2 className="text-lg font-semibold text-text mb-6">Equity Sectors</h2>

            <div className="space-y-4">
                {data.map((item) => {
                    const isPositive = item.change >= 0;
                    return (
                        <div key={item.name} className="flex items-center justify-between">
                            <span className="text-sm text-text">{item.name}</span>
                            <div className="flex items-center gap-4">
                                <span className="text-sm text-muted">${item.value.toFixed(2)}</span>
                                <span className={clsx("text-xs px-2 py-1 rounded font-medium min-w-[60px] text-center",
                                    isPositive ? "bg-success/10 text-success" : "bg-danger/10 text-danger"
                                )}>
                                    {isPositive ? '↗' : '↘'} {Math.abs(item.change).toFixed(2)}%
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
