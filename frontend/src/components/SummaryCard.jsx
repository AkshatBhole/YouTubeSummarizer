import React from 'react';
import SectionCard from './SectionCard';
import { FileText, CheckCircle2 } from 'lucide-react';

const SummaryCard = ({ data }) => {
    return (
        <SectionCard title="Combined Summary" icon={FileText} defaultOpen={true} colorClass="text-blue-400">
            <div className="space-y-6">
                {data.map((item, index) => (
                    <div key={index} className="flex gap-4 p-5 rounded-xl bg-dark-800/60 border border-slate-700/50 hover:border-slate-600/80 transition-all duration-300 shadow-sm">
                        <div className="mt-1 flex-shrink-0">
                            <CheckCircle2 className="w-6 h-6 text-brand-500" />
                        </div>
                        <div className="flex-1">
                            <h4 className="text-xl font-semibold text-slate-100 mb-2">{item.title}</h4>

                            {/* Main Content (if any) */}
                            {item.content && (
                                <p className="text-slate-400 leading-relaxed text-sm lg:text-base mb-4">
                                    {item.content}
                                </p>
                            )}

                            {/* Subtopics */}
                            {item.subtopics && item.subtopics.length > 0 && (
                                <div className="space-y-4 mt-4">
                                    {item.subtopics.map((sub, subIndex) => (
                                        <div key={subIndex} className="bg-dark-900/50 p-4 rounded-lg border border-slate-700/30">
                                            <h5 className="text-md font-medium text-brand-300 mb-2 border-b border-slate-700/50 pb-1 inline-block">
                                                {sub.heading}
                                            </h5>
                                            <ul className="space-y-2 mt-2">
                                                {sub.points.map((point, pIndex) => (
                                                    <li key={pIndex} className="text-slate-400 text-sm flex items-start gap-2">
                                                        <span className="w-1.5 h-1.5 rounded-full bg-slate-500 mt-2 flex-shrink-0" />
                                                        <span className="flex-1">{point}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </SectionCard>
    );
};

export default SummaryCard;
