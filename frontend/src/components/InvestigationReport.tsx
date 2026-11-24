import React, { useState } from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  Copy, 
  Download, 
  Check, 
  Globe, 
  PhoneCall, 
  Layers, 
  Info, 
  ExternalLink,
  Lock,
  Eye,
  FileText,
  Share2,
  ChevronRight,
  ArrowLeft
} from 'lucide-react';
import { ScanResponse, Span } from '../types/intelligence';

interface InvestigationReportProps {
  report: ScanResponse;
  onNewScan: () => void;
}

export const InvestigationReport: React.FC<InvestigationReportProps> = ({ report, onNewScan }) => {
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<'evidence' | 'psychology' | 'actions'>('evidence');

  const risk = report.risk;
  const isSafe = risk.band === 'low';
  const isCaution = risk.band === 'caution';
  const isHigh = risk.band === 'high';
  const isCrit = risk.band === 'very_high';

  const riskColor = isCrit ? 'rose' : isHigh ? 'rose' : isCaution ? 'amber' : 'emerald';
  const riskTitle = isCrit ? 'CRITICAL RISK' : isHigh ? 'HIGH RISK' : isCaution ? 'CAUTION ADVISED' : 'LOW DETECTED RISK';

  const handleCopy = () => {
    const reportText = `ZENVEX GUARD // INVESTIGATION REPORT
Scan ID: ${report.scan_id}
Risk Verdict: ${risk.label} (${risk.score}/100)
Scam Category: ${report.scam_type ? report.scam_type.label : 'None / Benign'}
Detected Language: ${report.language}

EXPLANATION:
${report.explanation.text}

DETECTED INDICATORS:
${report.indicators.map(i => `- ${i.label}: ${i.evidence.join(', ')}`).join('\n') || 'None'}

DETECTED URLS:
${report.urls.map(u => `- ${u.url} (${u.verdict}): ${u.flags.map(f => f.label).join('; ')}`).join('\n') || 'None'}

RECOMMENDED SAFETY ACTIONS:
${report.actions.map(a => `- ${a.en}`).join('\n')}

CYBERCRIME HELPLINE: 1930 | cybercrime.gov.in
Disclaimer: ${risk.disclaimer}`;

    navigator.clipboard.writeText(reportText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExport = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `zenvex-guard-${report.scan_id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Render highlighted spans inside the original message
  const renderHighlightedText = () => {
    const text = report.text;
    if (!text || !report.spans || report.spans.length === 0) {
      return <span>{text}</span>;
    }

    // The API counts Unicode code points, while JavaScript strings index UTF-16 units.
    const characters = Array.from(text);
    // Sort spans by start offset
    const sorted = [...report.spans].sort((a, b) => a.start - b.start);
    const elements: React.ReactNode[] = [];
    let currentIndex = 0;

    sorted.forEach((span, idx) => {
      // Overlap prevention
      if (span.start < currentIndex) return;

      if (span.start > currentIndex) {
        elements.push(
          <span key={`text-${currentIndex}`}>
            {characters.slice(currentIndex, span.start).join('')}
          </span>
        );
      }

      const matchText = characters.slice(span.start, span.end).join('');
      const isUrl = span.kind === 'url';

      elements.push(
        <mark
          key={`span-${idx}`}
          className={`px-1.5 py-0.5 rounded font-semibold text-xs ${
            isUrl 
              ? 'bg-cyan-500/25 text-cyan-300 border border-cyan-500/40' 
              : 'bg-rose-500/25 text-rose-300 border border-rose-500/40'
          }`}
          title={isUrl ? 'Suspicious URL Structure' : `Indicator: ${span.id}`}
        >
          {matchText}
        </mark>
      );
      currentIndex = span.end;
    });

    if (currentIndex < characters.length) {
      elements.push(
        <span key={`text-end`}>
          {characters.slice(currentIndex).join('')}
        </span>
      );
    }

    return elements;
  };

  return (
    <div className="space-y-8 py-4 max-w-5xl mx-auto">
      {/* Top action header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <button
            onClick={onNewScan}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Back to Scanner"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono text-cyan-400">SCAN #{report.scan_id}</span>
              <span className="text-slate-500">•</span>
              <span className="text-xs text-slate-400 uppercase font-mono">LANG: {report.language}</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-extrabold text-white">
              Threat Forensic Dossier
            </h1>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopy}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-navy-850 hover:bg-slate-800 text-slate-300 text-xs border border-slate-700 transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy Dossier'}</span>
          </button>
          <button
            onClick={handleExport}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-navy-850 hover:bg-slate-800 text-slate-300 text-xs border border-slate-700 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      {/* Primary Threat Verdict Card */}
      <div className={`p-6 sm:p-8 rounded-2xl glass-panel border ${
        isCrit ? 'border-rose-500/50 bg-rose-950/15' :
        isHigh ? 'border-rose-500/40 bg-rose-950/10' :
        isCaution ? 'border-amber-500/40 bg-amber-950/10' :
        'border-emerald-500/40 bg-emerald-950/10'
      }`}>
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="flex items-start space-x-4">
            <div className={`w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 ${
              isCrit ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
              isHigh ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
              isCaution ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
              'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
            }`}>
              {isSafe ? <ShieldCheck className="w-8 h-8" /> : isCaution ? <AlertTriangle className="w-8 h-8" /> : <ShieldAlert className="w-8 h-8" />}
            </div>

            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className={`px-2.5 py-0.5 rounded-md text-xs font-extrabold uppercase tracking-wider ${
                  isCrit ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                  isHigh ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                  isCaution ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                  'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                }`}>
                  {riskTitle}
                </span>
                {report.scam_type && (
                  <span className="px-2.5 py-0.5 rounded-md text-xs font-semibold bg-violet-500/20 text-violet-300 border border-violet-500/30">
                    {report.scam_type.label}
                  </span>
                )}
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                {risk.label}
              </h2>
              <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
                {report.explanation.text}
              </p>
            </div>
          </div>

          {/* Numeric Evidence Score Gauge */}
          <div className="p-4 rounded-xl bg-navy-950 border border-slate-800 text-center shrink-0 w-full lg:w-48 space-y-2">
            <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Evidence Score</span>
            <div className="flex items-baseline justify-center space-x-1">
              <span className={`text-4xl font-black font-mono ${
                isCrit ? 'text-rose-400' : isHigh ? 'text-rose-400' : isCaution ? 'text-amber-400' : 'text-emerald-400'
              }`}>
                {risk.score}
              </span>
              <span className="text-slate-500 font-mono text-xs">/ 100</span>
            </div>
            {/* Breakdown meters */}
            <div className="space-y-1 pt-1 text-[10px] text-slate-400 font-mono">
              <div className="flex justify-between">
                <span>Text Rules:</span>
                <span className="text-slate-200">+{risk.breakdown.text}</span>
              </div>
              <div className="flex justify-between">
                <span>URL Structure:</span>
                <span className="text-slate-200">+{risk.breakdown.url}</span>
              </div>
              {risk.breakdown.ml > 0 && (
                <div className="flex justify-between">
                  <span>ML Model:</span>
                  <span className="text-slate-200">+{risk.breakdown.ml}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Inspected Content with Interactive Evidence Highlighting */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileText className="w-4 h-4 text-violet-400" />
            <h3 className="text-sm font-bold text-white">Analyzed Content & Extracted Signatures</h3>
          </div>
          <div className="flex items-center space-x-3 text-xs">
            <span className="flex items-center space-x-1">
              <span className="w-2.5 h-2.5 rounded bg-rose-500/50 inline-block border border-rose-500"></span>
              <span className="text-slate-300">Scam Language Hook</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2.5 h-2.5 rounded bg-cyan-500/50 inline-block border border-cyan-500"></span>
              <span className="text-slate-300">Suspicious Link</span>
            </span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-navy-950 border border-slate-800 font-mono text-sm leading-relaxed text-slate-200 whitespace-pre-wrap break-words">
          {renderHighlightedText()}
        </div>
      </div>

      {/* Multi-angle Investigation Tabs */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="flex border-b border-slate-800 bg-navy-900/60 px-4 pt-3 space-x-4">
          <button
            onClick={() => setActiveTab('evidence')}
            className={`pb-3 text-xs sm:text-sm font-semibold transition-colors border-b-2 flex items-center space-x-2 ${
              activeTab === 'evidence'
                ? 'border-violet-500 text-white'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Indicators & URLs ({report.indicators.length + report.urls.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('psychology')}
            className={`pb-3 text-xs sm:text-sm font-semibold transition-colors border-b-2 flex items-center space-x-2 ${
              activeTab === 'psychology'
                ? 'border-violet-500 text-white'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Eye className="w-4 h-4" />
            <span>Victim Manipulation Tactics</span>
          </button>
          <button
            onClick={() => setActiveTab('actions')}
            className={`pb-3 text-xs sm:text-sm font-semibold transition-colors border-b-2 flex items-center space-x-2 ${
              activeTab === 'actions'
                ? 'border-violet-500 text-white'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Recommended Safety Actions ({report.actions.length})</span>
          </button>
        </div>

        <div className="p-6">
          {/* TAB 1: Indicators & URLs */}
          {activeTab === 'evidence' && (
            <div className="space-y-6">
              {/* Text Indicators */}
              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Detected Message Indicators
                </h4>
                {report.indicators.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {report.indicators.map((ind) => (
                      <div key={ind.id} className="p-3.5 rounded-xl bg-navy-950 border border-slate-800/80 space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-xs text-white">{ind.label}</span>
                          <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300">
                            +{ind.weight} pts
                          </span>
                        </div>
                        {ind.evidence.length > 0 && (
                          <div className="text-[11px] text-slate-400 font-mono">
                            <span className="text-slate-500">Trigger phrase: </span>
                            <span className="text-rose-300">"{ind.evidence.join('", "')}"</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400 italic">No standard malicious text indicators detected in this content.</p>
                )}
              </div>

              {/* URL Intelligence Section */}
              <div className="space-y-3 pt-4 border-t border-slate-800">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
                  <Globe className="w-3.5 h-3.5 text-cyan-400" />
                  <span>14-Point Offline URL Inspection</span>
                </h4>
                {report.urls.length > 0 ? (
                  <div className="space-y-3">
                    {report.urls.map((url, uidx) => (
                      <div key={uidx} className="p-4 rounded-xl bg-navy-950 border border-slate-800 space-y-3">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-2">
                          <div className="font-mono text-xs font-semibold text-cyan-300 break-all">
                            {url.url}
                          </div>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase shrink-0 ${
                            url.score > 40 ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'
                          }`}>
                            {url.verdict.toUpperCase()} (Score: {url.score})
                          </span>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] font-mono text-slate-400">
                          <div>
                            <span className="block text-slate-500">Host:</span>
                            <span className="text-slate-200">{url.host || 'N/A'}</span>
                          </div>
                          <div>
                            <span className="block text-slate-500">Registered Domain:</span>
                            <span className="text-slate-200">{url.registered_domain || 'N/A'}</span>
                          </div>
                          <div>
                            <span className="block text-slate-500">Official Brand Match:</span>
                            <span className={url.official_domain_match ? 'text-emerald-400 font-bold' : 'text-slate-400'}>
                              {url.official_domain_match ? 'YES (Official)' : 'NO (Unverified)'}
                            </span>
                          </div>
                          <div>
                            <span className="block text-slate-500">Safe Offline Parsing:</span>
                            <span className="text-emerald-400">Never Opened</span>
                          </div>
                        </div>

                        {/* Structural Flags */}
                        {url.flags.length > 0 && (
                          <div className="space-y-1.5 pt-1">
                            <span className="text-[11px] font-semibold text-slate-300">Detected Structural Flags:</span>
                            <div className="flex flex-wrap gap-1.5">
                              {url.flags.map((f, fidx) => (
                                <span key={fidx} className="px-2 py-0.5 rounded text-[11px] bg-slate-800 text-slate-200 border border-slate-700">
                                  {f.label} (+{f.weight} pts)
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        <p className="text-xs text-slate-400 italic">{url.note}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400 italic">No links or URLs identified in this content.</p>
                )}
              </div>
            </div>
          )}

          {/* TAB 2: Psychological Manipulation */}
          {activeTab === 'psychology' && (
            <div className="space-y-4">
              <p className="text-xs text-slate-300 leading-relaxed">
                Cyber fraud relies primarily on cognitive engineering and psychological leverage to override rational hesitation. ZenVex Guard identifies the primary manipulative hooks detected in this message:
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-navy-950 border border-slate-800 space-y-2">
                  <div className="flex items-center space-x-2 text-rose-400 font-bold text-xs uppercase">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Artificial Urgency & Scarcity</span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Imposing immediate deadlines (e.g., <em>"immediately"</em>, <em>"tonight"</em>, <em>"within 2 hours"</em>) denies victims sufficient time to consult trusted family members or verify with their branch manager.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-navy-950 border border-slate-800 space-y-2">
                  <div className="flex items-center space-x-2 text-amber-400 font-bold text-xs uppercase">
                    <Lock className="w-4 h-4" />
                    <span>Authority & Institutional Coercion</span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Threatening termination of essential services (bank accounts, PAN card, SIM connection, electricity supply, or law enforcement warrants) induces acute fear and compliance.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-navy-950 border border-slate-800 space-y-2">
                  <div className="flex items-center space-x-2 text-violet-400 font-bold text-xs uppercase">
                    <Globe className="w-4 h-4" />
                    <span>Counterfeit Verification Illusion</span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Providing lookalike hyperlinks (e.g., containing <em>sbi-kyc</em> or <em>hdfc-update</em>) tricks users into believing they are using an authorized portal rather than a phishing collection terminal.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-navy-950 border border-slate-800 space-y-2">
                  <div className="flex items-center space-x-2 text-cyan-400 font-bold text-xs uppercase">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Reverse Psychology / False Advice</span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Some sophisticated scams include genuine-sounding safety warnings (e.g., <em>"Do not share OTP"</em>) while requesting input of the same secrets on a third-party form.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: Recommended Safety Actions */}
          {activeTab === 'actions' && (
            <div className="space-y-6">
              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Immediate Prescribed Actions
                </h4>
                <div className="space-y-2.5">
                  {report.actions.map((act, aidx) => (
                    <div key={aidx} className="p-3.5 rounded-xl bg-navy-950 border border-slate-800 flex items-start space-x-3">
                      <div className="w-5 h-5 rounded-full bg-violet-600/20 text-violet-400 border border-violet-500/30 flex items-center justify-center shrink-0 mt-0.5 text-xs font-bold font-mono">
                        {aidx + 1}
                      </div>
                      <div className="space-y-1">
                        <p className="text-xs font-semibold text-white leading-relaxed">{act.en}</p>
                        {act.te && (
                          <p className="text-xs text-slate-400 leading-relaxed font-sans">{act.te}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Official Helplines callout */}
              <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/30 space-y-2">
                <div className="flex items-center space-x-2 text-rose-300 font-bold text-xs uppercase">
                  <PhoneCall className="w-4 h-4" />
                  <span>Financial Fraud Emergency Guidance</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  If money has already been deducted or credentials were submitted on a suspicious site, dial <strong>1930</strong> immediately within the Golden Hour to facilitate a freeze of the transferred funds. Log a complaint on <strong>cybercrime.gov.in</strong>.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer disclaimer */}
      <div className="p-4 rounded-xl bg-navy-900 border border-slate-800/80 text-[11px] text-slate-400 text-center font-mono leading-relaxed">
        {report.risk.disclaimer} • Generated by ZenVex Guard Autonomous Threat Engine
      </div>
    </div>
  );
};
