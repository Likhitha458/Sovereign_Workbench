import React, { useState } from 'react';
import {
    MessageSquare,
    FileText,
    BookOpen,
    Workflow,
    Settings,
    Plus,
    ShieldCheck,
    Pin,
    Edit2,
    Trash2,
    Check,
    X
} from 'lucide-react';
import { Chat } from '../types';

interface SidebarProps {
    currentView: string;
    setCurrentView: (view: string) => void;
    chats: Chat[];
    activeChatId: string | null;
    setActiveChatId: (id: string | null) => void;
    onNewChat: () => void;
    onPinChat: (chatId: string, pinned: boolean) => void;
    onRenameChat: (chatId: string, newTitle: string) => void;
    onDeleteChat: (chatId: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
    currentView,
    setCurrentView,
    chats,
    activeChatId,
    setActiveChatId,
    onNewChat,
    onPinChat,
    onRenameChat,
    onDeleteChat
}) => {
    const [editingChatId, setEditingChatId] = useState<string | null>(null);
    const [editingTitle, setEditingTitle] = useState('');

    const navItems = [
        { id: 'chats', label: 'Chats', icon: MessageSquare },
        { id: 'documents', label: 'Documents', icon: FileText },
        { id: 'knowledge-base', label: 'Knowledge Base', icon: BookOpen },
        { id: 'agent-tasks', label: 'Agent Tasks', icon: Workflow },
        { id: 'settings', label: 'Settings', icon: Settings },
    ];

    const pinnedChats = chats.filter((c) => c.pinned);
    const recentChats = chats.filter((c) => !c.pinned);

    const handleStartRename = (e: React.MouseEvent, chat: Chat) => {
        e.stopPropagation();
        setEditingChatId(chat.id);
        setEditingTitle(chat.title);
    };

    const handleSaveRename = (e: React.MouseEvent, chatId: string) => {
        e.stopPropagation();
        if (editingTitle.trim()) {
            onRenameChat(chatId, editingTitle.trim());
        }
        setEditingChatId(null);
    };

    const handleCancelRename = (e: React.MouseEvent) => {
        e.stopPropagation();
        setEditingChatId(null);
    };

    const renderChatItem = (chat: Chat) => {
        const isEditing = editingChatId === chat.id;
        const isActive = activeChatId === chat.id && currentView === 'chats';

        return (
            <div
                key={chat.id}
                onClick={() => {
                    setCurrentView('chats');
                    setActiveChatId(chat.id);
                }}
                className={`group flex items-center justify-between px-3 py-2 rounded-md text-xs transition-colors cursor-pointer ${isActive
                    ? 'bg-[#1C3333] text-white font-medium'
                    : 'text-[#8C9C9C] hover:bg-[#1A2E2E] hover:text-white'
                    }`}
            >
                {isEditing ? (
                    <div className="flex items-center gap-1.5 w-full" onClick={(e) => e.stopPropagation()}>
                        <input
                            type="text"
                            value={editingTitle}
                            onChange={(e) => setEditingTitle(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') handleSaveRename(e as any, chat.id);
                                if (e.key === 'Escape') handleCancelRename(e as any);
                            }}
                            className="bg-[#0E1A1A] border border-[#087F72] text-white text-xs px-2 py-0.5 rounded outline-none w-full"
                            autoFocus
                        />
                        <button
                            onClick={(e) => handleSaveRename(e, chat.id)}
                            className="text-emerald-400 hover:text-white p-0.5"
                            title="Save title"
                        >
                            <Check className="w-3.5 h-3.5" />
                        </button>
                        <button
                            onClick={handleCancelRename}
                            className="text-red-400 hover:text-white p-0.5"
                            title="Cancel"
                        >
                            <X className="w-3.5 h-3.5" />
                        </button>
                    </div>
                ) : (
                    <>
                        <span className="truncate flex-1 pr-2">{chat.title}</span>
                        <div className="hidden group-hover:flex items-center gap-1 shrink-0">
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onPinChat(chat.id, !chat.pinned);
                                }}
                                className={`p-1 hover:text-white rounded ${chat.pinned ? 'text-[#087F72]' : 'text-[#637575]'}`}
                                title={chat.pinned ? 'Unpin chat' : 'Pin chat'}
                            >
                                <Pin className="w-3 h-3" />
                            </button>
                            <button
                                onClick={(e) => handleStartRename(e, chat)}
                                className="p-1 text-[#637575] hover:text-white rounded"
                                title="Rename chat"
                            >
                                <Edit2 className="w-3 h-3" />
                            </button>
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onDeleteChat(chat.id);
                                }}
                                className="p-1 text-[#637575] hover:text-red-400 rounded"
                                title="Delete chat"
                            >
                                <Trash2 className="w-3 h-3" />
                            </button>
                        </div>
                    </>
                )}
            </div>
        );
    };

    return (
        <aside className="w-64 bg-[#142626] text-white flex flex-col h-screen select-none border-r border-[#1C3333]">
            {/* Brand Header */}
            <div className="p-4 flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-[#087F72] flex items-center justify-center font-bold text-white text-xl shadow-md">
                    S
                </div>
                <div>
                    <h1 className="font-semibold text-sm tracking-wide text-white leading-tight">SOVEREIGN</h1>
                    <p className="text-[11px] text-[#8C9C9C] font-mono tracking-wider">AI WORKBENCH</p>
                </div>
            </div>

            {/* New Chat Button */}
            <div className="px-3 py-2">
                <button
                    onClick={onNewChat}
                    className="w-full bg-[#087F72] hover:bg-[#066B60] text-white font-medium py-2.5 px-4 rounded-lg flex items-center gap-2 text-sm transition-colors shadow-sm"
                >
                    <Plus className="w-4 h-4" />
                    <span>New Chat</span>
                </button>
            </div>

            {/* Primary Navigation */}
            <nav className="px-3 py-2 space-y-1">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = currentView === item.id;
                    return (
                        <button
                            key={item.id}
                            onClick={() => setCurrentView(item.id)}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors font-medium ${isActive
                                ? 'bg-[#1C3333] text-white font-semibold shadow-inner'
                                : 'text-[#B0C0C0] hover:bg-[#1A2E2E] hover:text-white'
                                }`}
                        >
                            <Icon className={`w-4 h-4 ${isActive ? 'text-[#087F72]' : 'text-[#8C9C9C]'}`} />
                            <span>{item.label}</span>
                        </button>
                    );
                })}
            </nav>

            {/* Pinned & Recent Chats Section */}
            <div className="mt-2 px-3 py-2 flex-1 overflow-y-auto space-y-4">
                {/* Pinned Section */}
                {pinnedChats.length > 0 && (
                    <div>
                        <h2 className="text-[11px] font-semibold tracking-wider text-[#087F72] uppercase mb-1.5 flex items-center gap-1.5 px-1">
                            <Pin className="w-3 h-3 text-[#087F72]" />
                            <span>Pinned Chats</span>
                        </h2>
                        <div className="space-y-0.5">
                            {pinnedChats.map(renderChatItem)}
                        </div>
                    </div>
                )}

                {/* Recent Section */}
                <div>
                    <h2 className="text-[11px] font-semibold tracking-wider text-[#637575] uppercase mb-1.5 px-1">
                        Recent Chats
                    </h2>
                    <div className="space-y-0.5">
                        {recentChats.length > 0 ? (
                            recentChats.map(renderChatItem)
                        ) : (
                            <p className="text-xs text-[#637575] italic px-1">No recent chats</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Sovereign Workspace Security Badge */}
            <div className="mx-3 my-2 p-2.5 rounded-lg bg-[#0E1A1A] border border-[#1C3333] text-[11px] text-[#8C9C9C]">
                <div className="flex items-center gap-1.5 font-semibold text-white mb-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-[#087F72]" />
                    <span>Local workspace</span>
                </div>
                <p className="text-[10px] leading-tight text-[#637575]">
                    Your data stays here. 100% On-Premise.
                </p>
            </div>

            {/* User Account Footer */}
            <div className="p-3 border-t border-[#1C3333] flex items-center gap-3 bg-[#0E1A1A]">
                <div className="w-8 h-8 rounded-full bg-[#1C3333] border border-[#244040] flex items-center justify-center font-semibold text-xs text-white">
                    A
                </div>
                <div className="overflow-hidden">
                    <p className="text-xs font-semibold text-white truncate">Abhinaya</p>
                    <p className="text-[11px] text-[#637575] truncate">Engineering workspace</p>
                </div>
            </div>
        </aside>
    );
};
