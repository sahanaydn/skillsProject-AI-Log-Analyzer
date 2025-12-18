import React, { useEffect, useRef, useState } from 'react';
import { Bot, User, MessageSquare, ChevronDown, FileText } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

const SourcePill = ({ logs, messageIndex }) => {
    const [isOpen, setIsOpen] = useState(false);

    if (!logs || logs.length === 0) return null;

    return (
        <div className="sourceContainer">
            <button onClick={() => setIsOpen(!isOpen)} className="sourcePill">
                <FileText size={14} />
                <span>Sources ({logs.length})</span>
                <ChevronDown size={16} className={`chevron ${isOpen ? 'open' : ''}`} />
            </button>
            {isOpen && (
                <div className="sourceContent">
                    {logs.map((log, index) => (
                        <pre key={`${messageIndex}-log-${index}`} className="logSnippet">{log}</pre>
                    ))}
                </div>
            )}
        </div>
    );
};

const ChatView = ({ chatHistory, isChatting, onSuggestionClick }) => {
    const chatEndRef = useRef(null);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatHistory, isChatting]);

    if (chatHistory.length === 0 && !isChatting) {
        return (
            <div className="placeholder-view">
                <MessageSquare size={48} />
                <p>Ask a question about the analyzed logs.</p>
            </div>
        );
    }

    return (
        <div className="chatWindow">
            {chatHistory.map((msg, index) => (
                <div key={index} className={`chatMessage ${msg.sender}`}>
                    <div className="avatar">
                        {msg.sender === 'user' ? <User size={18} /> : <Bot size={18} />}
                    </div>
                    <div className="messageContent">
                        <div className="text">
                            {msg.sender === 'user' ? msg.text : msg.answer}
                        </div>
                        {msg.sender === 'ai' && (
                            <div className="messageExtras">
                                <SourcePill logs={msg.relevant_logs} messageIndex={index} />
                                <div className="suggestions">
                                    {msg.suggested_followup?.map((sugg, i) => (
                                        <button key={i} className="suggestionChip" onClick={() => onSuggestionClick(sugg)}>
                                            {sugg}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            ))}
            {isChatting && (
                <div className="chatMessage ai">
                    <div className="avatar"><Bot size={18} /></div>
                    <div className="messageContent">
                        <div className="text"><LoadingSpinner /></div>
                    </div>
                </div>
            )}
            <div ref={chatEndRef} />
        </div>
    );
};

export default ChatView;

