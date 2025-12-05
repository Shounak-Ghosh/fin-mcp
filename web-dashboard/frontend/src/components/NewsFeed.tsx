import React from 'react';
import { Link } from 'react-router-dom';
import type { NewsItem } from '../types';

interface Props {
    data: NewsItem[];
}

export const NewsFeed: React.FC<Props> = ({ data }) => {
    return (
        <div className="bg-surface rounded-xl p-6 border border-border">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-semibold text-text">Market Summary</h2>
                <span className="text-xs text-muted">Updated recently</span>
            </div>

            <div className="space-y-6">
                {data.map((item, index) => (
                    <a
                        key={index}
                        href={item.url || '#'}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block group cursor-pointer"
                    >
                        <h3 className="text-text font-medium mb-2 group-hover:text-primary transition-colors">{item.title}</h3>
                        <p className="text-muted text-sm mb-2 line-clamp-2">{item.summary}</p>
                        <div className="flex items-center gap-2 text-xs text-muted/60">
                            <span>{item.source}</span>
                            <span>•</span>
                            <span>{item.time}</span>
                        </div>
                        {index < data.length - 1 && <div className="h-px bg-border mt-4" />}
                    </a>
                ))}
            </div>

            <div className="mt-6 pt-4 border-t border-border">
                <Link
                    to="/news"
                    className="block w-full text-center py-2 text-sm font-medium text-blue-500 hover:text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors"
                >
                    See More
                </Link>
            </div>
        </div>
    );
};
