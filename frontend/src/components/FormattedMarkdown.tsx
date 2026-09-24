import React from 'react';

interface FormattedMarkdownProps {
    content: string;
}

export const FormattedMarkdown: React.FC<FormattedMarkdownProps> = ({ content }) => {
    if (!content) return null;

    // Helper to render inline markdown styles like **bold**, *italic*, `code`
    const renderInline = (text: string): React.ReactNode[] => {
        // Regex patterns to match bold (with optional spaces inside ** **), italic, and code
        // Handled carefully to support trailing spaces like "**Input **"
        const parts: React.ReactNode[] = [];
        let keyCounter = 0;

        // Tokenize text into chunks
        // Regex matches **bold**, `code`, or *italic*
        const tokenRegex = /(\*\*\s*[\s\S]*?\s*\*\*|`[^`]+`|\*[^*]+\*|_[^_]+_)/g;
        const tokens = text.split(tokenRegex);

        tokens.forEach((token) => {
            if (!token) return;

            if (token.startsWith('**') && token.endsWith('**') && token.length >= 4) {
                // Bold tag, trim internal asterisks
                const inner = token.slice(2, -2);
                parts.push(
                    <strong key={`b-${keyCounter++}`} className="font-bold text-[#172B2B]">
                        {inner}
                    </strong>
                );
            } else if (token.startsWith('`') && token.endsWith('`') && token.length >= 2) {
                // Inline code
                const inner = token.slice(1, -1);
                parts.push(
                    <code key={`c-${keyCounter++}`} className="px-1.5 py-0.5 rounded bg-[#E6F4F2] text-[#087F72] font-mono text-xs border border-[#BDE3DE]">
                        {inner}
                    </code>
                );
            } else if ((token.startsWith('*') && token.endsWith('*')) || (token.startsWith('_') && token.endsWith('_'))) {
                // Italic tag
                const inner = token.slice(1, -1);
                parts.push(
                    <em key={`i-${keyCounter++}`} className="italic text-[#334444]">
                        {inner}
                    </em>
                );
            } else {
                // Normal text chunk
                parts.push(<React.Fragment key={`t-${keyCounter++}`}>{token}</React.Fragment>);
            }
        });

        return parts;
    };

    // Split content into blocks by double linebreaks or headers
    const blocks = content.split(/\n\n+/);

    return (
        <div className="space-y-3.5 text-sm text-[#172B2B] leading-relaxed">
            {blocks.map((block, blockIdx) => {
                const lines = block.split('\n');

                // Check if block starts with heading (#, ##, ###)
                const firstLine = lines[0].trim();

                if (firstLine.startsWith('# ')) {
                    return (
                        <h1 key={blockIdx} className="text-xl font-bold text-[#172B2B] mt-4 mb-2 pb-1 border-b border-[#E1E8E8] flex items-center gap-2">
                            {renderInline(firstLine.replace(/^#\s+/, ''))}
                        </h1>
                    );
                }
                if (firstLine.startsWith('## ')) {
                    return (
                        <h2 key={blockIdx} className="text-lg font-bold text-[#172B2B] mt-3.5 mb-1.5 flex items-center gap-2">
                            {renderInline(firstLine.replace(/^##\s+/, ''))}
                        </h2>
                    );
                }
                if (firstLine.startsWith('### ')) {
                    return (
                        <h3 key={blockIdx} className="text-base font-semibold text-[#087F72] mt-3 mb-1">
                            {renderInline(firstLine.replace(/^###\s+/, ''))}
                        </h3>
                    );
                }
                if (firstLine.startsWith('#### ')) {
                    return (
                        <h4 key={blockIdx} className="text-sm font-semibold text-[#172B2B] mt-2 mb-1">
                            {renderInline(firstLine.replace(/^####\s+/, ''))}
                        </h4>
                    );
                }

                // Check if block is a horizontal rule
                if (firstLine === '---' || firstLine === '***' || firstLine === '___') {
                    return <hr key={blockIdx} className="my-3 border-t border-[#E1E8E8]" />;
                }

                // Check if lines are bullet points or numbered lists
                const isBulletList = lines.every(l => l.trim() === '' || l.trim().startsWith('- ') || l.trim().startsWith('* '));
                const isNumberedList = lines.every(l => l.trim() === '' || /^\d+\.\s/.test(l.trim()));

                if (isBulletList && lines.some(l => l.trim().length > 0)) {
                    return (
                        <ul key={blockIdx} className="list-disc pl-5 space-y-1.5 text-[#172B2B]">
                            {lines.map((line, lineIdx) => {
                                const clean = line.trim().replace(/^[-*]\s+/, '');
                                if (!clean) return null;
                                return <li key={lineIdx}>{renderInline(clean)}</li>;
                            })}
                        </ul>
                    );
                }

                if (isNumberedList && lines.some(l => l.trim().length > 0)) {
                    return (
                        <ol key={blockIdx} className="list-decimal pl-5 space-y-1.5 text-[#172B2B]">
                            {lines.map((line, lineIdx) => {
                                const clean = line.trim().replace(/^\d+\.\s+/, '');
                                if (!clean) return null;
                                return <li key={lineIdx}>{renderInline(clean)}</li>;
                            })}
                        </ol>
                    );
                }

                // Standard Paragraph
                return (
                    <div key={blockIdx} className="space-y-1">
                        {lines.map((line, lineIdx) => {
                            // Check if single line has bullet prefix inside mixed paragraph
                            const trimmed = line.trim();
                            if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
                                return (
                                    <div key={lineIdx} className="flex items-start gap-2 pl-2 my-1">
                                        <span className="text-[#087F72] font-bold">•</span>
                                        <div>{renderInline(trimmed.replace(/^[-*]\s+/, ''))}</div>
                                    </div>
                                );
                            }
                            if (/^\d+\.\s/.test(trimmed)) {
                                const match = trimmed.match(/^(\d+)\.\s+(.*)/);
                                return (
                                    <div key={lineIdx} className="flex items-start gap-2 pl-2 my-1">
                                        <span className="text-[#087F72] font-semibold font-mono text-xs mt-0.5">{match ? match[1] + '.' : ''}</span>
                                        <div>{renderInline(match ? match[2] : trimmed)}</div>
                                    </div>
                                );
                            }
                            if (trimmed.startsWith('# ')) {
                                return (
                                    <h1 key={lineIdx} className="text-xl font-bold text-[#172B2B] mt-3 mb-1">
                                        {renderInline(trimmed.replace(/^#\s+/, ''))}
                                    </h1>
                                );
                            }
                            if (trimmed.startsWith('## ')) {
                                return (
                                    <h2 key={lineIdx} className="text-lg font-bold text-[#172B2B] mt-2.5 mb-1">
                                        {renderInline(trimmed.replace(/^##\s+/, ''))}
                                    </h2>
                                );
                            }
                            if (trimmed.startsWith('### ')) {
                                return (
                                    <h3 key={lineIdx} className="text-base font-semibold text-[#087F72] mt-2 mb-1">
                                        {renderInline(trimmed.replace(/^###\s+/, ''))}
                                    </h3>
                                );
                            }

                            return (
                                <p key={lineIdx} className="leading-relaxed">
                                    {renderInline(line)}
                                </p>
                            );
                        })}
                    </div>
                );
            })}
        </div>
    );
};
export default FormattedMarkdown;
