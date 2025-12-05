import { useEffect, useState } from 'react';
import axios from 'axios';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Dashboard } from './components/Dashboard';
import { AllNews } from './components/AllNews';
import { StockDetails } from './components/StockDetails';
import type { MarketStatus, WatchlistItem, NewsItem, SectorItem, GainerItem } from './types';

// API Base URL
const API_URL = 'http://localhost:8000/api';

function DashboardWrapper() {
  const [marketStatus, setMarketStatus] = useState<MarketStatus[]>([]);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [sectors, setSectors] = useState<SectorItem[]>([]);
  const [gainers, setGainers] = useState<GainerItem[]>([]);
  const [aiSummary, setAiSummary] = useState<string>('');
  const [loading, setLoading] = useState(true);

  const fetchMarketData = async () => {
    try {
      const [
        marketRes,
        watchlistRes,
        newsRes,
        sectorsRes,
        gainersRes
      ] = await Promise.all([
        axios.get(`${API_URL}/market-status`),
        axios.get(`${API_URL}/watchlist`),
        axios.get(`${API_URL}/news?limit=3`),
        axios.get(`${API_URL}/sectors`),
        axios.get(`${API_URL}/gainers`)
      ]);

      setMarketStatus(marketRes.data);
      setWatchlist(watchlistRes.data);
      setNews(newsRes.data);
      setSectors(sectorsRes.data);
      setGainers(gainersRes.data);
    } catch (error) {
      console.error('Error fetching market data:', error);
    } finally {
      setLoading(false);
    }
  };

  const refreshWatchlist = async () => {
    try {
      const res = await axios.get(`${API_URL}/watchlist`);
      setWatchlist(res.data);
    } catch (error) {
      console.error('Error refreshing watchlist:', error);
    }
  };

  useEffect(() => {
    const fetchAISummary = async () => {
      try {
        const res = await axios.get(`${API_URL}/ai-summary`);
        setAiSummary(res.data.summary);
      } catch (error) {
        console.error('Error fetching AI summary:', error);
      }
    };

    // Initial fetch
    fetchMarketData();
    fetchAISummary();

    // Poll market data every 5 seconds
    const intervalId = setInterval(fetchMarketData, 5000);

    return () => clearInterval(intervalId);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center text-text">
        <div className="animate-pulse">Loading market data...</div>
      </div>
    );
  }

  return (
    <Dashboard
      marketStatus={marketStatus}
      watchlist={watchlist}
      news={news}
      sectors={sectors}
      gainers={gainers}
      aiSummary={aiSummary}
      onRefreshWatchlist={refreshWatchlist}
    />
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardWrapper />} />
        <Route path="/news" element={<AllNews />} />
        <Route path="/stock/:symbol" element={<StockDetails />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
