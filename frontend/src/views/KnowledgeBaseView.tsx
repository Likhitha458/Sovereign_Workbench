import React, { useState } from 'react';
import { BookOpen, Search, FileText, CheckCircle, ArrowRight } from 'lucide-react';
import { SourceCitation } from '../types';

export const KnowledgeBaseView: React.FC = () => {
    const [query, setQuery] = useState('');
    const [isSearching, setIsSearching] = useState(false);
    const [searchResults, setSearchResults] = useState<SourceCitation[]>([]);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        setIsSearching(true);
        try {
            const res = await fetch('/api/knowledge-base/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, top_k: 4 }),
            });
            const data = await res.json();
            setSearchResults(data.results || []);
        } catch (err) {
            console.error("Search error:", err);
        } finally {
            setIsSearching(false);
        }
    };

    return (
        <div className="flex-1 p-6 md:p-10 bg-[#F7F9F9] overflow-y-auto">
            <div className="max-w-5xl mx-auto space-y-6">
                <div>
                    <h1 className="text-2xl font-bold text-[#172B2B]">Knowledge Base</h1>
                    <p className="text-xs text-[#637575] mt-1">
                        Access grounded vectors from your company's sovereign document repository.
                    </p>
                </div>

                {/* Repository Stats Cards (Matching Figma Kit 03 Knowledge Base) */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-white p-4 rounded-card border border-canvas-border flex flex-col justify-between">
                        <span className="text-xs font-semibold text-[#637575]">Regulations</span>
                        <div className="flex items-baseline justify-between mt-2">
                            <span className="text-2xl font-bold text-[#172B2B]">12</span>
                            <span className="text-[11px] text-[#087F72] font-semibold">Documents</span>
                        </div>
                    </div>

                    <div className="bg-white p-4 rounded-card border border-canvas-border flex flex-col justify-between">
                        <span className="text-xs font-semibold text-[#637575]">SOPs</span>
                        <div className="flex items-baseline justify-between mt-2">
                            <span className="text-2xl font-bold text-[#172B2B]">8</span>
                            <span className="text-[11px] text-[#087F72] font-semibold">Documents</span>
                        </div>
                    </div>

                    <div className="bg-white p-4 rounded-card border border-canvas-border flex flex-col justify-between">
                        <span className="text-xs font-semibold text-[#637575]">Maintenance Manuals</span>
                        <div className="flex items-baseline justify-between mt-2">
                            <span className="text-2xl font-bold text-[#172B2B]">5</span>
                            <span className="text-[11px] text-[#087F72] font-semibold">Documents</span>
                        </div>
                    </div>

                    <div className="bg-white p-4 rounded-card border border-canvas-border flex flex-col justify-between">
                        <span className="text-xs font-semibold text-[#637575]">Inspection Reports</span>
                        <div className="flex items-baseline justify-between mt-2">
                            <span className="text-2xl font-bold text-[#172B2B]">10</span>
                            <span className="text-[11px] text-[#087F72] font-semibold">Documents</span>
                        </div>
                    </div>
                </div>

                {/* Semantic Query Box */}
                <form onSubmit={handleSearch} className="bg-white p-4 rounded-card border border-canvas-border flex gap-3">
                    <div className="flex-1 relative">
                        <Search className="w-4 h-4 text-[#8C9C9C] absolute left-3 top-3" />
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Query safety mandates, equipment tolerances, or inspection requirements..."
                            className="w-full pl-9 pr-4 py-2 bg-[#F7F9F9] border border-canvas-border rounded-control text-xs outline-none focus:border-[#087F72]"
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={isSearching}
                        className="bg-[#087F72] hover:bg-[#066B60] text-white px-5 py-2 rounded-control text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
                    >
                        <span>{isSearching ? 'Searching...' : 'Search'}</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                </form>

                {/* Relevant Excerpts Results */}
                <div className="space-y-4">
                    <h3 className="text-xs font-bold text-[#637575] uppercase tracking-wider">
                        Relevant Sections
                    </h3>

                    {searchResults.length > 0 ? (
                        searchResults.map((res, idx) => (
                            <div key={idx} className="bg-white p-4 rounded-card border border-canvas-border space-y-2 shadow-xs">
                                <div className="flex items-center justify-between text-xs font-semibold text-[#087F72]">
                                    <div className="flex items-center gap-2">
                                        <FileText className="w-4 h-4" />
                                        <span>{res.source}</span>
                                    </div>
                                    <span className="text-[11px] bg-[#E6F4F2] px-2 py-0.5 rounded text-[#087F72]">Match Score 98%</span>
                                </div>
                                <p className="text-xs text-[#172B2B] leading-relaxed bg-[#F7F9F9] p-3 rounded-md border border-canvas-border font-mono">
                                    "{res.snippet}"
                                </p>
                            </div>
                        ))
                    ) : (
                        /* Default Demo Excerpts matching Figma kit 03 Knowledge Base */
                        <div className="space-y-3">
                            <div className="bg-white p-4 rounded-card border border-canvas-border space-y-2 shadow-xs">
                                <div className="flex items-center justify-between text-xs font-semibold text-[#087F72]">
                                    <div className="flex items-center gap-2">
                                        <FileText className="w-4 h-4" />
                                        <span>Safety_Regulation_2025.pdf — Page 14</span>
                                    </div>
                                    <span className="text-[11px] bg-[#E6F4F2] px-2 py-0.5 rounded text-[#087F72]">Section 04.2</span>
                                </div>
                                <p className="text-xs text-[#172B2B] leading-relaxed bg-[#F7F9F9] p-3 rounded-md border border-canvas-border">
                                    "Pressure relief valve overpressure testing must be conducted every 12 months with mandatory supervisor sign-off recorded in maintenance logs."
                                </p>
                            </div>

                            <div className="bg-white p-4 rounded-card border border-canvas-border space-y-2 shadow-xs">
                                <div className="flex items-center justify-between text-xs font-semibold text-[#087F72]">
                                    <div className="flex items-center gap-2">
                                        <FileText className="w-4 h-4" />
                                        <span>Maintenance_SOP.pdf — Page 8</span>
                                    </div>
                                    <span className="text-[11px] bg-[#E6F4F2] px-2 py-0.5 rounded text-[#087F72]">Section 02.1</span>
                                </div>
                                <p className="text-xs text-[#172B2B] leading-relaxed bg-[#F7F9F9] p-3 rounded-md border border-canvas-border">
                                    "All maintenance records must include the responsible engineer's sign-off. Recent corrective actions and hydrostatic evidence required before operational release."
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
