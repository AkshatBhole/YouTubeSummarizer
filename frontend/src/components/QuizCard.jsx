import React, { useState } from 'react';
import SectionCard from './SectionCard';
import { BrainCircuit, Check, X, HelpCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const QuizItem = ({ item, index }) => {
    const [showAnswer, setShowAnswer] = useState(false);
    const [selectedOption, setSelectedOption] = useState(null);

    const isMCQ = item.type === 'mcq' || item.type === 'tf';

    return (
        <div className="p-5 rounded-xl bg-dark-800/60 border border-slate-700/50 mb-4 transition-all hover:border-slate-600">
            <div className="flex justify-between items-start gap-4 mb-4">
                <div>
                    <span className="inline-block px-2 py-1 mb-2 text-xs font-semibold rounded bg-slate-700 text-slate-300 uppercase tracking-wider">
                        Question {index + 1}
                    </span>
                    <h4 className="text-lg text-slate-200 font-medium">{item.question}</h4>
                </div>
                <button
                    onClick={() => setShowAnswer(!showAnswer)}
                    className="text-xs text-brand-400 hover:text-brand-300 transition-colors shrink-0"
                >
                    {showAnswer ? "Hide Answer" : "Reveal Answer"}
                </button>
            </div>

            {isMCQ ? (
                <div className="space-y-2">
                    {item.options.map((option, idx) => {
                        const isCorrect = option === item.answer;
                        const isSelected = selectedOption === option;

                        let btnClass = "w-full text-left p-3 rounded-lg border text-sm transition-all ";

                        if (showAnswer) {
                            if (isCorrect) btnClass += "bg-emerald-900/40 border-emerald-500/50 text-emerald-100";
                            else if (isSelected) btnClass += "bg-red-900/30 border-red-500/30 text-red-200";
                            else btnClass += "bg-dark-900/30 border-slate-700/30 text-slate-500 opacity-50";
                        } else {
                            if (isSelected) btnClass += "bg-brand-900/30 border-brand-500/50 text-brand-100";
                            else btnClass += "bg-dark-900/30 border-slate-700/30 text-slate-300 hover:bg-dark-900/50 hover:border-slate-600";
                        }

                        return (
                            <button
                                key={idx}
                                onClick={() => !showAnswer && setSelectedOption(option)}
                                disabled={showAnswer}
                                className={btnClass}
                            >
                                <div className="flex items-center justify-between">
                                    <span>{option}</span>
                                    {showAnswer && isCorrect && <Check className="w-4 h-4 text-emerald-400" />}
                                    {showAnswer && isSelected && !isCorrect && <X className="w-4 h-4 text-red-400" />}
                                </div>
                            </button>
                        )
                    })}
                </div>
            ) : (
                <div className="relative">
                    {!showAnswer ? (
                        <div
                            onClick={() => setShowAnswer(true)}
                            className="p-4 rounded-lg bg-dark-900/30 border border-slate-700/30 text-slate-500 text-sm cursor-pointer hover:bg-dark-900/50 transition-colors flex items-center gap-2"
                        >
                            <HelpCircle className="w-4 h-4" /> Tap to reveal answer
                        </div>
                    ) : (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="p-4 rounded-lg bg-emerald-900/20 border border-emerald-500/30 text-emerald-100 text-sm"
                        >
                            <span className="font-semibold block mb-1 text-emerald-400">Answer:</span>
                            {item.answer}
                        </motion.div>
                    )}
                </div>
            )}
        </div>
    );
};

const QuizCard = ({ data }) => {
    return (
        <SectionCard title="Knowledge Check" icon={BrainCircuit} colorClass="text-pink-400">
            <div>
                {data.map((item, index) => (
                    <QuizItem key={item.id} item={item} index={index} />
                ))}
            </div>
        </SectionCard>
    );
};

export default QuizCard;
