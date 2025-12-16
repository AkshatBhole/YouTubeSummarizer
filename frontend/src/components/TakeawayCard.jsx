import React from 'react';
import SectionCard from './SectionCard';
import { Star, ShieldCheck } from 'lucide-react';

const TakeawayCard = ({ data }) => {
    return (
        <SectionCard title="Key Takeaways" icon={Star} colorClass="text-yellow-400">
            <div className="grid sm:grid-cols-2 gap-4">
                {data.map((item, index) => (
                    <div key={index} className="flex items-start gap-3 p-4 rounded-lg bg-yellow-400/5 border border-yellow-400/10">
                        <ShieldCheck className="w-5 h-5 text-yellow-400 shrink-0" />
                        <p className="text-sm text-slate-200 font-medium">{item}</p>
                    </div>
                ))}
            </div>
        </SectionCard>
    );
};

export default TakeawayCard;
