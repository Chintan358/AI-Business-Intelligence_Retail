import React, { useState, useEffect, useRef } from 'react';
import apiClient from '../api/client';
import {
  MessageSquare,
  Send,
  Sparkles,
  Bot,
  User,
  ShieldCheck,
  HelpCircle,
  Clock
} from 'lucide-react';

const ChatPage = () => {
  const [messages, setMessages] = useState([
    {
      id: 0,
      sender: 'assistant',
      message: (
        "Hello! I am your AI Business Operations & Decision Intelligence Assistant. " +
        "My answers are grounded in your verified retail database calculations (May 1 – October 31, 2026). " +
        "Ask me about monthly revenues, product margins, customer segments, stockout hazards, or profitability turnaround strategies!"
      ),
      created_at: new Date().toISOString()
    }
  ]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  const presetQueries = [
    "What was my total revenue in September?",
    "Which products generated the highest revenue?",
    "Which products have inventory risks?",
    "Why did sales decrease?",
    "Which customer segments are valuable?",
    "How can I improve profitability?",
    "What are my biggest business risks?"
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (textToSend) => {
    const q = textToSend || query;
    if (!q.trim()) return;

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      message: q,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, userMsg]);
    setQuery('');
    setLoading(true);

    try {
      const res = await apiClient.post('/chat/query', {
        query: q,
        conversation_id: conversationId
      });
      setConversationId(res.data.conversation_id);
      setMessages((prev) => [
        ...prev,
        {
          id: res.data.message_id,
          sender: 'assistant',
          message: res.data.message,
          grounding_data: res.data.grounding_data,
          created_at: res.data.created_at
        }
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'assistant',
          message: 'Sorry, I encountered an error querying the business intelligence database. Please retry.',
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-6.5rem)] bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
      {/* Chat Header */}
      <div className="px-6 py-3.5 border-b border-slate-800 bg-slate-900/80 backdrop-blur flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-white shadow-md shadow-emerald-500/20">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white flex items-center gap-2">
              <span>Grounded Retail Assistant</span>
              <span className="text-[10px] font-bold px-2 py-0.2 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Verified Data Grounding
              </span>
            </h2>
            <p className="text-[11px] text-slate-400">Deterministic calculations powered by PostgreSQL & Pandas</p>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-400">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <span>Zero Hallucination Policy</span>
        </div>
      </div>

      {/* Message Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
        {messages.map((m) => {
          const isUser = m.sender === 'user';
          return (
            <div
              key={m.id}
              className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
            >
              <div
                className={`h-8 w-8 rounded-full flex items-center justify-center text-xs shrink-0 ${
                  isUser ? 'bg-slate-700 text-white' : 'bg-emerald-600 text-white shadow-md shadow-emerald-500/20'
                }`}
              >
                {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
              </div>

              <div
                className={`max-w-2xl rounded-2xl px-4 py-3 text-xs leading-relaxed ${
                  isUser
                    ? 'bg-emerald-600 text-white rounded-tr-none'
                    : 'bg-slate-950 border border-slate-800 text-slate-200 rounded-tl-none'
                }`}
              >
                <div className="whitespace-pre-line">{m.message}</div>
                {m.grounding_data && Object.keys(m.grounding_data).length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center gap-1 text-[10px] text-emerald-400 font-medium">
                    <ShieldCheck className="h-3 w-3 shrink-0" />
                    <span>Cross-referenced with database records</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex items-start gap-3">
            <div className="h-8 w-8 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs">
              <Bot className="h-4 w-4" />
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-2xl rounded-tl-none px-4 py-3 text-xs text-slate-400 flex items-center space-x-2">
              <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></div>
              <span>Querying database engine and synthesizing ground truth...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Prompt Chips */}
      <div className="px-4 py-2 border-t border-slate-800/80 bg-slate-900/60 overflow-x-auto">
        <div className="flex items-center space-x-2 w-max">
          <span className="text-[10px] text-slate-500 uppercase font-bold flex items-center gap-1">
            <Sparkles className="h-3 w-3" />
            Suggested:
          </span>
          {presetQueries.map((pq, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(pq)}
              disabled={loading}
              className="px-2.5 py-1 rounded-full text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 hover:border-slate-600 transition whitespace-nowrap disabled:opacity-50"
            >
              {pq}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="p-3 border-t border-slate-800 bg-slate-900/90 flex items-center gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a verified retail business question (e.g. 'What was my total revenue in September?')..."
          className="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="h-9 w-9 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white flex items-center justify-center transition disabled:opacity-50 shadow-md shadow-emerald-500/20"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
};

export default ChatPage;
