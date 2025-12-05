import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import type { WatchlistItem } from '../types';
import { ArrowUp, ArrowDown, Plus, Trash2 } from 'lucide-react';
import clsx from 'clsx';
import { StockSearchModal } from './StockSearchModal';
import axios from 'axios';

interface Props {
    data: WatchlistItem[];
    onRefresh: () => void;
}

export const Watchlist: React.FC<Props> = ({ data, onRefresh }) => {
    const [isSearchOpen, setIsSearchOpen] = useState(false);

    const handleAddStock = async (symbol: string) => {
        try {
            await axios.post('http://localhost:8000/api/watchlist', { symbol });
            onRefresh();
            setIsSearchOpen(false);
        } catch (error) {
            console.error('Error adding stock:', error);
        }
    };

    const handleDeleteStock = async (e: React.MouseEvent, symbol: string) => {
        e.preventDefault(); // Prevent navigation
        e.stopPropagation(); // Prevent bubbling to Link
        if (!confirm(`Remove ${symbol} from watchlist?`)) return;

        try {
            await axios.delete(`http://localhost:8000/api/watchlist/${symbol}`);
            onRefresh();
        } catch (error) {
            console.error('Error removing stock:', error);
        }
    };

    return (
        <>
            <div className="bg-surface rounded-xl p-4 border border-border">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-lg font-semibold text-text">Watchlist</h2>
                    <button
                        onClick={() => setIsSearchOpen(true)}
                        className="text-muted hover:text-text transition-colors p-1 hover:bg-white/5 rounded"
                    >
                        <Plus size={20} />
                    </button>
                </div>

                <div className="space-y-3">
                    {data.map((item) => {
                        const isPositive = item.percentChange >= 0;
                        return (
                            <Link to={`/stock/${item.symbol}`} key={item.symbol} className="block group relative">
                                <div className="flex justify-between items-center cursor-pointer hover:bg-white/5 p-2 rounded-lg transition-colors -mx-2 pr-12">
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
                                <button
                                    onClick={(e) => handleDeleteStock(e, item.symbol)}
                                    className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-muted hover:text-danger opacity-0 group-hover:opacity-100 transition-opacity"
                                    title="Remove from watchlist"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </Link>
                        );
                    })}
                </div>
            </div>

            <StockSearchModal
                isOpen={isSearchOpen}
                onClose={() => setIsSearchOpen(false)}
                onAdd={handleAddStock}
            />
        </>
    );
};
