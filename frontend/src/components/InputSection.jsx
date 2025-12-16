import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2, Youtube } from 'lucide-react';

const InputSection = ({ onSubmit, isLoading }) => {
    const [url1, setUrl1] = useState('');
    const [url2, setUrl2] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (url1 && url2) {
            onSubmit(url1, url2);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-4xl mx-auto mb-12"
        >
            <div className="glass-card p-8 rounded-2xl border-t border-white/10 relative overflow-hidden">
                {/* Background decorative blob */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />

                <h2 className="text-3xl font-bold mb-6 text-center">
                    <span className="gradient-text">Compare & Learn</span> from Videos
                </h2>

                <form onSubmit={handleSubmit} className="space-y-4 relative z-10">
                    <div className="grid md:grid-cols-2 gap-4">
                        <div className="group">
                            <label className="block text-sm font-medium text-slate-400 mb-2 ml-1">Video Source 1</label>
                            <div className="relative">
                                <Youtube className="absolute left-3 top-3.5 text-slate-500 w-5 h-5 group-focus-within:text-brand-400 transition-colors" />
                                <input
                                    type="text"
                                    placeholder="Paste first YouTube URL..."
                                    className="w-full bg-dark-900/50 border border-slate-700/50 rounded-xl py-3 pl-10 pr-4 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500/50 transition-all"
                                    value={url1}
                                    onChange={(e) => setUrl1(e.target.value)}
                                    disabled={isLoading}
                                />
                            </div>
                        </div>

                        <div className="group">
                            <label className="block text-sm font-medium text-slate-400 mb-2 ml-1">Video Source 2</label>
                            <div className="relative">
                                <Youtube className="absolute left-3 top-3.5 text-slate-500 w-5 h-5 group-focus-within:text-brand-400 transition-colors" />
                                <input
                                    type="text"
                                    placeholder="Paste second YouTube URL..."
                                    className="w-full bg-dark-900/50 border border-slate-700/50 rounded-xl py-3 pl-10 pr-4 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500/50 transition-all"
                                    value={url2}
                                    onChange={(e) => setUrl2(e.target.value)}
                                    disabled={isLoading}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="pt-4 flex justify-center">
                        <button
                            type="submit"
                            disabled={isLoading || !url1 || !url2}
                            className="group relative inline-flex items-center justify-center px-8 py-3 font-semibold text-white transition-all duration-200 bg-brand-600 rounded-full hover:bg-brand-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                    Generating Analysis...
                                </>
                            ) : (
                                <>
                                    Generate Comparison
                                    <Send className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                            {/* Button Glow Effect */}
                            <div className="absolute inset-0 rounded-full ring-2 ring-white/20 group-hover:ring-white/40 transition-all" />
                        </button>
                    </div>
                </form>
            </div>
        </motion.div>
    );
};

export default InputSection;
