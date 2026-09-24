import React, { useState } from 'react';
import {
    Shield,
    Star,
    Lock,
    ShieldCheck,
    Cpu,
    Building2,
    User,
    Eye,
    EyeOff,
    ArrowRight,
    Info,
    Key,
    Check
} from 'lucide-react';

interface LoginViewProps {
    onLoginSuccess: () => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onLoginSuccess }) => {
    const [organization, setOrganization] = useState('');
    const [userId, setUserId] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');
    const [copiedDemo, setCopiedDemo] = useState(false);

    const DEMO_ORG = "DEFENSE-UNIT-01";
    const DEMO_USER = "operator-704";
    const DEMO_PASS = "SovereignPass2026!";

    const handleFillDemo = () => {
        setOrganization(DEMO_ORG);
        setUserId(DEMO_USER);
        setPassword(DEMO_PASS);
        setErrorMsg('');
        setCopiedDemo(true);
        setTimeout(() => setCopiedDemo(false), 2000);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setErrorMsg('');

        if (!organization.trim() || !userId.trim() || !password.trim()) {
            setErrorMsg('Please fill in all authorization fields or use demo credentials.');
            return;
        }

        setIsSubmitting(true);
        setTimeout(() => {
            setIsSubmitting(false);
            onLoginSuccess();
        }, 600);
    };

    return (
        <div className="flex flex-col lg:flex-row min-h-screen w-screen bg-[#071313] text-white overflow-x-hidden font-sans select-none">
            {/* ── LEFT PANEL: Branding & Mission Overview ─────────────────────────── */}
            <div className="lg:w-1/2 p-8 lg:p-14 flex flex-col justify-between relative bg-gradient-to-b from-[#091C1C] via-[#061515] to-[#040D0D] border-r border-[#152E2E]/60 overflow-hidden">
                {/* Background Tactical Grid & Silhouette Glow */}
                <div className="absolute inset-0 bg-[radial-gradient(#153838_1px,transparent_1px)] [background-size:24px_24px] opacity-25 pointer-events-none" />

                {/* Military silhouette background overlay effect */}
                <div className="absolute bottom-0 left-0 right-0 h-72 bg-gradient-to-t from-[#040D0D] via-transparent to-transparent z-0 pointer-events-none" />
                <div
                    className="absolute inset-0 z-0 opacity-15 pointer-events-none bg-cover bg-bottom mix-blend-overlay"
                    style={{
                        backgroundImage: `radial-gradient(circle at 30% 70%, rgba(8,127,114,0.35) 0%, transparent 60%)`
                    }}
                />

                <div className="relative z-10">
                    {/* Header Logo */}
                    <div className="flex items-center gap-3.5 mb-10">
                        <div className="relative flex items-center justify-center w-11 h-11 rounded-lg bg-gradient-to-br from-[#087F72] to-[#044A42] border border-[#33A395]/40 shadow-[0_0_15px_rgba(8,127,114,0.3)]">
                            <Shield className="w-7 h-7 text-white stroke-[1.75]" />
                            <Star className="w-3.5 h-3.5 text-white fill-white absolute top-[13px]" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold tracking-wider text-white flex items-center gap-2">
                                SOVEREIGN AI WORKBENCH
                            </h1>
                            <p className="text-[10px] font-mono tracking-widest text-[#56C5B8] uppercase">
                                SECURE &nbsp;|&nbsp; PRIVATE &nbsp;|&nbsp; ORGANIZATION-RESTRICTED
                            </p>
                        </div>
                    </div>

                    {/* Main Headline */}
                    <h2 className="text-3xl lg:text-4xl font-semibold tracking-tight text-white mb-10 leading-snug max-w-xl">
                        AI-powered intelligence and document analysis for a safer tomorrow.
                    </h2>

                    {/* Feature Bullets */}
                    <div className="space-y-6 max-w-lg mb-8">
                        <div className="flex items-start gap-4">
                            <div className="w-9 h-9 rounded-lg bg-[#0E2929] border border-[#1B4747] flex items-center justify-center shrink-0 mt-0.5 text-[#56C5B8]">
                                <Lock className="w-4 h-4" />
                            </div>
                            <div>
                                <h3 className="text-sm font-semibold text-white">Designed for authorized organizations only</h3>
                                <p className="text-xs text-[#8C9C9C] mt-0.5 leading-relaxed">
                                    Access is restricted to approved users and devices within your organization.
                                </p>
                            </div>
                        </div>

                        <div className="flex items-start gap-4">
                            <div className="w-9 h-9 rounded-lg bg-[#0E2929] border border-[#1B4747] flex items-center justify-center shrink-0 mt-0.5 text-[#56C5B8]">
                                <ShieldCheck className="w-4 h-4" />
                            </div>
                            <div>
                                <h3 className="text-sm font-semibold text-white">Keeps your data secure</h3>
                                <p className="text-xs text-[#8C9C9C] mt-0.5 leading-relaxed">
                                    All documents, models and knowledge base remain within your private network.
                                </p>
                            </div>
                        </div>

                        <div className="flex items-start gap-4">
                            <div className="w-9 h-9 rounded-lg bg-[#0E2929] border border-[#1B4747] flex items-center justify-center shrink-0 mt-0.5 text-[#56C5B8]">
                                <Cpu className="w-4 h-4" />
                            </div>
                            <div>
                                <h3 className="text-sm font-semibold text-white">Built for mission-critical operations</h3>
                                <p className="text-xs text-[#8C9C9C] mt-0.5 leading-relaxed">
                                    Trusted AI assistance for complex decision-making and analysis.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Bottom Left Prototype Box */}
                <div className="relative z-10 mt-8">
                    <div className="p-4 rounded-xl bg-[#081E1E]/80 border border-[#1B4747] flex items-start gap-3 backdrop-blur-md">
                        <Lock className="w-5 h-5 text-[#56C5B8] shrink-0 mt-0.5" />
                        <div>
                            <h4 className="text-xs font-semibold text-[#56C5B8]">Organization-Restricted Deployment</h4>
                            <p className="text-[11px] text-[#8C9C9C] mt-0.5 leading-relaxed">
                                This prototype demonstrates the user interface. In production, the application is deployed only within an authorized organization's infrastructure (on-premise / air-gapped).
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* ── RIGHT PANEL: Form & Credentials ─────────────────────────────── */}
            <div className="lg:w-1/2 p-8 lg:p-14 flex flex-col justify-between bg-[#051111] relative overflow-y-auto">
                <div className="max-w-md mx-auto w-full my-auto py-6">
                    {/* Header Shield & Titles */}
                    <div className="flex flex-col items-center text-center mb-8">
                        <div className="relative flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-[#087F72] to-[#044A42] border border-[#33A395]/40 mb-4 shadow-[0_0_20px_rgba(8,127,114,0.35)]">
                            <Shield className="w-8 h-8 text-white stroke-[1.75]" />
                            <Star className="w-4 h-4 text-white fill-white absolute top-[16px]" />
                        </div>
                        <h2 className="text-xl font-bold tracking-wide text-white">
                            SOVEREIGN AI WORKBENCH
                        </h2>
                        <p className="text-xs font-medium text-[#8C9C9C] mt-1">
                            Authorized Access Only
                        </p>
                        <p className="text-xs text-[#5D7373] mt-3 leading-relaxed max-w-sm">
                            This system is designed for deployment only within an authorized organization's infrastructure.
                        </p>
                    </div>

                    {/* Authentication Form */}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {errorMsg && (
                            <div className="p-3 rounded-lg bg-red-950/60 border border-red-700/50 text-red-300 text-xs text-center">
                                {errorMsg}
                            </div>
                        )}

                        {/* Organization Input */}
                        <div>
                            <label className="block text-xs font-medium text-[#8C9C9C] mb-1.5">
                                Organization / Unit
                            </label>
                            <div className="relative">
                                <Building2 className="w-4 h-4 text-[#5D7373] absolute left-3.5 top-1/2 -translate-y-1/2" />
                                <input
                                    type="text"
                                    value={organization}
                                    onChange={(e) => setOrganization(e.target.value)}
                                    placeholder="Enter your organization or unit"
                                    className="w-full bg-[#081A1A] border border-[#183636] focus:border-[#56C5B8] outline-none text-xs text-white placeholder-[#455757] rounded-lg pl-10 pr-4 py-3 transition-all"
                                />
                            </div>
                        </div>

                        {/* User ID Input */}
                        <div>
                            <label className="block text-xs font-medium text-[#8C9C9C] mb-1.5">
                                User ID
                            </label>
                            <div className="relative">
                                <User className="w-4 h-4 text-[#5D7373] absolute left-3.5 top-1/2 -translate-y-1/2" />
                                <input
                                    type="text"
                                    value={userId}
                                    onChange={(e) => setUserId(e.target.value)}
                                    placeholder="Enter your user ID"
                                    className="w-full bg-[#081A1A] border border-[#183636] focus:border-[#56C5B8] outline-none text-xs text-white placeholder-[#455757] rounded-lg pl-10 pr-4 py-3 transition-all"
                                />
                            </div>
                        </div>

                        {/* Password Input */}
                        <div>
                            <label className="block text-xs font-medium text-[#8C9C9C] mb-1.5">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="w-4 h-4 text-[#5D7373] absolute left-3.5 top-1/2 -translate-y-1/2" />
                                <input
                                    type={showPassword ? "text" : "password"}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Enter your password"
                                    className="w-full bg-[#081A1A] border border-[#183636] focus:border-[#56C5B8] outline-none text-xs text-white placeholder-[#455757] rounded-lg pl-10 pr-10 py-3 transition-all"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#5D7373] hover:text-[#56C5B8]"
                                >
                                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                        </div>

                        {/* Authenticate Button */}
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full mt-2 bg-[#56C5B8] hover:bg-[#48B4A7] text-[#041717] font-semibold text-xs py-3.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-all shadow-[0_0_15px_rgba(86,197,184,0.2)] disabled:opacity-50 cursor-pointer"
                        >
                            <span>{isSubmitting ? "Authenticating..." : "Authenticate"}</span>
                            <ArrowRight className="w-4 h-4" />
                        </button>
                    </form>

                    {/* ── DEMO CREDENTIALS SECTION ───────────────────────────────────── */}
                    <div className="mt-6 p-4 rounded-xl bg-[#091D1D] border border-[#194040] relative">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-[11px] font-mono uppercase tracking-wider text-[#56C5B8] font-bold flex items-center gap-1.5">
                                <Key className="w-3.5 h-3.5" />
                                Demo Login Credentials
                            </span>
                            <button
                                type="button"
                                onClick={handleFillDemo}
                                className="text-[11px] font-medium bg-[#0E2B2B] hover:bg-[#163D3D] text-[#56C5B8] px-2.5 py-1 rounded border border-[#1E4D4D] transition-colors flex items-center gap-1 cursor-pointer"
                            >
                                {copiedDemo ? (
                                    <>
                                        <Check className="w-3 h-3 text-emerald-400" />
                                        <span className="text-emerald-400 font-semibold">Filled!</span>
                                    </>
                                ) : (
                                    <span>Auto-Fill Credentials</span>
                                )}
                            </button>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs font-mono bg-[#051111] p-2.5 rounded-lg border border-[#143333]">
                            <div>
                                <span className="text-[10px] text-[#5D7373] block uppercase">Organization</span>
                                <span className="text-white font-medium select-all">{DEMO_ORG}</span>
                            </div>
                            <div>
                                <span className="text-[10px] text-[#5D7373] block uppercase">User ID</span>
                                <span className="text-white font-medium select-all">{DEMO_USER}</span>
                            </div>
                            <div>
                                <span className="text-[10px] text-[#5D7373] block uppercase">Password</span>
                                <span className="text-white font-medium select-all">{DEMO_PASS}</span>
                            </div>
                        </div>
                    </div>

                    <p className="text-[11px] text-center text-[#5D7373] mt-6">
                        Only authorized personnel are allowed to access.
                    </p>

                    {/* Bottom Prototype Notice Box */}
                    <div className="mt-4 p-3.5 rounded-xl bg-[#081818] border border-[#153333] flex items-start gap-2.5">
                        <Info className="w-4 h-4 text-[#56C5B8] shrink-0 mt-0.5" />
                        <p className="text-[11px] text-[#8C9C9C] leading-relaxed">
                            This is a <strong className="text-white font-semibold">prototype</strong>. The actual system will be deployed on your organization's secure infrastructure.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};
export default LoginView;
