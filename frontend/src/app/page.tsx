'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  Music, 
  Download, 
  Settings, 
  Scissors, 
  BarChart3, 
  Box, 
  CheckCircle2, 
  XCircle,
  Loader2,
  Waves
} from 'lucide-react';
import { submitTask, getTaskStatus, getDownloadUrl } from '@/lib/api';

const STEPS = [
  { id: 'downloading', label: 'Downloading', icon: Download },
  { id: 'separating', label: 'AI Separating', icon: Scissors },
  { id: 'analyzing', label: 'Analyzing', icon: BarChart3 },
  { id: 'packaging', label: 'Packaging', icon: Box },
];

export default function Home() {
  const [input, setInput] = useState('');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('idle');
  const [resultFile, setResultFile] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Polling logic
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (taskId && (status !== 'completed' && status !== 'failed')) {
      interval = setInterval(async () => {
        try {
          const data = await getTaskStatus(taskId);
          console.log('Task Status Update:', data); // 🛠️ Debug log for tracking status
          setStatus(data.status);
          if (data.status === 'completed') {
            setResultFile(data.result_file);
            clearInterval(interval);
          } else if (data.status === 'failed') {
            setError(data.error || 'Processing failed');
            clearInterval(interval);
          }
        } catch (err) {
          console.error('Polling error:', err);
        }
      }, 3000);
    }

    return () => clearInterval(interval);
  }, [taskId, status]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input) return;

    setIsLoading(true);
    setError(null);
    setResultFile(null);
    setStatus('submitting');

    try {
      const data = await submitTask(input);
      setTaskId(data.task_id);
      setStatus('queued');
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to submit task');
      setStatus('idle');
    } finally {
      setIsLoading(false);
    }
  };

  const getStepStatus = (stepId: string) => {
    const statusOrder = ['queued', 'downloading', 'separating', 'analyzing', 'packaging', 'completed'];
    const currentIndex = statusOrder.indexOf(status);
    const stepIndex = statusOrder.indexOf(stepId);

    if (status === 'failed') return 'failed';
    if (status === 'completed') return 'completed';
    if (currentIndex > stepIndex) return 'completed';
    if (currentIndex === stepIndex) return 'current';
    return 'pending';
  };

  return (
    <main className="min-h-screen p-4 md:p-8 flex flex-col items-center justify-center bg-[#0a0a0b] text-white">
      {/* Background Decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/10 blur-[120px] rounded-full" />
      </div>

      <div className="w-full max-w-3xl z-10">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-indigo-400 text-sm font-medium mb-4">
            <Waves size={16} />
            <span>AI Audio Engine</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-4 text-white">
            Stem<span className="text-gradient">Sense.</span>
          </h1>
          <p className="text-zinc-400 text-lg md:text-xl max-w-xl mx-auto">
            Extract vocals, drums, and bass with professional AI accuracy. Fully analyzed.
          </p>
        </motion.div>

        {/* Search Bar */}
        <motion.form 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          onSubmit={handleSubmit}
          className="relative group mb-12"
        >
          <div className="absolute inset-0 bg-indigo-500/20 blur-2xl group-hover:bg-indigo-500/30 transition-all duration-500 rounded-[2rem] opacity-50" />
          <div className="relative flex items-center p-2 rounded-2xl glass glass-hover">
            <div className="pl-4 text-zinc-500">
              <Search size={22} />
            </div>
            <input 
              type="text" 
              placeholder="Paste YouTube URL or type song name..."
              className="flex-1 bg-transparent border-none outline-none px-4 py-3 text-lg placeholder:text-zinc-600"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={status !== 'idle' && status !== 'completed' && status !== 'failed'}
            />
            <button 
              type="submit"
              disabled={isLoading || (status !== 'idle' && status !== 'completed' && status !== 'failed')}
              className="px-6 py-3 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-white font-semibold transition-all shadow-lg shadow-indigo-500/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isLoading ? <Loader2 className="animate-spin" size={20} /> : <Music size={20} />}
              Process
            </button>
          </div>
        </motion.form>

        {/* Progress Section */}
        <AnimatePresence>
          {status !== 'idle' && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="glass rounded-3xl p-8 mb-8"
            >
              {status === 'failed' ? (
                <div className="flex flex-col items-center gap-4 text-center">
                  <XCircle size={48} className="text-red-500" />
                  <h3 className="text-xl font-bold">Processing Failed</h3>
                  <p className="text-zinc-400">{error}</p>
                  <button 
                    onClick={() => setStatus('idle')}
                    className="mt-2 text-indigo-400 hover:text-indigo-300 font-medium"
                  >
                    Try Again
                  </button>
                </div>
              ) : status === 'completed' ? (
                <div className="flex flex-col items-center gap-6 text-center">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="p-3 rounded-full bg-green-500/20 text-green-500"
                  >
                    <CheckCircle2 size={48} />
                  </motion.div>
                  <div>
                    <h3 className="text-2xl font-bold mb-2">Separation Complete!</h3>
                    <p className="text-zinc-400 mb-6">Your stems and analysis package is ready for download.</p>
                  </div>
                  
                  <div className="flex gap-4">
                    <a 
                      href={getDownloadUrl(resultFile!)}
                      className="flex items-center gap-2 px-8 py-4 rounded-2xl bg-white text-black font-bold hover:bg-zinc-200 transition-all"
                    >
                      <Download size={20} />
                      Download Stems
                    </a>
                    <button 
                      onClick={() => setStatus('idle')}
                      className="px-8 py-4 rounded-2xl glass glass-hover font-bold"
                    >
                      New Song
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-8">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-zinc-300">Processing Pipeline</h3>
                    <span className="text-sm px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 animate-pulse uppercase tracking-wider font-bold">
                      {status}...
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {STEPS.map((step) => {
                      const stepStatus = getStepStatus(step.id);
                      const isCurrent = stepStatus === 'current';
                      const isCompleted = stepStatus === 'completed';
                      
                      return (
                        <div key={step.id} className="relative">
                          <motion.div 
                            initial={false}
                            animate={{
                              scale: isCurrent ? 1.05 : 1,
                              backgroundColor: isCompleted ? 'rgba(79, 70, 229, 0.15)' : isCurrent ? 'rgba(255, 255, 255, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                              borderColor: isCompleted ? 'rgba(79, 70, 229, 0.4)' : isCurrent ? 'rgba(255, 255, 255, 0.3)' : 'rgba(255, 255, 255, 0.05)'
                            }}
                            className={`
                              flex flex-col items-center gap-3 p-5 rounded-2xl border transition-all duration-500 relative overflow-hidden
                              ${isCompleted ? 'text-indigo-400' : isCurrent ? 'text-white' : 'text-zinc-600'}
                            `}
                          >
                            {/* Inner Glow for current step */}
                            {isCurrent && (
                              <motion.div 
                                layoutId="glow"
                                className="absolute inset-0 bg-indigo-500/10 blur-xl"
                                animate={{ opacity: [0.3, 0.6, 0.3] }}
                                transition={{ duration: 2, repeat: Infinity }}
                              />
                            )}

                            <div className="relative z-10">
                              <step.icon size={28} className={isCurrent ? 'animate-bounce-subtle' : ''} />
                            </div>
                            <span className="text-xs font-bold uppercase tracking-wider z-10">{step.label}</span>
                            
                            <AnimatePresence>
                              {isCompleted && (
                                <motion.div 
                                  initial={{ scale: 0, opacity: 0 }}
                                  animate={{ scale: 1, opacity: 1 }}
                                  className="absolute top-2 right-2 text-indigo-400 z-10"
                                >
                                  <CheckCircle2 size={16} />
                                </motion.div>
                              )}
                            </AnimatePresence>

                            {/* Status text for current */}
                            {isCurrent && (
                              <motion.span 
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="text-[10px] font-bold text-indigo-400 mt-1 uppercase"
                              >
                                In Progress...
                              </motion.span>
                            )}
                          </motion.div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Visual Progress Bar Section */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs font-bold text-zinc-500 uppercase tracking-widest px-1">
                      <span>Start</span>
                      <span>Finish</span>
                    </div>
                    <div className="h-3 w-full bg-zinc-900 rounded-full p-1 border border-white/5 relative shadow-inner">
                      <motion.div 
                        className="h-full bg-gradient-to-r from-indigo-600 via-purple-500 to-indigo-400 rounded-full relative"
                        initial={{ width: '0%' }}
                        animate={{ 
                          width: status === 'queued' ? '5%' : 
                                 status === 'downloading' ? '25%' : 
                                 status === 'separating' ? '55%' : 
                                 status === 'analyzing' ? '75%' : 
                                 status === 'packaging' ? '90%' : '100%'
                        }}
                        transition={{ type: 'spring', stiffness: 50, damping: 20 }}
                      >
                        {/* Shimmer effect */}
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent w-20 animate-shimmer" />
                      </motion.div>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Feature Cards (Only show when idle) */}
        {status === 'idle' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { icon: Scissors, title: "Stem Isolation", desc: "Isolate vocals, drums, bass and more using Demucs AI." },
              { icon: BarChart3, title: "Deep Analysis", desc: "Get accurate BPM, Musical Key, and LUFS loudness data." },
              { icon: Box, title: "Zip Export", desc: "Everything packaged and ready for your DAW or sampler." }
            ].map((feature, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * i }}
                className="glass rounded-3xl p-6 glass-hover"
              >
                <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-4">
                  <feature.icon size={24} />
                </div>
                <h4 className="font-bold mb-2">{feature.title}</h4>
                <p className="text-zinc-500 text-sm leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
