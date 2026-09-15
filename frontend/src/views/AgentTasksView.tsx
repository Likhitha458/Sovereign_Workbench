import React, { useState } from 'react';
import {
    Workflow,
    FileText,
    CheckCircle2,
    AlertTriangle,
    Download,
    Eye,
    Check,
    X,
    Play,
    Loader2,
    ShieldAlert,
    ExternalLink
} from 'lucide-react';
import { AgentTaskResult, Finding } from '../types';

export const AgentTasksView: React.FC = () => {
    const [isRunning, setIsRunning] = useState(false);
    const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
    const [taskResult, setTaskResult] = useState<AgentTaskResult | null>(null);
    const [showPreviewModal, setShowPreviewModal] = useState(false);
    const [humanDecision, setHumanDecision] = useState<'pending' | 'approved' | 'rejected'>('pending');

    const stepsList = [
        { num: 1, label: 'Document uploaded' },
        { num: 2, label: 'Text extracted' },
        { num: 3, label: 'OCR completed' },
        { num: 4, label: 'Regulations searched' },
        { num: 5, label: 'SOP searched' },
        { num: 6, label: 'Findings analyzed' },
        { num: 7, label: 'Risks identified' },
        { num: 8, label: 'Recommendations generated' },
        { num: 9, label: 'Approval note prepared' },
        { num: 10, label: 'Generating approval note' },
    ];

    const handleStartAnalysis = async () => {
        setIsRunning(true);
        setCurrentStepIndex(1);
        setTaskResult(null);
        setHumanDecision('pending');

        // Smooth timeline animation simulation synced with server execution
        for (let step = 1; step <= 9; step++) {
            await new Promise((r) => setTimeout(r, 400));
            setCurrentStepIndex(step);
        }

        try {
            const res = await fetch('/api/agent/inspection/run', { method: 'POST' });
            const data: AgentTaskResult = await res.json();
            setCurrentStepIndex(10);
            setTaskResult(data);
        } catch (err) {
            console.error("Agent workflow error:", err);
        } finally {
            setIsRunning(false);
        }
    };

    const handleDownloadDocx = () => {
        if (!taskResult?.docx_filename) return;
        window.open(`/api/agent/download/${taskResult.docx_filename}`, '_blank');
    };

    return (
        <div className="flex-1 p-6 md:p-10 bg-[#F7F9F9] overflow-y-auto relative">
            <div className="max-w-5xl mx-auto space-y-6">

                {/* Header Title Banner */}
                <div className="flex items-center justify-between">
                    <div>
                        <div className="inline-flex items-center gap-1 text-[11px] font-bold text-[#087F72] uppercase tracking-wider bg-[#E6F4F2] px-2.5 py-0.5 rounded border border-[#BDE3DE] mb-1">
                            <Workflow className="w-3 h-3" />
                            <span>Smart Agent Workflow</span>
                        </div>
                        <h1 className="text-2xl font-bold text-[#172B2B]">Inspection report → Approval note</h1>
                        <p className="text-xs text-[#637575] mt-0.5">
                            A guided workflow with document evidence at every step.
                        </p>
                    </div>

                    <div className="flex items-center gap-2">
                        <button
                            onClick={handleStartAnalysis}
                            disabled={isRunning}
                            className="bg-[#087F72] hover:bg-[#066B60] text-white px-5 py-2.5 rounded-control text-xs font-semibold flex items-center gap-2 transition-colors disabled:opacity-50 shadow-sm"
                        >
                            {isRunning ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    <span>Analyzing Unit 04...</span>
                                </>
                            ) : (
                                <>
                                    <Play className="w-4 h-4 fill-white" />
                                    <span>Start Analysis →</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>

                {/* Input Documents & Analysis Progress Timeline Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                    {/* Input Documents Card */}
                    <div className="bg-white p-5 rounded-card border border-canvas-border space-y-3 shadow-xs">
                        <h3 className="text-xs font-bold text-[#637575] uppercase tracking-wider">
                            Input Documents
                        </h3>

                        <div className="space-y-2">
                            <div className="flex items-center justify-between p-2.5 bg-[#F7F9F9] border border-canvas-border rounded-md text-xs">
                                <div className="flex items-center gap-2 font-medium text-[#172B2B]">
                                    <FileText className="w-4 h-4 text-[#087F72]" />
                                    <span>Inspection_Report_Unit04.pdf</span>
                                </div>
                                <span className="text-[10px] text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded">Ready</span>
                            </div>

                            <div className="flex items-center justify-between p-2.5 bg-[#F7F9F9] border border-canvas-border rounded-md text-xs">
                                <div className="flex items-center gap-2 font-medium text-[#172B2B]">
                                    <FileText className="w-4 h-4 text-[#087F72]" />
                                    <span>Safety_Regulation_2025.pdf</span>
                                </div>
                                <span className="text-[10px] text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded">Ready</span>
                            </div>

                            <div className="flex items-center justify-between p-2.5 bg-[#F7F9F9] border border-canvas-border rounded-md text-xs">
                                <div className="flex items-center gap-2 font-medium text-[#172B2B]">
                                    <FileText className="w-4 h-4 text-[#087F72]" />
                                    <span>Maintenance_SOP.pdf</span>
                                </div>
                                <span className="text-[10px] text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded">Ready</span>
                            </div>
                        </div>

                        <div className="pt-2">
                            <h4 className="text-xs font-semibold text-[#172B2B] mb-1">What you'll receive</h4>
                            <p className="text-xs text-[#637575] leading-relaxed">
                                Source-linked findings, severity levels, regulatory checks, and a formatted DOCX approval note ready for human review.
                            </p>
                        </div>
                    </div>

                    {/* Analysis Progress Timeline Card (Matching Figma Kit 04a Agent Tasks Running) */}
                    <div className="bg-white p-5 rounded-card border border-canvas-border space-y-3 shadow-xs">
                        <div className="flex items-center justify-between">
                            <h3 className="text-xs font-bold text-[#637575] uppercase tracking-wider">
                                Analysis Progress
                            </h3>
                            <span className={`text-xs font-semibold px-2 py-0.5 rounded ${taskResult ? 'bg-emerald-50 text-emerald-700' : isRunning ? 'bg-amber-50 text-amber-700' : 'bg-gray-100 text-gray-600'
                                }`}>
                                {taskResult ? 'Completed' : isRunning ? 'Running' : 'Ready'}
                            </span>
                        </div>

                        <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                            {stepsList.map((st) => {
                                const isCompleted = currentStepIndex > st.num || taskResult !== null;
                                const isCurrent = currentStepIndex === st.num && isRunning;
                                return (
                                    <div key={st.num} className="flex items-center gap-3 text-xs">
                                        <div className={`w-5 h-5 rounded-full flex items-center justify-center font-mono text-[10px] font-bold ${isCompleted
                                                ? 'bg-[#087F72] text-white'
                                                : isCurrent
                                                    ? 'bg-amber-500 text-white animate-pulse'
                                                    : 'bg-[#F7F9F9] text-[#8C9C9C] border border-canvas-border'
                                            }`}>
                                            {isCompleted ? <Check className="w-3 h-3 text-white" /> : st.num}
                                        </div>
                                        <span className={`font-medium ${isCompleted ? 'text-[#172B2B]' : isCurrent ? 'text-amber-700 font-bold' : 'text-[#8C9C9C]'
                                            }`}>
                                            {st.label}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>

                {/* Results Section (Matching Figma Kit 04b Agent Task Results) */}
                {taskResult && (
                    <div className="space-y-6 pt-4 border-t border-canvas-border">

                        {/* Warning Alert Banner */}
                        <div className="bg-amber-50 border border-amber-200 p-4 rounded-card flex items-start gap-3 text-amber-900">
                            <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                            <div>
                                <h4 className="font-bold text-sm">Corrective action required before operational approval.</h4>
                                <p className="text-xs text-amber-800 mt-0.5">
                                    Inspection identified overdue valve maintenance and missing supervisor signature in Unit 04 logs.
                                </p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                            {/* Findings Column */}
                            <div className="md:col-span-2 space-y-3">
                                <h3 className="text-sm font-bold text-[#172B2B]">Key Inspection Findings</h3>

                                <div className="space-y-3">
                                    {taskResult.findings.map((f, idx) => (
                                        <div key={idx} className="bg-white p-4 rounded-card border border-canvas-border space-y-2 shadow-xs">
                                            <div className="flex items-center justify-between">
                                                <span className="font-semibold text-xs text-[#172B2B]">{f.title}</span>
                                                <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${f.severity === 'HIGH' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-amber-50 text-amber-700 border border-amber-200'
                                                    }`}>
                                                    {f.severity} RISK
                                                </span>
                                            </div>
                                            <p className="text-xs text-[#637575] leading-relaxed">{f.detail}</p>
                                            <div className="flex items-center gap-1.5 text-[11px] font-mono text-[#087F72]">
                                                <FileText className="w-3 h-3" />
                                                <span>Source: {f.ref}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {/* Recommendations */}
                                <div className="bg-white p-4 rounded-card border border-canvas-border space-y-2">
                                    <h4 className="font-bold text-xs text-[#172B2B] uppercase">Corrective Action Recommendations</h4>
                                    <ul className="space-y-1 text-xs text-[#637575] list-disc list-inside">
                                        {taskResult.recommendations.map((rec, i) => (
                                            <li key={i}>{rec}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>

                            {/* Draft Approval Note Card (Figma 04b right card) */}
                            <div className="bg-white p-5 rounded-card border border-canvas-border flex flex-col justify-between shadow-xs">
                                <div>
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-[11px] font-bold text-[#087F72] uppercase tracking-wider bg-[#E6F4F2] px-2 py-0.5 rounded border border-[#BDE3DE]">
                                            Approval Note
                                        </span>
                                        <span className="text-[11px] font-mono text-[#637575]">DRAFT</span>
                                    </div>

                                    <h3 className="font-bold text-sm text-[#172B2B] mb-2">INSPECTION REPORT — UNIT 04</h3>
                                    <p className="text-xs text-[#637575] leading-relaxed mb-4">
                                        Summary, findings, regulatory citations, and recommended actions prepared for supervisor sign-off.
                                    </p>
                                </div>

                                <div className="space-y-2 pt-4 border-t border-canvas-border">
                                    <div className="grid grid-cols-2 gap-2">
                                        <button
                                            onClick={() => setShowPreviewModal(true)}
                                            className="bg-[#F7F9F9] hover:bg-canvas-border text-[#172B2B] py-2 px-3 rounded-control text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors border border-canvas-border"
                                        >
                                            <Eye className="w-3.5 h-3.5" />
                                            <span>Preview</span>
                                        </button>

                                        <button
                                            onClick={handleDownloadDocx}
                                            className="bg-[#087F72] hover:bg-[#066B60] text-white py-2 px-3 rounded-control text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors shadow-xs"
                                        >
                                            <Download className="w-3.5 h-3.5" />
                                            <span>DOCX</span>
                                        </button>
                                    </div>

                                    {/* Human-in-the-Loop Review Buttons */}
                                    <div className="pt-2 border-t border-canvas-border flex items-center gap-2">
                                        <button
                                            onClick={() => setHumanDecision('approved')}
                                            className={`flex-1 py-2 px-3 rounded-control text-xs font-semibold flex items-center justify-center gap-1 transition-colors ${humanDecision === 'approved'
                                                    ? 'bg-emerald-600 text-white'
                                                    : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200'
                                                }`}
                                        >
                                            <Check className="w-3.5 h-3.5" />
                                            <span>Approve</span>
                                        </button>

                                        <button
                                            onClick={() => setHumanDecision('rejected')}
                                            className={`flex-1 py-2 px-3 rounded-control text-xs font-semibold flex items-center justify-center gap-1 transition-colors ${humanDecision === 'rejected'
                                                    ? 'bg-red-600 text-white'
                                                    : 'bg-red-50 text-red-700 hover:bg-red-100 border border-red-200'
                                                }`}
                                        >
                                            <X className="w-3.5 h-3.5" />
                                            <span>Reject</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Approval Note Document Preview Modal (Figma kit screen 04c Approval Note Modal) */}
                {showPreviewModal && taskResult && (
                    <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
                        <div className="bg-white rounded-card max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6 space-y-4 border border-canvas-border shadow-2xl relative">
                            <div className="flex items-center justify-between border-b border-canvas-border pb-3">
                                <span className="text-xs font-mono font-bold text-[#087F72]">APPROVAL NOTE PREVIEW</span>
                                <button
                                    onClick={() => setShowPreviewModal(false)}
                                    className="text-[#637575] hover:text-[#172B2B] p-1 rounded-md"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            {/* Formatted Document Paper View */}
                            <div className="bg-[#F7F9F9] border border-canvas-border p-6 rounded-lg text-xs space-y-4 font-sans text-[#172B2B]">
                                <div className="text-center pb-3 border-b border-canvas-border">
                                    <h2 className="text-lg font-bold text-[#087F72]">SOVEREIGN AI WORKBENCH — APPROVAL NOTE</h2>
                                    <p className="text-slate-500 font-mono">SUBJECT: Inspection Report — Unit 04</p>
                                    <p className="text-slate-400 text-[10px]">Reference: REF-SOV-04-2026</p>
                                </div>

                                <div>
                                    <h4 className="font-bold text-[#172B2B] uppercase mb-1">1. Summary</h4>
                                    <p className="text-[#637575] leading-relaxed">{taskResult.summary}</p>
                                </div>

                                <div>
                                    <h4 className="font-bold text-[#172B2B] uppercase mb-1">2. Key Findings</h4>
                                    <ul className="space-y-1 list-disc list-inside text-[#637575]">
                                        {taskResult.findings.map((f, i) => (
                                            <li key={i}><strong className="text-[#172B2B]">{f.title}</strong> — {f.detail}</li>
                                        ))}
                                    </ul>
                                </div>

                                <div>
                                    <h4 className="font-bold text-[#172B2B] uppercase mb-1">3. Regulatory References</h4>
                                    <p className="text-[#087F72] font-mono">Safety_Regulation_2025.pdf — Page 14 (Section 04.2)</p>
                                    <p className="text-[#087F72] font-mono">Maintenance_SOP.pdf — Page 8 (Section 02.1)</p>
                                </div>

                                <div>
                                    <h4 className="font-bold text-[#172B2B] uppercase mb-1">4. Recommended Actions</h4>
                                    <ol className="space-y-1 list-decimal list-inside text-[#637575]">
                                        {taskResult.recommendations.map((rec, i) => (
                                            <li key={i}>{rec}</li>
                                        ))}
                                    </ol>
                                </div>

                                <div className="pt-4 border-t border-canvas-border flex justify-between text-slate-400 font-mono text-[10px]">
                                    <span>Lead Inspector: Abhinaya</span>
                                    <span>Status: DRAFT REVIEW</span>
                                </div>
                            </div>

                            <div className="flex justify-end gap-3 pt-2">
                                <button
                                    onClick={handleDownloadDocx}
                                    className="bg-[#087F72] hover:bg-[#066B60] text-white px-4 py-2 rounded-control text-xs font-semibold flex items-center gap-1.5 shadow-xs"
                                >
                                    <Download className="w-4 h-4" />
                                    <span>Download DOCX</span>
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
