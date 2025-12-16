import React from 'react';
import SectionCard from './SectionCard';
import { BookOpen, Quote } from 'lucide-react';

const NotesCard = ({ data }) => {
    return (
        <SectionCard title="Final Learning Notes" icon={BookOpen} colorClass="text-teal-400">
            <div className="p-6 rounded-xl bg-gradient-to-r from-teal-900/20 to-transparent border border-teal-500/20 relative overflow-hidden">
                <Quote className="absolute top-4 left-4 w-8 h-8 text-teal-500/20 rotate-180" />
                <p className="relative z-10 text-slate-300 italic leading-relaxed text-lg pl-8">
                    "{data}"
                </p>
            </div>
        </SectionCard>
    );
};

export default NotesCard;
