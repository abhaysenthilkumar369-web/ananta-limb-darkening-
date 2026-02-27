import React from 'react';
import { motion } from 'framer-motion';

const MODELS = [
    { id: 'linear', name: 'Linear', equation: '1 - u_{1}(1 - \\mu)' },
    { id: 'quadratic', name: 'Quadratic', equation: '1 - a_{1}(1-\\mu) - a_{2}(1-\\mu)^2' },
    { id: 'square-root', name: 'Square-root', equation: '1 - c(1-\\mu) - d(1-\\sqrt{\\mu})' },
    { id: 'logarithmic', name: 'Logarithmic', equation: '1 - e(1-\\mu) - f\\mu\\ln(\\mu)' },
    { id: 'claret', name: 'Claret 4-parameter', equation: '1 - \\sum a_{k}(1-\\mu^{k/2})' },
    { id: 'compare', name: 'Compare Models', equation: 'Rank models by \u03C7^{2}_{red}' }
];

export const ModelCards = ({ selectedModel, onSelectModel }) => {
    return (
        <div className="glass-panel p-6 mt-8">
            <h3 className="text-xl font-light mb-6 text-center text-white/90">Limb Darkening Model Selection</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {MODELS.map((model) => {
                    const isSelected = selectedModel === model.id;
                    return (
                        <motion.div
                            key={model.id}
                            onClick={() => onSelectModel(model.id)}
                            className={`relative overflow-hidden cursor-pointer rounded-[20px] transition-all duration-300 ${isSelected ? 'glass-card-active' : 'glass-card'
                                }`}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                        >
                            {/* Active state glow background */}
                            {isSelected && (
                                <motion.div
                                    layoutId="activeGlow"
                                    className="absolute inset-0 bg-gradient-to-br from-accent-teal/20 to-transparent z-0"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ duration: 0.3 }}
                                />
                            )}

                            <div className="relative z-10 p-5 h-full flex flex-col justify-center">
                                <h4 className="font-medium text-lg mb-2">{model.name}</h4>
                                <div className="text-accent-teal/80 text-sm font-mono opacity-80">
                                    {model.id === 'compare' ? (
                                        <span>{model.equation}</span>
                                    ) : (
                                        <span>{`$$ I(\\mu)/I(1) = ${model.equation} $$`}</span>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
};
