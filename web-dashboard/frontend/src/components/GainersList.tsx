import React from 'react';
import { Link } from 'react-router-dom';
import type { GainerItem } from '../types';


interface Props {
    data: GainerItem[];
}

export const GainersList: React.FC<Props> = ({ data }) => {
    return (
        <div className="bg-surface rounded-xl p-6 border border-border mt-6">
            <div className="flex gap-4 mb-6 border-b border-border pb-2">
                <button className="text-text font-semibold border-b-2 border-primary pb-2 -mb-2.5">Gainers</button>
                <button className="text-muted hover:text-text transition-colors">Losers</button>
                <button className="text-muted hover:text-text transition-colors">Active</button>
            </div>

            <div className="space-y-4">
                {data.map((item) => (
                    <Link to={`/stock/${item.symbol}`} key={item.symbol} className="block">
                        <div className="flex justify-between items-center hover:bg-white/5 p-2 rounded-lg transition-colors -mx-2">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded bg-white/10 flex items-center justify-center text-[10px] font-bold text-text">
                                    {item.symbol.substring(0, 2)}
                                </div>
                                <div>
                                    <div className="font-medium text-sm text-text truncate max-w-[120px]">{item.name}</div>
                                    <div className="text-xs text-muted">{item.symbol}</div>
                                </div>
                            </div>

                            <div className="text-right">
                                <div className="text-sm font-medium text-text">${item.price.toFixed(2)}</div>
                                <div className="text-xs text-success">+{item.change.toFixed(2)}%</div>
                            </div>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    );
};
