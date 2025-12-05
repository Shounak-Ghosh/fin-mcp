import React, { useState, useEffect } from 'react';
import { Search, X, Plus, Loader2 } from 'lucide-react';

interface SearchResult {
    symbol: string;
    name: string;
    type: string;
    exchange: string;
}

interface Props {
    isOpen: boolean;
    onClose: () => void;
    onAdd: (symbol: string) => Promise<void>;
}

export const StockSearchModal: React.FC<Props> = ({ isOpen, onClose, onAdd }) => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isAdding, setIsAdding] = useState<string | null>(null);

    useEffect(() => {
        const searchStocks = async () => {
            if (query.length < 2) {
                setResults([]);
                return;
            }

            setIsLoading(true);
            try {
                const response = await fetch(`http://localhost:8000/api/search?q=${encodeURIComponent(query)}`);
                if (response.ok) {
                    const data = await response.json();
                    setResults(data);
                }
            } catch (error) {
                console.error('Error searching stocks:', error);
            } finally {
                setIsLoading(false);
            }
        };

        const timeoutId = setTimeout(searchStocks, 500);
        return () => clearTimeout(timeoutId);
    }, [query]);

    const handleAdd = async (symbol: string) => {
        setIsAdding(symbol);
        try {
            await onAdd(symbol);
            // Optional: Close modal or show success state
            // onClose(); 
        } catch (error) {
            console.error('Error adding stock:', error);
        } finally {
            setIsAdding(null);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-surface border border-border rounded-xl w-full max-w-md shadow-2xl flex flex-col max-h-[80vh]">
                <div className="p-4 border-b border-border flex items-center gap-3">
                    <Search className="text-muted" size={20} />
                    <input
                        type="text"
                        placeholder="Search for a stock..."
                        className="bg-transparent border-none outline-none flex-1 text-text placeholder:text-muted"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        autoFocus
                    />
                    <button onClick={onClose} className="text-muted hover:text-text transition-colors">
                        <X size={20} />
                    </button>
                </div>

                <div className="overflow-y-auto flex-1 p-2">
                    {isLoading ? (
                        <div className="flex justify-center p-8 text-muted">
                            <Loader2 className="animate-spin" />
                        </div>
                    ) : results.length > 0 ? (
                        <div className="space-y-1">
                            {results.map((result) => (
                                <div key={result.symbol} className="flex items-center justify-between p-3 hover:bg-white/5 rounded-lg group">
                                    <div>
                                        <div className="font-medium text-text">{result.symbol}</div>
                                        <div className="text-sm text-muted">{result.name}</div>
                                        <div className="text-xs text-muted/50">{result.exchange} • {result.type}</div>
                                    </div>
                                    <button
                                        onClick={() => handleAdd(result.symbol)}
                                        disabled={isAdding === result.symbol}
                                        className="p-2 rounded-lg bg-primary/10 text-primary hover:bg-primary/20 transition-colors disabled:opacity-50"
                                    >
                                        {isAdding === result.symbol ? (
                                            <Loader2 size={18} className="animate-spin" />
                                        ) : (
                                            <Plus size={18} />
                                        )}
                                    </button>
                                </div>
                            ))}
                        </div>
                    ) : query.length >= 2 ? (
                        <div className="text-center p-8 text-muted">
                            No results found for "{query}"
                        </div>
                    ) : (
                        <div className="text-center p-8 text-muted">
                            Type to search for stocks, ETFs, or indices
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
