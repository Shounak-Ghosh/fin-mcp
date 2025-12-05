import React from 'react';
import { Link } from 'react-router-dom';
import type { WatchlistItem } from '../types';
import { ArrowUp, ArrowDown } from 'lucide-react';
import clsx from 'clsx';

interface Props {
    data: WatchlistItem[];
}

export const Watchlist: React.FC<Props> = ({ data }) => {
    return (
        <div className="bg-surface rounded-xl p-4 border border-border">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-text">Watchlist</h2>
                <button className="text-muted hover:text-text transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                </button>
            </div>

            <div className="space-y-3">
                {data.map((item) => {
                    const isPositive = item.percentChange >= 0;
                    return (
                        <Link to={`/stock/${item.symbol}`} key={item.symbol} className="block">
                            <div className="flex justify-between items-center group cursor-pointer hover:bg-white/5 p-2 rounded-lg transition-colors -mx-2">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center text-xs font-bold text-text">
                                        {item.symbol[0]}
                                    </div>
                                    <div>
                                        <div className="font-medium text-text">{item.name}</div>
                                        <div className="text-xs text-muted">{item.symbol}</div>
                                    </div>
                                </div>

                                <div className="text-right">
                                    <div className="font-medium text-text">${item.price.toFixed(2)}</div>
                                    <div className={clsx("text-xs flex items-center justify-end gap-1", isPositive ? "text-success" : "text-danger")}>
                                        {isPositive ? <ArrowUp size={12} /> : <ArrowDown size={12} />}
                                        {Math.abs(item.percentChange).toFixed(2)}%
                                    </div>
                                </div>
                            </div>
                        </Link>
                    );
                })}
            </div>
        </div>
    );
};
