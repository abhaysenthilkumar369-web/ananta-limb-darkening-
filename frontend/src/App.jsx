import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, Loader2, AlertCircle } from 'lucide-react';
import axios from 'axios';
import { ModelCards } from './components/ModelCards';
import { ResultsGraphs } from './components/Graphs';

function App() {
    const [file, setFile] = useState(null);
    const [selectedModel, setSelectedModel] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [analysisData, setAnalysisData] = useState(null);

    // For Cloud Run, this uses the same host if served via proxy, or specific address
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

    const handleFileUpload = (e) => {
        const selected = e.target.files[0];
        if (selected) {
            setFile(selected);
            // Reset state on new file
            setAnalysisData(null);
            setSelectedModel('');
            setError('');
        }
    };

    const executeAnalysis = async () => {
        if (!file || !selectedModel) return;

        setLoading(true);
        setError('');

        const formData = new FormData();
        formData.append('image', file);
        formData.append('model_type', selectedModel);

        try {
            const response = await axios.post(`${API_URL}/analyze`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setAnalysisData(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Analysis failed. Please check the image and try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadReport = async () => {
        if (!file || !selectedModel) return;

        try {
            const formData = new FormData();
            formData.append('image', file);
            formData.append('model_type', selectedModel);

            const response = await axios.post(`${API_URL}/download_report`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                responseType: 'blob', // Important for PDF
            });

            const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `ANANTA_Limb_Darkening_Report_${selectedModel}.pdf`);
            document.body.appendChild(link);
            link.click();

            window.URL.revokeObjectURL(url);
            link.remove();

        } catch (err) {
            setError('Failed to download PDF report. ' + err.message);
        }
    };

    return (
        <div className="min-h-screen flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8">
            {/* Header section (Liquid Glass Styling) */}
            <motion.div
                initial={{ y: -20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className="text-center mb-12"
            >
                <h1 className="text-4xl md:text-5xl font-extralight tracking-tight text-gradient mb-3">
                    ANANTA <span className="font-semibold text-accent-teal">Limb Darkening Analyser</span>
                </h1>
                <p className="text-white/60 text-lg tracking-wide uppercase text-sm" style={{ letterSpacing: '0.15em' }}>
                    The NExT Gen Tool for Astronomy
                </p>
            </motion.div>

            {/* Main Content Area */}
            <motion.div
                className="w-full max-w-5xl flex flex-col gap-6"
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.8, delay: 0.2 }}
            >
                {/* Upload Panel */}
                <div className="glass-panel p-8 text-center border border-white/10 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-[24px]" />
                    <Upload className={`mx-auto w-12 h-12 mb-4 transition-colors ${file ? 'text-green-400' : 'text-accent-teal/80'}`} />
                    <h2 className="text-2xl font-light mb-2">
                        {file ? `Selected Image: ${file.name}` : "Upload Stellar Observation"}
                    </h2>
                    <p className="text-white/50 mb-6 text-sm">Supported formats: PNG, JPEG, FITS</p>
                    <label className="relative inline-flex cursor-pointer items-center justify-center px-8 py-3 font-medium text-white transition-all bg-white/10 rounded-full hover:bg-white/20 border border-white/10 hover:border-accent-teal/50 hover:shadow-[0_0_20px_rgba(0,212,255,0.3)]">
                        <span>{file ? 'Change File' : 'Select File'}</span>
                        <input type="file" className="hidden" accept=".png,.jpeg,.jpg,.fits" onChange={handleFileUpload} />
                    </label>
                </div>

                {/* Model Selection Pipeline */}
                {file && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        <ModelCards selectedModel={selectedModel} onSelectModel={setSelectedModel} />
                    </motion.div>
                )}

                {/* Action Button & Errors */}
                <AnimatePresence>
                    {selectedModel && !loading && !analysisData && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            className="flex justify-center mt-4"
                        >
                            <button
                                onClick={executeAnalysis}
                                className="px-8 py-4 font-semibold text-lg text-space-dark bg-accent-teal rounded-full shadow-[0_0_30px_rgba(0,212,255,0.4)] hover:shadow-[0_0_40px_rgba(0,212,255,0.6)] hover:bg-white transition-all transform hover:scale-105"
                            >
                                Analyze with Selected {selectedModel === 'compare' ? 'Models' : 'Model'}
                            </button>
                        </motion.div>
                    )}

                    {loading && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex flex-col items-center justify-center py-12"
                        >
                            <Loader2 className="w-12 h-12 text-accent-teal animate-spin mb-4" />
                            <p className="text-xl font-light text-white/80">Crunching stellar pixels...</p>
                        </motion.div>
                    )}

                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="glass-panel border-red-500/30 bg-red-500/10 p-4 flex items-center justify-center text-red-200 mt-4"
                        >
                            <AlertCircle className="w-6 h-6 mr-3" />
                            <span>{error}</span>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Results Data Matrix */}
                {analysisData && !loading && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex flex-col gap-6"
                    >
                        <ResultsGraphs analysisData={analysisData} selectedModel={selectedModel} />

                        {/* Scientific Report Download Block */}
                        <div className="glass-panel p-6 mt-4 flex items-center justify-between">
                            <div>
                                <h4 className="text-lg font-medium text-white/90">Mathematical Report Export</h4>
                                <p className="text-sm text-white/50 max-w-lg mt-1">
                                    Download a complete 3-page publication-grade PDF containing analytical results, classical drift scan representations, and statistical proofs.
                                </p>
                            </div>
                            <button
                                onClick={handleDownloadReport}
                                className="flex items-center px-6 py-3 bg-white/10 hover:bg-white/20 border border-white/20 rounded-full transition-all text-white font-medium group"
                            >
                                <FileText className="w-5 h-5 mr-2 text-accent-teal group-hover:scale-110 transition-transform" />
                                Download Scientific Report
                            </button>
                        </div>
                    </motion.div>
                )}

            </motion.div>
        </div>
    );
}

export default App;
