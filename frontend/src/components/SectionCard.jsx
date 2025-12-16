import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp } from 'lucide-react';

const SectionCard = ({ title, icon: Icon, children, defaultOpen = false, colorClass = "text-brand-400" }) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-6 group"
        >
            <div className="glass-card rounded-xl overflow-hidden border border-slate-700/30 hover:border-slate-600/50 transition-colors">
                <button
                    onClick={() => setIsOpen(!isOpen)}
                    className="w-full flex items-center justify-between p-5 bg-dark-800/30 hover:bg-dark-800/50 transition-colors"
                >
                    <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg bg-dark-900 ring-1 ring-white/5 ${colorClass}`}>
                            <Icon className="w-6 h-6" />
                        </div>
                        <h3 className="text-xl font-semibold text-slate-100">{title}</h3>
                    </div>
                    <div className={`p-1 rounded-full bg-slate-800/50 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}>
                        <ChevronDown className="w-5 h-5 text-slate-400" />
                    </div>
                </button>

                <AnimatePresence>
                    {isOpen && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.3 }}
                            className="overflow-hidden"
                        >
                            <div className="p-6 pt-0 border-t border-slate-700/30 bg-dark-900/20">
                                <div className="pt-6">
                                    {children}
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </motion.div>
    );
};

export default SectionCard;
