import React from 'react';
import { MarketOverview } from './MarketOverview';
import { Watchlist } from './Watchlist';
import { NewsFeed } from './NewsFeed';
import { SectorPerformance } from './SectorPerformance';
import { GainersList } from './GainersList';
import { AISummary } from './AISummary';
import type { MarketStatus, WatchlistItem, NewsItem, SectorItem, GainerItem } from '../types';

interface Props {
    marketStatus: MarketStatus[];
    watchlist: WatchlistItem[];
    news: NewsItem[];
    sectors: SectorItem[];
    gainers: GainerItem[];
    aiSummary: string;
}

export const Dashboard: React.FC<Props> = ({
    marketStatus,
    watchlist,
    news,
    sectors,
    gainers,
    aiSummary
}) => {
    return (
        <div className="min-h-screen bg-background text-text p-6 md:p-8">
            <header className="flex items-center gap-4 mb-8">
                <div className="flex items-center gap-2">
                    <div className="w-6 h-4 bg-blue-600 rounded-sm relative overflow-hidden">
                        <div className="absolute top-0 left-0 w-2 h-2 bg-white/20"></div>
                    </div>
                    <span className="font-semibold text-blue-500">US Markets</span>
                </div>
                <nav className="flex gap-4 text-sm text-muted">
                    <a href="#" className="hover:text-text transition-colors">Crypto</a>
                    <a href="#" className="hover:text-text transition-colors">Earnings</a>
                    <a href="#" className="hover:text-text transition-colors">Screener</a>
                    <a href="#" className="hover:text-text transition-colors">Politicians</a>
                    <a href="#" className="hover:text-text transition-colors">Watchlist</a>
                </nav>
            </header>

            <AISummary summary={aiSummary} loading={!aiSummary && marketStatus.length === 0} />

            <MarketOverview data={marketStatus} />

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Left Column - News */}
                <div className="lg:col-span-8">
                    <NewsFeed data={news} />
                </div>

                {/* Right Column - Watchlist & Sectors */}
                <div className="lg:col-span-4 space-y-8">
                    <Watchlist data={watchlist} />
                    <GainersList data={gainers} />
                    <SectorPerformance data={sectors} />
                </div>
            </div>
        </div>
    );
};
