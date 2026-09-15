import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ChatsView } from './views/ChatsView';
import { DocumentsView } from './views/DocumentsView';
import { KnowledgeBaseView } from './views/KnowledgeBaseView';
import { AgentTasksView } from './views/AgentTasksView';
import { SettingsView } from './views/SettingsView';
import { Chat, Message, Attachment } from './types';

export const App: React.FC = () => {
    const [currentView, setCurrentView] = useState<string>('chats');
    const [chats, setChats] = useState<Chat[]>([]);
    const [activeChatId, setActiveChatId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(false);

    useEffect(() => {
        fetchChats();
    }, []);

    useEffect(() => {
        if (activeChatId) {
            fetchMessages(activeChatId);
        } else {
            setMessages([]);
        }
    }, [activeChatId]);

    const fetchChats = async () => {
        try {
            const res = await fetch('/api/chats');
            const data = await res.json();
            setChats(data);
            if (data.length > 0 && !activeChatId) {
                setActiveChatId(data[0].id);
            }
        } catch (err) {
            console.error("Error fetching chats:", err);
        }
    };

    const fetchMessages = async (chatId: string) => {
        try {
            const res = await fetch(`/api/chats/${chatId}/messages`);
            const data = await res.json();
            setMessages(data);
        } catch (err) {
            console.error("Error fetching messages:", err);
        }
    };

    const handleNewChat = async () => {
        try {
            const res = await fetch('/api/chats', { method: 'POST' });
            const newChat = await res.json();
            setChats((prev) => [newChat, ...prev]);
            setActiveChatId(newChat.id);
            setCurrentView('chats');
            setMessages([]);
        } catch (err) {
            console.error("Error creating chat:", err);
        }
    };

    const handlePinChat = async (chatId: string, pinned: boolean) => {
        try {
            await fetch(`/api/chats/${chatId}/pin?pinned=${pinned}`, { method: 'POST' });
            fetchChats();
        } catch (err) {
            console.error("Error pinning chat:", err);
        }
    };

    const handleRenameChat = async (chatId: string, title: string) => {
        try {
            await fetch(`/api/chats/${chatId}/rename`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title })
            });
            fetchChats();
        } catch (err) {
            console.error("Error renaming chat:", err);
        }
    };

    const handleDeleteChat = async (chatId: string) => {
        try {
            await fetch(`/api/chats/${chatId}`, { method: 'DELETE' });
            setChats((prev) => prev.filter((c) => c.id !== chatId));
            if (activeChatId === chatId) {
                const remaining = chats.filter((c) => c.id !== chatId);
                setActiveChatId(remaining.length > 0 ? remaining[0].id : null);
            }
        } catch (err) {
            console.error("Error deleting chat:", err);
        }
    };

    const handleSendMessage = async (
        text: string,
        model: string,
        attachments: Attachment[]
    ) => {
        let chatId = activeChatId;
        if (!chatId) {
            // Create a new chat before sending - title will be auto-updated by backend
            const res = await fetch('/api/chats', { method: 'POST' });
            const newChat = await res.json();
            chatId = newChat.id;
            setActiveChatId(chatId);
            setChats((prev) => [newChat, ...prev]);
        }

        // Optimistic User Message shown immediately
        const tempUserMsg: Message = {
            id: Math.random().toString(),
            chat_id: chatId || 'temp-chat',
            sender: 'user',
            content: text,
            attachments
        };
        setMessages((prev) => [...prev, tempUserMsg]);
        setIsLoading(true);

        try {
            const res = await fetch('/api/chat/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chat_id: chatId,
                    message: text,
                    selected_model: model,
                    attachments
                })
            });
            const aiMsg: Message = await res.json();
            setMessages((prev) => [
                ...prev.filter(m => m.id !== tempUserMsg.id),
                tempUserMsg,
                aiMsg
            ]);

            // Refresh chats to pick up auto-generated titles from backend
            await fetchChats();

        } catch (err) {
            console.error("Chat send error:", err);
            // Show a minimal error message in the chat
            const errMsg: Message = {
                id: Math.random().toString(),
                chat_id: chatId || 'temp-chat',
                sender: 'assistant',
                content: '⚠️ Could not connect to the local AI backend. Please ensure the server is running.',
            };
            setMessages((prev) => [
                ...prev.filter(m => m.id !== tempUserMsg.id),
                tempUserMsg,
                errMsg
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const getViewTitle = () => {
        switch (currentView) {
            case 'chats': return 'Sovereign AI Workbench';
            case 'documents': return 'Documents';
            case 'knowledge-base': return 'Knowledge Base';
            case 'agent-tasks': return 'Agent Tasks';
            case 'settings': return 'Settings & Sovereignty';
            default: return 'Sovereign AI Workbench';
        }
    };

    return (
        <div className="flex h-screen w-screen overflow-hidden bg-[#F7F9F9]">
            <Sidebar
                currentView={currentView}
                setCurrentView={setCurrentView}
                chats={chats}
                activeChatId={activeChatId}
                setActiveChatId={setActiveChatId}
                onNewChat={handleNewChat}
                onPinChat={handlePinChat}
                onRenameChat={handleRenameChat}
                onDeleteChat={handleDeleteChat}
            />

            <div className="flex-1 flex flex-col h-full overflow-hidden">
                <Header title={getViewTitle()} />

                {currentView === 'chats' && (
                    <ChatsView
                        messages={messages}
                        onSendMessage={handleSendMessage}
                        onStarterClick={(prompt) => handleSendMessage(prompt, 'Auto', [])}
                        isLoading={isLoading}
                    />
                )}

                {currentView === 'documents' && <DocumentsView />}
                {currentView === 'knowledge-base' && <KnowledgeBaseView />}
                {currentView === 'agent-tasks' && <AgentTasksView />}
                {currentView === 'settings' && <SettingsView />}
            </div>
        </div>
    );
};
export default App;
