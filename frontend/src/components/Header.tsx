import React from 'react';
import { ShieldCheck, HardDrive } from 'lucide-react';

interface HeaderProps {
    title: string;
}

export const Header: React.FC<HeaderProps> = ({ title }) => {
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
            </div>
        </header>
    );
};
