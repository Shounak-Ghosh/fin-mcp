import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import type { NewsItem } from '../types';

const API_URL = 'http://localhost:8000/api';

export const AllNews: React.FC = () => {
    const [news, setNews] = useState<NewsItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchNews = async () => {
            try {
                const response = await axios.get(`${API_URL}/news`);
                setNews(response.data);
            } catch (error) {
                console.error('Error fetching news:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchNews();
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center text-text">
                <div className="animate-pulse">Loading news...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background text-text p-6 md:p-8">
            <div className="max-w-4xl mx-auto">
                <header className="mb-8">
                    <Link to="/" className="text-blue-500 hover:text-blue-400 mb-4 inline-block">
                        &larr; Back to Dashboard
                    </Link>
                    <h1 className="text-2xl font-bold">All Market News</h1>
                </header>

                <div className="bg-surface rounded-xl p-6 border border-border">
                    <div className="space-y-6">
                        {news.map((item, index) => (
                            <a
                                key={index}
                                href={item.url || '#'}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block group cursor-pointer"
                            >
                                <h3 className="text-lg font-medium mb-2 group-hover:text-primary transition-colors">{item.title}</h3>
                                <p className="text-muted text-base mb-2">{item.summary}</p>
                                <div className="flex items-center gap-2 text-sm text-muted/60">
                                    <span>{item.source}</span>
                                    <span>•</span>
                                    <span>{item.time}</span>
                                </div>
                                {index < news.length - 1 && <div className="h-px bg-border mt-6" />}
                            </a>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};
