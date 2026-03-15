"use client";
import React, { useState, useEffect } from 'react';
import { Shield, Radio, Send, Activity, Lock, Upload, Download, Globe } from 'lucide-react';

const API = "http://10.213.230.220:8000";

interface Message {
  direction: "sent" | "received";
  peer: string;
  text: string;
  time: string;
}

export default function AegisDashboard() {
  const [peers, setPeers] = useState<string[]>([]);
  const [status, setStatus] = useState("SCANNING");
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedTarget, setSelectedTarget] = useState<string>("ALL");

  useEffect(() => {
    const fetchPeers = async () => {
      try {
        const res = await fetch(`${API}/peers`);
        const data = await res.json();
        setPeers(data.peers || []);
        setStatus(data.peers.length > 0 ? "MESH_ACTIVE" : "SCANNING");
      } catch { setStatus("OFFLINE"); }
    };

    const fetchMessages = async () => {
      try {
        const res = await fetch(`${API}/messages`);
        const data = await res.json();
        setMessages(data.messages || []);
      } catch { }
    };

    const interval = setInterval(() => {
      fetchPeers();
      fetchMessages();
    }, 2000);
    fetchPeers();
    fetchMessages();
    return () => clearInterval(interval);
  }, []);

  const handleSend = async () => {
    if (!message || (peers.length === 0 && selectedTarget !== "ALL")) return;
    await fetch(`${API}/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ receiver_id: selectedTarget, message })
    });
    setMessage("");
  };

  return (
    <div className="min-h-screen bg-[#0a0a0c] text-slate-200 font-sans p-4 md:p-10">
      <div className="max-w-6xl mx-auto flex justify-between items-center mb-10 border-b border-white/10 pb-6">
        <div className="flex items-center gap-3">
          <Shield className="text-blue-500 w-8 h-8" />
          <h1 className="text-2xl font-black tracking-widest text-white">Hop<span className="text-blue-500">Chat</span></h1>
        </div>
        <div className={`flex items-center gap-2 px-4 py-1 rounded-full border ${status === "MESH_ACTIVE" ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-400" : "border-red-500/50 bg-red-500/10 text-red-400"}`}>
          <Activity className="w-4 h-4 animate-pulse" />
          <span className="text-xs font-bold tracking-tighter uppercase">{status}</span>
        </div>
      </div>

      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-xl">
          <div className="flex items-center gap-2 mb-6">
            <Radio className="text-blue-400 w-5 h-5" />
            <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400">Target Selection</h2>
          </div>
          <div className="space-y-3">

            <div
              onClick={() => setSelectedTarget("ALL")}
              className={`p-4 rounded-xl border transition-all cursor-pointer group flex items-center gap-3 ${selectedTarget === "ALL" ? "bg-blue-500/20 border-blue-500/50" : "bg-white/5 border-white/5 hover:border-blue-500/30"}`}
            >
              <Globe className={`w-5 h-5 ${selectedTarget === "ALL" ? "text-blue-400" : "text-slate-500 group-hover:text-blue-400"}`} />
              <div>
                <p className="text-[10px] text-slate-400 mb-1 tracking-widest">OMNI-DIRECTIONAL</p>
                <p className={`text-sm font-bold ${selectedTarget === "ALL" ? "text-blue-100" : "text-slate-300"}`}>BROADCAST TO ALL</p>
              </div>
            </div>

            <div className="w-full h-px bg-white/10 my-4"></div>

            {peers.length === 0 ? (
              <div className="py-6 text-center border border-dashed border-white/10 rounded-xl">
                <p className="text-xs text-slate-500">Scanning for peers...</p>
              </div>
            ) : (
              peers.map(p => (
                <div
                  key={p}
                  onClick={() => setSelectedTarget(p)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer group ${selectedTarget === p ? "bg-emerald-500/10 border-emerald-500/50" : "bg-white/5 border-white/5 hover:border-emerald-500/30"}`}
                >
                  <p className="text-[10px] text-slate-500 mb-1">AUTHORIZED NODE</p>
                  <p className={`text-sm font-mono transition-colors ${selectedTarget === p ? "text-emerald-400" : "text-emerald-100 group-hover:text-emerald-300"}`}>{p}</p>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <div className="bg-gradient-to-br from-blue-600/20 to-purple-600/20 border border-blue-500/20 rounded-2xl p-8">
            <div className="flex items-center gap-2 mb-4 text-blue-400">
              <Lock className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-widest">
                {selectedTarget === "ALL" ? "Global Secure Uplink" : `Direct Uplink: ${selectedTarget}`}
              </span>
            </div>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder={`Inject message for ${selectedTarget === "ALL" ? "global broadcast" : selectedTarget}...`}
              className="w-full h-32 bg-black/40 border border-white/10 rounded-xl p-4 text-lg text-white placeholder:text-slate-600 focus:outline-none focus:border-blue-500/50 transition-all"
            />
            <button
              onClick={handleSend}
              disabled={(peers.length === 0 && selectedTarget !== "ALL") || !message}
              className="mt-4 w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-30 disabled:cursor-not-allowed text-white font-bold py-4 rounded-xl flex items-center justify-center gap-3 transition-all shadow-lg shadow-blue-500/20"
            >
              <Send className="w-5 h-5" />
              {selectedTarget === "ALL" ? "INITIATE GLOBAL BROADCAST" : "TRANSMIT DIRECT SHARDS"}
            </button>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-xl">
            <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400 mb-4">Transmission Log</h2>
            <div className="space-y-2 max-h-64 overflow-y-auto pr-2">
              {messages.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-6">No transmissions yet...</p>
              ) : (
                [...messages].reverse().map((m, i) => (
                  <div key={i} className={`flex items-start gap-3 p-3 rounded-xl border ${m.direction === "sent" ? "border-blue-500/20 bg-blue-500/5" : "border-emerald-500/20 bg-emerald-500/5"}`}>
                    {m.direction === "sent"
                      ? <Upload className="w-4 h-4 text-blue-400 mt-0.5 shrink-0" />
                      : <Download className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                    }
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-slate-500 mb-0.5">
                        {m.direction === "sent" ? `YOU → ${m.peer}` : `${m.peer} → YOU`}
                        <span className="ml-2 opacity-50">{m.time}</span>
                      </p>
                      <p className="text-sm text-white font-mono break-words">{m.text}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}