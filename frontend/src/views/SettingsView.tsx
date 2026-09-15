import React, { useState, useEffect } from 'react';
import { ShieldCheck, HardDrive, Cpu, Terminal, CheckCircle2, Lock, Activity } from 'lucide-react';
import { AuditLog } from '../types';

export const SettingsView: React.FC = () => {
    const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);

    useEffect(() => {
        fetchAuditLogs();
    }, []);

    const fetchAuditLogs = async () => {
        try {
            const res = await fetch('/api/audit-logs');
            const data = await res.json();
            setAuditLogs(data);
        } catch (err) {
            console.error("Audit log error:", err);
        }
    };

    return (
        <div className="flex-1 p-6 md:p-10 bg-[#F7F9F9] overflow-y-auto">
            <div className="max-w-5xl mx-auto space-y-6">
                <div>
                    <h1 className="text-2xl font-bold text-[#172B2B]">Settings</h1>
                    <p className="text-xs text-[#637575] mt-1">
                        Manage local models, security, audit logs, and runtime readiness.
                    </p>
                </div>

                {/* Sovereignty Panel Cards (Matching Figma 05 Settings Top Panel) */}
                <div className="bg-white p-6 rounded-card border border-canvas-border space-y-4 shadow-xs">
                    <div className="flex items-center justify-between border-b border-canvas-border pb-3">
                        <div className="flex items-center gap-2">
                            <ShieldCheck className="w-5 h-5 text-[#087F72]" />
                            <h3 className="font-bold text-sm text-[#172B2B]">Local AI & Sovereignty Status</h3>
                        </div>
                        <span className="bg-[#E6F4F2] text-[#087F72] font-semibold text-xs px-3 py-1 rounded-full border border-[#BDE3DE]">
                            100% Offline / On-Premise
                        </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-1">
                        <div className="p-3 bg-[#F7F9F9] border border-canvas-border rounded-lg space-y-1">
                            <span className="text-[11px] font-semibold text-[#637575] uppercase">External AI APIs</span>
                            <p className="text-lg font-bold text-emerald-700 flex items-center gap-1">
                                <Lock className="w-4 h-4 text-emerald-600" />
                                <span>0 (Blocked)</span>
                            </p>
                        </div>

                        <div className="p-3 bg-[#F7F9F9] border border-canvas-border rounded-lg space-y-1">
                            <span className="text-[11px] font-semibold text-[#637575] uppercase">Internet Dependency</span>
                            <p className="text-lg font-bold text-emerald-700 flex items-center gap-1">
                                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                                <span>None (Offline)</span>
                            </p>
                        </div>

                        <div className="p-3 bg-[#F7F9F9] border border-canvas-border rounded-lg space-y-1">
                            <span className="text-[11px] font-semibold text-[#637575] uppercase">Vector Database</span>
                            <p className="text-lg font-bold text-[#172B2B]">Local ChromaDB</p>
                        </div>

                        <div className="p-3 bg-[#F7F9F9] border border-canvas-border rounded-lg space-y-1">
                            <span className="text-[11px] font-semibold text-[#637575] uppercase">Code Sandbox</span>
                            <p className="text-lg font-bold text-[#172B2B]">Docker Container</p>
                        </div>
                    </div>
                </div>

                {/* Local Models Table */}
                <div className="bg-white p-6 rounded-card border border-canvas-border space-y-4 shadow-xs">
                    <h3 className="font-bold text-sm text-[#172B2B]">Local AI Models</h3>

                    <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 bg-[#F7F9F9] border border-canvas-border rounded-lg text-xs">
                            <div className="flex items-center gap-3">
                                <Cpu className="w-4 h-4 text-[#087F72]" />
                                <div>
                                    <h4 className="font-bold text-[#172B2B]">Qwen3</h4>
                                    <p className="text-[#637575]">General reasoning, regulation analysis, and RAG answers</p>
                                </div>
                            </div>
                            <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded">
                                ✓ Ready
                            </span>
                        </div>

                        <div className="flex items-center justify-between p-3 bg-[#F7F9F9] border border-canvas-border rounded-lg text-xs">
                            <div className="flex items-center gap-3">
                                <Cpu className="w-4 h-4 text-[#087F72]" />
                                <div>
                                    <h4 className="font-bold text-[#172B2B]">Qwen2.5-VL</h4>
                                    <p className="text-[#637575]">Multimodal vision, equipment photo inspection, and P&ID diagrams</p>
                                </div>
                            </div>
                            <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded">
                                ✓ Ready
                            </span>
                        </div>

                        <div className="flex items-center justify-between p-3 bg-[#F7F9F9] border border-canvas-border rounded-lg text-xs">
                            <div className="flex items-center gap-3">
                                <Terminal className="w-4 h-4 text-[#087F72]" />
                                <div>
                                    <h4 className="font-bold text-[#172B2B]">Qwen3-Coder</h4>
                                    <p className="text-[#637575]">Code generation, math, data processing, and script creation</p>
                                </div>
                            </div>
                            <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded">
                                ✓ Ready
                            </span>
                        </div>
                    </div>
                </div>

                {/* Audit Log Table */}
                <div className="bg-white p-6 rounded-card border border-canvas-border space-y-4 shadow-xs">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Activity className="w-4 h-4 text-[#087F72]" />
                            <h3 className="font-bold text-sm text-[#172B2B]">System Audit Logs</h3>
                        </div>
                        <button
                            onClick={fetchAuditLogs}
                            className="text-xs text-[#087F72] hover:underline font-semibold"
                        >
                            Refresh Logs
                        </button>
                    </div>

                    <div className="overflow-x-auto border border-canvas-border rounded-lg">
                        <table className="w-full text-left border-collapse text-xs">
                            <thead>
                                <tr className="bg-[#F7F9F9] border-b border-canvas-border text-[11px] font-semibold text-[#637575] uppercase">
                                    <th className="py-2.5 px-3">Timestamp</th>
                                    <th className="py-2.5 px-3">Action</th>
                                    <th className="py-2.5 px-3">User</th>
                                    <th className="py-2.5 px-3">Tool/Engine</th>
                                    <th className="py-2.5 px-3">Details</th>
                                    <th className="py-2.5 px-3">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-canvas-border font-mono text-[11px]">
                                {auditLogs.length > 0 ? (
                                    auditLogs.map((log) => (
                                        <tr key={log.id} className="hover:bg-[#F7F9F9]">
                                            <td className="py-2 px-3 text-[#637575] whitespace-nowrap">
                                                {new Date(log.timestamp).toLocaleTimeString()}
                                            </td>
                                            <td className="py-2 px-3 font-semibold text-[#172B2B]">{log.action}</td>
                                            <td className="py-2 px-3 text-[#637575]">{log.user_name}</td>
                                            <td className="py-2 px-3 text-[#087F72]">{log.tools_used || 'Local Engine'}</td>
                                            <td className="py-2 px-3 text-[#637575] max-w-xs truncate">{log.details}</td>
                                            <td className="py-2 px-3">
                                                <span className="text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded font-bold text-[10px]">
                                                    {log.status}
                                                </span>
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    /* Demo Fallback Row */
                                    <tr>
                                        <td className="py-2.5 px-3 text-[#637575]">12 Sep 2026 20:00</td>
                                        <td className="py-2.5 px-3 font-semibold text-[#172B2B]">MODEL_ROUTER_AUTO</td>
                                        <td className="py-2.5 px-3 text-[#637575]">Abhinaya</td>
                                        <td className="py-2.5 px-3 text-[#087F72]">Qwen3 Engine</td>
                                        <td className="py-2.5 px-3 text-[#637575]">Auto routed query to Qwen3</td>
                                        <td className="py-2.5 px-3">
                                            <span className="text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded font-bold text-[10px]">
                                                SUCCESS
                                            </span>
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>
    );
};
