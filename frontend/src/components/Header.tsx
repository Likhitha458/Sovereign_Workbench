import React from 'react';
import { LogOut } from 'lucide-react';

interface HeaderProps {
    title: string;
    onLogout?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ title, onLogout }) => {
    return (
        <header className="h-14 bg-white border-b border-canvas-border px-6 flex items-center justify-between select-none">
            <div className="flex items-center gap-3">
                <h1 className="font-bold text-lg text-workbench-text">{title}</h1>
            </div>

            <div className="flex items-center gap-3">
                {/* Offline On-Premise Status Badge */}
                <div className="flex items-center gap-2 bg-[#E6F4F2] text-[#087F72] border border-[#BDE3DE] px-3 py-1 rounded-full text-xs font-semibold shadow-xs">
                    <span className="w-2 h-2 rounded-full bg-[#087F72] animate-pulse"></span>
                    <span>Offline / On-Premise</span>
                </div>

                {/* Logout Action Button */}
                {onLogout && (
                    <button
                        onClick={onLogout}
                        title="Lock session / Logout"
                        className="flex items-center gap-1.5 text-xs text-[#637575] hover:text-[#172B2B] hover:bg-[#F7F9F9] border border-canvas-border px-3 py-1 rounded-md transition-colors font-medium cursor-pointer"
                    >
                        <LogOut className="w-3.5 h-3.5 text-[#087F72]" />
                        <span>Logout</span>
                    </button>
                )}
            </div>
        </header>
    );
};
export default Header;
