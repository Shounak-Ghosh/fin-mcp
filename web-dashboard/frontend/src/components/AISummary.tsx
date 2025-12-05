import React from 'react';

interface Props {
    summary: string;
    loading: boolean;
}

export const AISummary: React.FC<Props> = ({ summary, loading }) => {
    return (
        <div className="bg-card rounded-xl p-6 mb-8 border border-white/10 relative overflow-hidden">
            {/* Gradient background effect */}
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"></div>

            <div className="flex items-start gap-4">
                <div className="p-2 bg-blue-500/10 rounded-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                </div>

                <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
                        AI Market Summary

                    </h3>

                    {loading ? (
                        <div className="space-y-2 animate-pulse">
                            <div className="h-4 bg-white/10 rounded w-3/4"></div>
                            <div className="h-4 bg-white/10 rounded w-1/2"></div>
                            <div className="h-4 bg-white/10 rounded w-5/6"></div>
                        </div>
                    ) : (
                        <div className="text-muted leading-relaxed space-y-2">
                            {summary.split('\n').map((paragraph, pIndex) => (
                                <p key={pIndex}>
                                    {paragraph.split(/(\*\*.*?\*\*|\[\[.*?\]\])/g).map((part, index) => {
                                        if (part.startsWith('**') && part.endsWith('**')) {
                                            return <strong key={index} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
                                        }
                                        if (part.startsWith('[[') && part.endsWith(']]')) {
                                            const content = part.slice(2, -2);
                                            // Handle case where pipe might be missing
                                            const [color, text] = content.includes('|')
                                                ? content.split('|')
                                                : ['blue', content];

                                            let colorClass = 'text-blue-400';
                                            if (color.trim() === 'green') colorClass = 'text-green-400';
                                            if (color.trim() === 'red') colorClass = 'text-red-400';

                                            return <span key={index} className={colorClass}>{text || color}</span>;
                                        }
                                        return part;
                                    })}
                                </p>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
