import React from 'react';
import SectionCard from './SectionCard';
import { Key } from 'lucide-react';

const AnswerCard = ({ data }) => {
    return (
        <SectionCard title="Answer Key" icon={Key} colorClass="text-emerald-400" defaultOpen={false}>
            <div className="space-y-4">
                {data.map((item, index) => (
                    <div key={index} className="flex gap-4 p-3 rounded-lg hover:bg-white/5 transition-colors border-b border-white/5 last:border-0">
                        <div className="text-emerald-500 font-mono text-sm font-bold pt-1">
                            {index + 1}.
                        </div>
                        <div>
                            <p className="text-sm text-slate-400 mb-1">{item.question}</p>
                            <p className="text-slate-200 font-medium">{item.answer}</p>
                        </div>
                    </div>
                ))}
            </div>
        </SectionCard>
    );
};

export default AnswerCard;
