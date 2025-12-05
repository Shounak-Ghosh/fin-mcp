export interface MarketStatus {
    symbol: string;
    name: string;
    price: number;
    change: number;
    percentChange: number;
    history: { time: string; value: number }[];
}

export interface WatchlistItem {
    symbol: string;
    name: string;
    price: number;
    change: number;
    percentChange: number;
}

export interface NewsItem {
    title: string;
    summary: string;
    source: string;
    time: string;
    url?: string;
}

export interface SectorItem {
    name: string;
    value: number;
    change: number;
}

export interface GainerItem {
    symbol: string;
    name: string;
    price: number;
    change: number;
}

export interface AISummaryData {
    summary: string;
}
