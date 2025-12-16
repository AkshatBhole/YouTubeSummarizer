import React from 'react';
import SectionCard from './SectionCard';
import { Scale, ArrowRight, ThumbsUp, GitMerge } from 'lucide-react';

const ComparativeCard = ({ data }) => {
    return (
        <SectionCard title="Comparative Insights" icon={Scale} colorClass="text-purple-400">
            <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-6">
                    {/* Video 1 Output */}
                    <div className="p-5 rounded-xl bg-gradient-to-br from-indigo-900/20 to-transparent border border-indigo-500/20">
                        <h4 className="flex items-center gap-2 text-indigo-300 font-semibold mb-3">
                            <ThumbsUp className="w-4 h-4" /> Video 1 Explains Better
                        </h4>
                        <ul className="space-y-3">
                            {data.video1Better.map((point, idx) => (
                                <li key={idx} className="flex items-start gap-2 text-sm text-slate-300">
                                    <ArrowRight className="w-4 h-4 text-indigo-400 mt-1 shrink-0" />
                                    <span>{point}</span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Video 2 Output */}
                    <div className="p-5 rounded-xl bg-gradient-to-br from-cyan-900/20 to-transparent border border-cyan-500/20">
                        <h4 className="flex items-center gap-2 text-cyan-300 font-semibold mb-3">
                            <ThumbsUp className="w-4 h-4" /> Video 2 Explains Better
                        </h4>
                        <ul className="space-y-3">
                            {data.video2Better.map((point, idx) => (
                                <li key={idx} className="flex items-start gap-2 text-sm text-slate-300">
                                    <ArrowRight className="w-4 h-4 text-cyan-400 mt-1 shrink-0" />
                                    <span>{point}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Agreement Output */}
                <div className="p-5 rounded-xl bg-dark-800/40 border border-slate-700/30 h-full">
                    <h4 className="flex items-center gap-2 text-emerald-300 font-semibold mb-4">
                        <GitMerge className="w-4 h-4" /> Both Videos Agree On
                    </h4>
                    <ul className="space-y-4">
                        {data.agreement.map((point, idx) => (
                            <li key={idx} className="flex gap-3 text-sm text-slate-300">
                                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 shrink-0" />
                                <span>{point}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </SectionCard>
    );
};

export default ComparativeCard;
