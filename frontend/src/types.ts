export interface SourceCitation {
    filename: string;
    page: number;
    source: string;
    snippet: string;
}

export interface Attachment {
    id: string;
    filename: string;
    file_type: string;
    file_size?: number;
    url?: string;
    file_path?: string;
}

export interface ExecutionResult {
    success: boolean;
    stdout: string;
    stderr: string;
    exit_code: number;
    execution_time_sec: number;
    sandbox_type: string;
}

export interface Message {
    id: string;
    chat_id: string;
    sender: 'user' | 'assistant';
    content: string;
    model_used?: string;
    routing_badge?: string;
    source_citations?: SourceCitation[];
    code_snippet?: string;
    execution_result?: ExecutionResult;
    attachments?: Attachment[];
    docx_download_url?: string;
    docx_filename?: string;
    created_at?: string;
}

export interface Chat {
    id: string;
    title: string;
    pinned?: boolean;
    created_at: string;
    updated_at: string;
}

export interface DocumentItem {
    id: string;
    filename: string;
    file_path: string;
    file_type: string;
    file_size: number;
    page_count: number;
    doc_category: string;
    indexed: boolean;
    uploaded_at: string;
}

export interface AuditLog {
    id: number;
    timestamp: string;
    action: string;
    user_name: string;
    model_selected?: string;
    tools_used?: string;
    status: string;
    details?: string;
}

export interface AgentStep {
    step: number;
    name: string;
    details: string;
    completed: boolean;
}

export interface Finding {
    id: string;
    title: string;
    severity: 'HIGH' | 'MEDIUM' | 'LOW';
    status: string;
    ref: string;
    detail: string;
}

export interface AgentTaskResult {
    status: string;
    unit_id: string;
    steps: AgentStep[];
    summary: string;
    findings: Finding[];
    recommendations: string[];
    docx_path: string;
    docx_filename: string;
    approval_status: string;
}
