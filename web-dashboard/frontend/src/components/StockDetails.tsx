import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface CalculationResult {
    symbol: string;
    initial_date: string;
    initial_price: number;
    current_price: number;
    current_value: number;
    roi: number;
    error?: string;
}

interface HistoryData {
    date: string;
    price: number;
}

export const StockDetails: React.FC = () => {
    const { symbol } = useParams<{ symbol: string }>();
    const [amount, setAmount] = useState<string>('1000');
    const [date, setDate] = useState<string>('');
    const [result, setResult] = useState<CalculationResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [history, setHistory] = useState<HistoryData[]>([]);
    const [historyLoading, setHistoryLoading] = useState(true);
    const [period, setPeriod] = useState<string>('1y');

    const periods = [
        { label: '1D', value: '1d' },
        { label: '1W', value: '5d' }, // yfinance uses 5d for 1 week usually
        { label: '1M', value: '1mo' },
        { label: 'YTD', value: 'ytd' },
        { label: '1Y', value: '1y' },
        { label: '5Y', value: '5y' },
        { label: '10Y', value: '10y' },
    ];

    // Set default date to 1 year ago
    useEffect(() => {
        const d = new Date();
        d.setFullYear(d.getFullYear() - 1);
        setDate(d.toISOString().split('T')[0]);
    }, []);

    // Fetch history data
    useEffect(() => {
        const fetchHistory = async () => {
            if (!symbol) return;
            setHistoryLoading(true);
            try {
                const response = await axios.get(`http://localhost:8000/api/stock/${symbol}/history`, {
                    params: { period }
                });
                setHistory(response.data);
            } catch (err) {
                console.error('Failed to fetch history:', err);
            } finally {
                setHistoryLoading(false);
            }
        };
        fetchHistory();
    }, [symbol, period]);

    const handleCalculate = async () => {
        if (!amount || !date || !symbol) return;

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await axios.get(`http://localhost:8000/api/stock/${symbol}/calculate`, {
                params: {
                    date: date,
                    amount: parseFloat(amount)
                }
            });

            if (response.data.error) {
                setError(response.data.error);
            } else {
                setResult(response.data);
            }
        } catch (err) {
            console.error(err);
            setError('Failed to calculate investment. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-background text-text p-6 md:p-8">
            <div className="max-w-4xl mx-auto">
                <Link to="/" className="text-blue-500 hover:text-blue-400 mb-6 inline-block">&larr; Back to Dashboard</Link>

                <div className="bg-card rounded-xl p-6 border border-border mb-8">
                    <h1 className="text-3xl font-bold mb-2">{symbol}</h1>
                    <p className="text-muted">Stock Details & Investment Calculator</p>
                </div>

                {/* Price Graph */}
                <div className="bg-card rounded-xl p-6 border border-border mb-8 h-[500px] flex flex-col">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
                        <h2 className="text-xl font-semibold">
                            Price History ({periods.find(p => p.value === period)?.label || '1 Year'})
                        </h2>
                        <div className="flex bg-background rounded-lg p-1 border border-border overflow-x-auto max-w-full">
                            {periods.map((p) => (
                                <button
                                    key={p.value}
                                    onClick={() => setPeriod(p.value)}
                                    className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors whitespace-nowrap ${period === p.value
                                        ? 'bg-blue-600 text-white'
                                        : 'text-muted hover:text-text hover:bg-gray-800'
                                        }`}
                                >
                                    {p.label}
                                </button>
                            ))}
                        </div>
                    </div>
                    <div className="flex-1 min-h-0">
                        {historyLoading ? (
                            <div className="h-full flex items-center justify-center text-muted">Loading chart...</div>
                        ) : (
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={history}>
                                    <XAxis
                                        dataKey="date"
                                        stroke="#6b7280"
                                        tickFormatter={(str) => {
                                            const d = new Date(str);
                                            return `${d.getMonth() + 1}/${d.getDate()}`;
                                        }}
                                        minTickGap={30}
                                    />
                                    <YAxis
                                        stroke="#6b7280"
                                        domain={['auto', 'auto']}
                                        tickFormatter={(val) => `$${val}`}
                                        width={60}
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '0.5rem' }}
                                        itemStyle={{ color: '#fff' }}
                                        labelStyle={{ color: '#9ca3af' }}
                                        formatter={(value: number) => [`$${value}`, 'Price']}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="price"
                                        stroke="#22c55e"
                                        strokeWidth={2}
                                        dot={false}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        )}
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Calculator Input */}
                    <div className="bg-card rounded-xl p-6 border border-border">
                        <h2 className="text-xl font-semibold mb-6">Investment Time Machine</h2>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm text-muted mb-2">Investment Amount ($)</label>
                                <input
                                    type="number"
                                    value={amount}
                                    onChange={(e) => setAmount(e.target.value)}
                                    className="w-full bg-background border border-border rounded-lg p-3 text-text focus:outline-none focus:border-blue-500 transition-colors"
                                />
                            </div>

                            <div>
                                <label className="block text-sm text-muted mb-2">Date of Investment</label>
                                <input
                                    type="date"
                                    value={date}
                                    onChange={(e) => setDate(e.target.value)}
                                    max={new Date().toISOString().split('T')[0]}
                                    className="w-full bg-background border border-border rounded-lg p-3 text-text focus:outline-none focus:border-blue-500 transition-colors"
                                />
                            </div>

                            <button
                                onClick={handleCalculate}
                                disabled={loading}
                                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Calculating...' : 'Calculate Returns'}
                            </button>
                        </div>
                    </div>

                    {/* Results */}
                    <div className="bg-card rounded-xl p-6 border border-border flex flex-col justify-center">
                        {error && (
                            <div className="text-red-400 text-center p-4 bg-red-400/10 rounded-lg">
                                {error}
                            </div>
                        )}

                        {result && (
                            <div className="space-y-6 animate-in fade-in duration-500">
                                <div className="text-center">
                                    <p className="text-muted mb-1">Current Value</p>
                                    <div className={`text-4xl font-bold ${result.roi >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                        ${result.current_value.toLocaleString()}
                                    </div>
                                    <div className={`text-sm font-medium mt-2 ${result.roi >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                        {result.roi >= 0 ? '+' : ''}{result.roi}% Return
                                    </div>
                                </div>

                                <div className="border-t border-border pt-6 space-y-3 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-muted">Initial Investment</span>
                                        <span>${parseFloat(amount).toLocaleString()}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-muted">Date</span>
                                        <span>{result.initial_date}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-muted">Price Then</span>
                                        <span>${result.initial_price}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-muted">Price Now</span>
                                        <span>${result.current_price}</span>
                                    </div>
                                </div>
                            </div>
                        )}

                        {!result && !error && !loading && (
                            <div className="text-center text-muted">
                                <p>Enter an amount and date to see how your investment would have performed.</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};
