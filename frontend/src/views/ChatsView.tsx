import React, { useState, useRef, useEffect } from 'react';
import {
    Send,
    Paperclip,
    Image as ImageIcon,
    ChevronDown,
    FileText,
    BookOpen,
    Code,
    Play,
    CheckCircle,
    AlertTriangle,
    ExternalLink,
    Bot,
    User,
    Sparkles,
    Loader2
} from 'lucide-react';
import { Message, Attachment, SourceCitation, ExecutionResult } from '../types';

interface ChatsViewProps {
    messages: Message[];
    onSendMessage: (text: string, model: string, attachments: Attachment[]) => Promise<void>;
    onStarterClick: (prompt: string) => void;
    isLoading: boolean;
}

export const ChatsView: React.FC<ChatsViewProps> = ({
    messages,
    onSendMessage,
    onStarterClick,
    isLoading,
}) => {
    const [inputText, setInputText] = useState('');
    const [selectedModel, setSelectedModel] = useState('Auto');
    const [showModelMenu, setShowModelMenu] = useState(false);
    const [attachments, setAttachments] = useState<Attachment[]>([]);
    const [executingCodeId, setExecutingCodeId] = useState<string | null>(null);
    const [codeExecutionResults, setCodeExecutionResults] = useState<Record<string, ExecutionResult>>({});

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const imageInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading]);

    const handleSend = () => {
        if (!inputText.trim() && attachments.length === 0) return;
        onSendMessage(inputText, selectedModel, attachments);
        setInputText('');
        setAttachments([]);
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>, isImage: boolean = false) => {
        const files = e.target.files;
        if (!files || files.length === 0) return;

        for (let i = 0; i < files.length; i++) {
            const f = files[i];
            // Determine the correct MIME type
            const detectedType = f.type || (isImage ? 'image/png' : 'application/pdf');

            // Optimistic UI: show attachment chip immediately so user sees it at once
            const tempId = `temp-${Math.random().toString(36).substring(7)}`;
            const tempAttachment: Attachment = {
                id: tempId,
                filename: f.name,
                file_type: detectedType,
                file_size: f.size,
                file_path: ''
            };
            setAttachments((prev) => [...prev, tempAttachment]);

            const formData = new FormData();
            formData.append('file', f);
            formData.append('doc_category', isImage ? 'image' : 'general');

            try {
                const res = await fetch('/api/documents/upload', {
                    method: 'POST',
                    body: formData
                });
                if (res.ok) {
                    const data = await res.json();
                    // Replace temp attachment with real one from backend
                    setAttachments((prev) =>
                        prev.map((att) =>
                            att.id === tempId
                                ? {
                                    id: data.id,
                                    filename: f.name,
                                    file_type: detectedType,
                                    file_size: f.size,
                                    file_path: data.file_path || ''
                                }
                                : att
                        )
                    );
                }
            } catch (err) {
                console.error("Attachment upload error:", err);
                // Keep the temp attachment (will still be sent with filename for fallback path lookup)
            }
        }
        // Reset the input so same file can be re-uploaded
        e.target.value = '';
    };

    const runCodeInSandbox = async (messageId: string, codeSnippet: string) => {
        setExecutingCodeId(messageId);
        try {
            const res = await fetch('/api/sandbox/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: codeSnippet })
            });
            const data: ExecutionResult = await res.json();
            setCodeExecutionResults((prev) => ({ ...prev, [messageId]: data }));
        } catch (err) {
            console.error("Code sandbox error:", err);
        } finally {
            setExecutingCodeId(null);
        }
    };

    const modelOptions = [
        { id: 'Auto', label: 'Auto (Default)', desc: 'Selects best model for task' },
        { id: 'Qwen3 — General', label: 'Qwen3', desc: 'General & Reasoning' },
        { id: 'Qwen2.5-VL — Vision', label: 'Qwen2.5-VL', desc: 'Vision & Documents' },
        { id: 'Qwen3-Coder — Coding', label: 'Qwen3-Coder', desc: 'Coding & Calculations' },
    ];

    return (
        <div className="flex-1 flex flex-col h-[calc(100vh-3.5rem)] bg-[#F7F9F9] relative overflow-hidden">
            {/* Hidden File Inputs */}
            <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                onChange={(e) => handleFileUpload(e, false)}
                accept=".pdf,.docx,.txt"
            />
            <input
                type="file"
                ref={imageInputRef}
                className="hidden"
                onChange={(e) => handleFileUpload(e, true)}
                accept="image/*"
            />

            {/* Main Chat Area */}
            <div className="flex-1 overflow-y-auto px-4 py-6 md:px-12 lg:px-24">
                {messages.length === 0 ? (
                    /* Welcome Screen matching Figma Kit 01 Chat Welcome */
                    <div className="max-w-3xl mx-auto pt-8 pb-12 flex flex-col items-start">
                        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E6F4F2] text-[#087F72] text-[11px] font-bold tracking-wider uppercase mb-6 border border-[#BDE3DE]">
                            <Sparkles className="w-3 h-3" />
                            <span>Private Intelligence</span>
                        </div>

                        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-[#172B2B] mb-3 leading-tight">
                            Your work. Your knowledge.<br />
                            <span className="text-[#087F72]">Your infrastructure.</span>
                        </h1>

                        <p className="text-base text-[#637575] max-w-xl mb-10 leading-relaxed">
                            A private AI workspace for engineering and industrial decisions.
                            Ask, analyze, and create — with your data kept on-premise.
                        </p>

                        {/* 3 Quick Action Starter Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
                            <button
                                onClick={() => onStarterClick("Review unit 04 inspection report and summarize safety findings.")}
                                className="bg-white p-5 rounded-card border border-canvas-border hover:border-[#087F72] hover:shadow-md transition-all text-left group flex flex-col justify-between h-40"
                            >
                                <div>
                                    <FileText className="w-6 h-6 text-[#087F72] mb-3 group-hover:scale-110 transition-transform" />
                                    <h3 className="font-semibold text-sm text-[#172B2B] mb-1">Review an inspection</h3>
                                    <p className="text-xs text-[#637575] leading-relaxed">
                                        Turn a report into findings and a draft approval note.
                                    </p>
                                </div>
                            </button>

                            <button
                                onClick={() => onStarterClick("What are the mandatory inspection interval regulations for pressure valves?")}
                                className="bg-white p-5 rounded-card border border-canvas-border hover:border-[#087F72] hover:shadow-md transition-all text-left group flex flex-col justify-between h-40"
                            >
                                <div>
                                    <BookOpen className="w-6 h-6 text-[#087F72] mb-3 group-hover:scale-110 transition-transform" />
                                    <h3 className="font-semibold text-sm text-[#172B2B] mb-1">Ask your documents</h3>
                                    <p className="text-xs text-[#637575] leading-relaxed">
                                        Find answers grounded in your regulations and SOPs.
                                    </p>
                                </div>
                            </button>

                            <button
                                onClick={() => onStarterClick("Write Python code to calculate pressure drop using Darcy-Weisbach equation.")}
                                className="bg-white p-5 rounded-card border border-canvas-border hover:border-[#087F72] hover:shadow-md transition-all text-left group flex flex-col justify-between h-40"
                            >
                                <div>
                                    <Code className="w-6 h-6 text-[#087F72] mb-3 group-hover:scale-110 transition-transform" />
                                    <h3 className="font-semibold text-sm text-[#172B2B] mb-1">Build a calculation</h3>
                                    <p className="text-xs text-[#637575] leading-relaxed">
                                        Write and run Python for an engineering task.
                                    </p>
                                </div>
                            </button>
                        </div>
                    </div>
                ) : (
                    /* Active Chat Messages Stream */
                    <div className="max-w-3xl mx-auto space-y-6">
                        {messages.map((msg) => (
                            <div key={msg.id} className="space-y-3">
                                {msg.sender === 'user' ? (
                                    /* User Message Bubble */
                                    <div className="flex justify-end">
                                        <div className="bg-white border border-canvas-border text-[#172B2B] px-5 py-3.5 rounded-2xl rounded-tr-xs shadow-xs max-w-2xl text-sm leading-relaxed">
                                            {msg.attachments && msg.attachments.length > 0 && (
                                                <div className="flex flex-wrap gap-2 mb-2">
                                                    {msg.attachments.map((att) => (
                                                        <div key={att.id} className="flex items-center gap-1.5 bg-[#F7F9F9] border border-canvas-border px-2.5 py-1 rounded-md text-xs font-mono text-[#637575]">
                                                            <FileText className="w-3.5 h-3.5 text-[#087F72]" />
                                                            <span>{att.filename}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                            <p className="whitespace-pre-wrap">{msg.content}</p>
                                        </div>
                                    </div>
                                ) : (
                                    /* Assistant Response Message */
                                    <div className="flex items-start gap-3">
                                        <div className="w-8 h-8 rounded-lg bg-[#087F72] text-white flex items-center justify-center font-bold text-xs shrink-0 mt-1 shadow-xs">
                                            S
                                        </div>

                                        <div className="flex-1 space-y-3">
                                            {/* Routing Badge matching Figma Kit */}
                                            {msg.routing_badge && (
                                                <div className="inline-flex items-center gap-1.5 bg-[#E6F4F2] text-[#087F72] px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold border border-[#BDE3DE]">
                                                    <span>{msg.routing_badge}</span>
                                                </div>
                                            )}

                                            {/* Main Message Text */}
                                            <div className="bg-white border border-canvas-border p-5 rounded-card shadow-xs text-sm text-[#172B2B] leading-relaxed space-y-4">
                                                <div className="prose prose-sm max-w-none space-y-2">
                                                    {msg.content.split('\n\n').map((para, i) => (
                                                        <p key={i} className="whitespace-pre-wrap">{para}</p>
                                                    ))}
                                                </div>

                                                {/* Source Citations Box */}
                                                {msg.source_citations && msg.source_citations.length > 0 && (
                                                    <div className="mt-4 pt-3 border-t border-canvas-border">
                                                        <h4 className="text-xs font-semibold text-[#637575] uppercase tracking-wider mb-2 flex items-center gap-1.5">
                                                            <BookOpen className="w-3.5 h-3.5 text-[#087F72]" />
                                                            <span>Source References</span>
                                                        </h4>
                                                        <div className="grid grid-cols-1 gap-2">
                                                            {msg.source_citations.map((cite, idx) => (
                                                                <div key={idx} className="bg-[#F7F9F9] border border-canvas-border p-2.5 rounded-md text-xs">
                                                                    <div className="flex items-center justify-between font-mono font-semibold text-[#087F72] mb-1">
                                                                        <span>{cite.source}</span>
                                                                        <ExternalLink className="w-3 h-3 text-[#637575]" />
                                                                    </div>
                                                                    <p className="text-[#637575] italic line-clamp-2">"{cite.snippet}"</p>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}

                                                {/* Downloadable Autonomous Word Document (.docx) Button */}
                                                {msg.docx_download_url && (
                                                    <div className="mt-4 p-3.5 bg-[#E6F4F2] border border-[#BDE3DE] rounded-lg flex items-center justify-between">
                                                        <div className="flex items-center gap-2.5">
                                                            <FileText className="w-5 h-5 text-[#087F72]" />
                                                            <div>
                                                                <p className="text-xs font-semibold text-[#172B2B]">
                                                                    {msg.docx_filename || 'Autonomous_Report.docx'}
                                                                </p>
                                                                <p className="text-[10px] text-[#637575]">
                                                                    Official Sovereign Word Document
                                                                </p>
                                                            </div>
                                                        </div>
                                                        <a
                                                            href={msg.docx_download_url}
                                                            download={msg.docx_filename || 'Autonomous_Report.docx'}
                                                            className="bg-[#087F72] hover:bg-[#066B60] text-white text-xs font-semibold px-3.5 py-1.5 rounded flex items-center gap-1.5 transition-colors shadow-xs"
                                                        >
                                                            <ExternalLink className="w-3.5 h-3.5" />
                                                            <span>Download .docx</span>
                                                        </a>
                                                    </div>
                                                )}

                                                {/* Formatted Code Block + One-Click Sandbox Runner */}
                                                {msg.code_snippet && (
                                                    <div className="mt-4 bg-[#142626] rounded-lg overflow-hidden border border-[#244040]">
                                                        <div className="bg-[#0E1A1A] px-4 py-2 flex items-center justify-between border-b border-[#1C3333]">
                                                            <span className="text-xs font-mono text-[#8C9C9C]">PYTHON CODE</span>
                                                            <button
                                                                onClick={() => runCodeInSandbox(msg.id, msg.code_snippet!)}
                                                                disabled={executingCodeId === msg.id}
                                                                className="bg-[#087F72] hover:bg-[#066B60] text-white px-3 py-1 rounded text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
                                                            >
                                                                {executingCodeId === msg.id ? (
                                                                    <>
                                                                        <Loader2 className="w-3 h-3 animate-spin" />
                                                                        <span>Executing...</span>
                                                                    </>
                                                                ) : (
                                                                    <>
                                                                        <Play className="w-3 h-3" />
                                                                        <span>Run Code</span>
                                                                    </>
                                                                )}
                                                            </button>
                                                        </div>
                                                        <pre className="p-4 text-xs font-mono text-emerald-400 overflow-x-auto">
                                                            <code>{msg.code_snippet}</code>
                                                        </pre>

                                                        {/* Execution Output Result Panel */}
                                                        {codeExecutionResults[msg.id] && (
                                                            <div className="bg-[#0E1A1A] border-t border-[#1C3333] p-3 text-xs font-mono">
                                                                <div className="flex items-center justify-between mb-1.5 text-[#8C9C9C]">
                                                                    <span className="flex items-center gap-1.5">
                                                                        <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                                                                        <span>{codeExecutionResults[msg.id].sandbox_type}</span>
                                                                    </span>
                                                                    <span>{codeExecutionResults[msg.id].execution_time_sec}s</span>
                                                                </div>
                                                                {codeExecutionResults[msg.id].stdout && (
                                                                    <div className="text-white whitespace-pre-wrap bg-[#142626] p-2 rounded border border-[#1C3333]">
                                                                        {codeExecutionResults[msg.id].stdout}
                                                                    </div>
                                                                )}
                                                                {codeExecutionResults[msg.id].stderr && (
                                                                    <div className="text-red-400 whitespace-pre-wrap bg-[#142626] p-2 rounded border border-red-950 mt-1">
                                                                        {codeExecutionResults[msg.id].stderr}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        )}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}

                        {/* Thinking / Loading indicator */}
                        {isLoading && (
                            <div className="flex items-start gap-3">
                                <div className="w-8 h-8 rounded-lg bg-[#087F72] text-white flex items-center justify-center font-bold text-xs shrink-0 mt-1">
                                    S
                                </div>
                                <div className="bg-white border border-canvas-border px-4 py-3 rounded-card text-xs text-[#637575] flex items-center gap-2">
                                    <Loader2 className="w-4 h-4 text-[#087F72] animate-spin" />
                                    <span>Sovereign local reasoning in progress...</span>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            {/* Input Form Bar (Matching Figma Kit 01 Chat Input) */}
            <div className="p-4 md:px-12 lg:px-24 bg-[#F7F9F9] border-t border-canvas-border">
                <div className="max-w-3xl mx-auto bg-white border border-canvas-border rounded-xl p-3 shadow-sm relative">

                    {/* Attachment Chips Display */}
                    {attachments.length > 0 && (
                        <div className="flex flex-wrap gap-2 mb-2 pb-2 border-b border-canvas-border">
                            {attachments.map((att) => (
                                <div key={att.id} className="flex items-center gap-1.5 bg-[#E6F4F2] text-[#087F72] px-2.5 py-1 rounded-md text-xs font-mono font-medium">
                                    <FileText className="w-3.5 h-3.5" />
                                    <span>{att.filename}</span>
                                    <button
                                        onClick={() => setAttachments(attachments.filter(a => a.id !== att.id))}
                                        className="ml-1 hover:text-red-600"
                                    >
                                        ×
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    <textarea
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSend();
                            }
                        }}
                        placeholder="Ask a question about your industrial work..."
                        className="w-full bg-transparent border-none outline-none resize-none text-sm text-[#172B2B] placeholder-[#8C9C9C] min-h-[44px] max-h-32"
                        rows={1}
                    />

                    <div className="flex items-center justify-between pt-2 border-t border-canvas-border/50">
                        <div className="flex items-center gap-2">
                            <button
                                type="button"
                                onClick={() => fileInputRef.current?.click()}
                                className="flex items-center gap-1.5 text-xs text-[#637575] hover:text-[#172B2B] px-2.5 py-1.5 rounded-md hover:bg-[#F7F9F9] transition-colors"
                            >
                                <Paperclip className="w-4 h-4 text-[#637575]" />
                                <span>Upload file</span>
                            </button>

                            <button
                                type="button"
                                onClick={() => imageInputRef.current?.click()}
                                className="flex items-center gap-1.5 text-xs text-[#637575] hover:text-[#172B2B] px-2.5 py-1.5 rounded-md hover:bg-[#F7F9F9] transition-colors"
                            >
                                <ImageIcon className="w-4 h-4 text-[#637575]" />
                                <span>Upload image</span>
                            </button>
                        </div>

                        <div className="flex items-center gap-2 relative">
                            {/* Model Selector Dropdown matching Figma 01d Chat Model Menu */}
                            <div className="relative">
                                <button
                                    type="button"
                                    onClick={() => setShowModelMenu(!showModelMenu)}
                                    className="flex items-center gap-1.5 border border-canvas-border px-3 py-1.5 rounded-control text-xs font-semibold text-[#172B2B] hover:bg-[#F7F9F9] transition-colors"
                                >
                                    <span>{selectedModel.split(' ')[0]}</span>
                                    <ChevronDown className="w-3.5 h-3.5 text-[#637575]" />
                                </button>

                                {showModelMenu && (
                                    <div className="absolute right-0 bottom-full mb-2 w-64 bg-white border border-canvas-border rounded-xl shadow-lg p-2 z-50">
                                        <p className="text-[11px] font-semibold text-[#637575] uppercase px-2 py-1 border-b border-canvas-border mb-1">
                                            Choose model
                                        </p>
                                        {modelOptions.map((opt) => (
                                            <button
                                                key={opt.id}
                                                onClick={() => {
                                                    setSelectedModel(opt.id);
                                                    setShowModelMenu(false);
                                                }}
                                                className={`w-full text-left p-2 rounded-lg text-xs transition-colors flex flex-col ${selectedModel === opt.id ? 'bg-[#E6F4F2] text-[#087F72] font-semibold' : 'hover:bg-[#F7F9F9] text-[#172B2B]'
                                                    }`}
                                            >
                                                <span className="font-semibold">{opt.label}</span>
                                                <span className="text-[10px] text-[#637575]">{opt.desc}</span>
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>

                            <button
                                type="button"
                                onClick={handleSend}
                                disabled={!inputText.trim() && attachments.length === 0}
                                className="bg-[#087F72] hover:bg-[#066B60] text-white px-4 py-1.5 rounded-control text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50 shadow-xs"
                            >
                                <span>Send</span>
                                <Send className="w-3.5 h-3.5" />
                            </button>
                        </div>
                    </div>
                </div>

                <p className="text-[11px] text-center text-[#8C9C9C] mt-2">
                    Responses run locally. Verify source references before making decisions.
                </p>
            </div>
        </div>
    );
};
