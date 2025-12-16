import React from 'react';
import SectionCard from './SectionCard';
import { Target } from 'lucide-react';

const Box = ({ title, questions, color }) => (
    <div className={`rounded-xl border ${color} bg-opacity-5 overflow-hidden h-full`}>
        <div className={`px-4 py-3 border-b ${color} bg-opacity-10 backdrop-blur-sm`}>
            <h4 className="font-semibold text-slate-200">{title}</h4>
        </div>
        <div className="p-4">
            <ul className="space-y-3">
                {questions.map((q, idx) => (
                    <li key={idx} className="text-sm text-slate-300 flex items-start gap-2">
                        <span className="opacity-50 mt-0.5">•</span>
                        {q}
                    </li>
                ))}
            </ul>
        </div>
    </div>
);

const DifficultyCard = ({ data }) => {
    return (
        <SectionCard title="Difficulty-Based Questions" icon={Target} colorClass="text-orange-400">
            <div className="grid md:grid-cols-3 gap-6">
                <Box
                    title="Easy"
                    questions={data.easy}
                    color="border-emerald-500/30 bg-emerald-500"
                />
                <Box
                    title="Medium"
                    questions={data.medium}
                    color="border-yellow-500/30 bg-yellow-500"
                />
                <Box
                    title="Hard"
                    questions={data.hard}
                    color="border-red-500/30 bg-red-500"
                />
            </div>
        </SectionCard>
    );
};

export default DifficultyCard;
