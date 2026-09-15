import React, { useState, useEffect } from 'react';
import { FileText, Upload, Trash2, RefreshCw, Search, CheckCircle, Clock } from 'lucide-react';
import { DocumentItem } from '../types';

export const DocumentsView: React.FC = () => {
    const [documents, setDocuments] = useState<DocumentItem[]>([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [isUploading, setIsUploading] = useState(false);

    useEffect(() => {
        fetchDocuments();
    }, []);

    const fetchDocuments = async () => {
        try {
            const res = await fetch('/api/documents');
            const data = await res.json();
            setDocuments(data);
        } catch (err) {
            console.error("Error fetching documents:", err);
        }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setIsUploading(true);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('doc_category', 'general');

        try {
            await fetch('/api/documents/upload', {
                method: 'POST',
                body: formData,
            });
            fetchDocuments();
        } catch (err) {
            console.error("Error uploading file:", err);
        } finally {
            setIsUploading(false);
        }
    };

    const handleDelete = async (docId: string) => {
        try {
            await fetch(`/api/documents/${docId}`, { method: 'DELETE' });
            fetchDocuments();
        } catch (err) {
            console.error("Error deleting doc:", err);
        }
    };

    const filteredDocs = documents.filter((doc) =>
        doc.filename.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="flex-1 p-6 md:p-10 bg-[#F7F9F9] overflow-y-auto">
            <div className="max-w-5xl mx-auto space-y-6">
                {/* Header Title + Upload Button */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-[#172B2B]">Documents</h1>
                        <p className="text-xs text-[#637575] mt-1">
                            Upload and manage files stored in your local workspace.
                        </p>
                    </div>

                    <label className="bg-[#087F72] hover:bg-[#066B60] text-white px-4 py-2 rounded-control text-xs font-semibold flex items-center gap-2 cursor-pointer transition-colors shadow-xs">
                        <Upload className="w-4 h-4" />
                        <span>{isUploading ? 'Indexing...' : 'Upload Document'}</span>
                        <input type="file" onChange={handleFileUpload} className="hidden" accept=".pdf,.docx,.txt" />
                    </label>
                </div>

                {/* Drop Zone Box (Figma Kit 02 Documents style) */}
                <div className="bg-white border-2 border-dashed border-canvas-border p-8 rounded-card text-center flex flex-col items-center justify-center">
                    <Upload className="w-8 h-8 text-[#087F72] mb-2" />
                    <h3 className="font-semibold text-sm text-[#172B2B]">Drop documents here, or browse files</h3>
                    <p className="text-xs text-[#637575] mt-1">Files are processed locally and stored in your workspace (PDF, DOCX, TXT, Images).</p>
                </div>

                {/* Search & Filter Bar */}
                <div className="flex items-center gap-4 bg-white p-3 rounded-card border border-canvas-border">
                    <div className="flex-1 relative">
                        <Search className="w-4 h-4 text-[#8C9C9C] absolute left-3 top-2.5" />
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            placeholder="Search documents..."
                            className="w-full pl-9 pr-4 py-1.5 bg-[#F7F9F9] border border-canvas-border rounded-control text-xs outline-none focus:border-[#087F72]"
                        />
                    </div>
                </div>

                {/* Documents Table */}
                <div className="bg-white rounded-card border border-canvas-border overflow-hidden shadow-xs">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-[#F7F9F9] border-b border-canvas-border text-[11px] font-semibold text-[#637575] uppercase">
                                <th className="py-3 px-4">File Name</th>
                                <th className="py-3 px-4">Type</th>
                                <th className="py-3 px-4">Status</th>
                                <th className="py-3 px-4">Date</th>
                                <th className="py-3 px-4 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-canvas-border text-xs">
                            {filteredDocs.length > 0 ? (
                                filteredDocs.map((doc) => (
                                    <tr key={doc.id} className="hover:bg-[#F7F9F9] transition-colors">
                                        <td className="py-3 px-4 font-medium text-[#172B2B] flex items-center gap-2">
                                            <FileText className="w-4 h-4 text-[#087F72]" />
                                            <span>{doc.filename}</span>
                                        </td>
                                        <td className="py-3 px-4 font-mono text-[#637575]">
                                            {doc.filename.split('.').pop()?.toUpperCase()}
                                        </td>
                                        <td className="py-3 px-4">
                                            {doc.indexed ? (
                                                <span className="inline-flex items-center gap-1 text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-semibold text-[11px]">
                                                    <CheckCircle className="w-3 h-3 text-emerald-600" />
                                                    <span>Indexed</span>
                                                </span>
                                            ) : (
                                                <span className="inline-flex items-center gap-1 text-amber-700 bg-amber-50 px-2 py-0.5 rounded font-semibold text-[11px]">
                                                    <Clock className="w-3 h-3 text-amber-600" />
                                                    <span>Processing</span>
                                                </span>
                                            )}
                                        </td>
                                        <td className="py-3 px-4 text-[#637575]">
                                            {new Date(doc.uploaded_at).toLocaleDateString()}
                                        </td>
                                        <td className="py-3 px-4 text-right">
                                            <button
                                                onClick={() => handleDelete(doc.id)}
                                                className="text-[#637575] hover:text-red-600 p-1 rounded"
                                                title="Delete"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                /* Default Demo Rows matching Figma kit 02 Documents */
                                <>
                                    <tr className="hover:bg-[#F7F9F9]">
                                        <td className="py-3 px-4 font-medium text-[#172B2B] flex items-center gap-2">
                                            <FileText className="w-4 h-4 text-[#087F72]" />
                                            <span>Inspection_Report_Unit04.pdf</span>
                                        </td>
                                        <td className="py-3 px-4 font-mono text-[#637575]">PDF</td>
                                        <td className="py-3 px-4">
                                            <span className="inline-flex items-center gap-1 text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-semibold text-[11px]">
                                                <CheckCircle className="w-3 h-3 text-emerald-600" />
                                                <span>Indexed</span>
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-[#637575]">12 Sep 2026</td>
                                        <td className="py-3 px-4 text-right text-[#637575]">Ready</td>
                                    </tr>

                                    <tr className="hover:bg-[#F7F9F9]">
                                        <td className="py-3 px-4 font-medium text-[#172B2B] flex items-center gap-2">
                                            <FileText className="w-4 h-4 text-[#087F72]" />
                                            <span>Safety_Regulation_2025.pdf</span>
                                        </td>
                                        <td className="py-3 px-4 font-mono text-[#637575]">PDF</td>
                                        <td className="py-3 px-4">
                                            <span className="inline-flex items-center gap-1 text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-semibold text-[11px]">
                                                <CheckCircle className="w-3 h-3 text-emerald-600" />
                                                <span>Indexed</span>
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-[#637575]">12 Sep 2026</td>
                                        <td className="py-3 px-4 text-right text-[#637575]">Ready</td>
                                    </tr>

                                    <tr className="hover:bg-[#F7F9F9]">
                                        <td className="py-3 px-4 font-medium text-[#172B2B] flex items-center gap-2">
                                            <FileText className="w-4 h-4 text-[#087F72]" />
                                            <span>Maintenance_SOP.pdf</span>
                                        </td>
                                        <td className="py-3 px-4 font-mono text-[#637575]">PDF</td>
                                        <td className="py-3 px-4">
                                            <span className="inline-flex items-center gap-1 text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-semibold text-[11px]">
                                                <CheckCircle className="w-3 h-3 text-emerald-600" />
                                                <span>Indexed</span>
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-[#637575]">12 Sep 2026</td>
                                        <td className="py-3 px-4 text-right text-[#637575]">Ready</td>
                                    </tr>
                                </>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};
