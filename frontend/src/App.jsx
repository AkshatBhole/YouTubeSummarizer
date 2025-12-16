import React, { useState } from 'react';
import InputSection from './components/InputSection';
import SummaryCard from './components/SummaryCard';
import ComparativeCard from './components/ComparativeCard';
import TakeawayCard from './components/TakeawayCard';
import QuizCard from './components/QuizCard';
import AnswerCard from './components/AnswerCard';
import DifficultyCard from './components/DifficultyCard';
import NotesCard from './components/NotesCard';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE_URL = import.meta.env.DEV
  ? "http://localhost:5000"
  : import.meta.env.VITE_API_URL;


function App() {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async (url1, url2) => {
    setIsLoading(true);
    setError(null);
    setData(null);

    // Simulate network delay or call actual API
    try {
      // In a real scenario: const response = await fetch('http://localhost:5000/api/analyze', ...);
      // For this demo, we can just fetch from the local backend if running, or prompt the user.
      // We will try to fetch from the backend we set up.

      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url1, url2 })
      });

      if (!response.ok) {
        throw new Error("Failed to fetch analysis.");
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      console.error(err);
      console.error(err);
      let msg = err.message || "An unexpected error occurred.";
      if (err.message.includes("Failed to fetch")) {
        msg = "Unable to connect to the server. The backend might be waking up (cold start), please try again in a moment.";
      }
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-dots-pattern bg-dark-950 text-slate-200 p-4 md:p-8 font-sans selection:bg-brand-500/30">

      {/* Header */}
      <header className="text-center mb-12 pt-8">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl md:text-6xl font-extrabold tracking-tight mb-4"
        >
          Multi-Video <span className="gradient-text">Learning Engine</span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-slate-400 max-w-2xl mx-auto text-lg"
        >
          Transform multiple videos into a single, comprehensive study guide.
        </motion.p>
      </header>

      <InputSection onSubmit={fetchData} isLoading={isLoading} />

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="max-w-4xl mx-auto mb-8 p-4 rounded-lg bg-red-900/20 border border-red-500/50 text-red-200 text-center"
        >
          {error}
        </motion.div>
      )}

      <div className="max-w-4xl mx-auto pb-20">
        <AnimatePresence mode="wait">
          {isLoading && (
            <motion.div
              key="loader"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center py-20 space-y-4"
            >
              <div className="w-16 h-16 border-4 border-brand-500/30 border-t-brand-500 rounded-full animate-spin" />
              <p className="text-brand-400 animate-pulse">Synthesizing Comparison...</p>
            </motion.div>
          )}

          {!isLoading && data && (
            <motion.div
              key="content"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, staggerChildren: 0.1 }}
            >
              <SummaryCard data={data.summary} />
              <ComparativeCard data={data.comparativeInsights} />
              <TakeawayCard data={data.keyTakeaways} />
              <QuizCard data={data.quiz} />
              <AnswerCard data={data.quiz} />
              <DifficultyCard data={data.difficultyQuestions} />
              <NotesCard data={data.notes} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
