import React, { useState, useEffect } from 'react';
import { LayoutGrid, MessageSquare, Send } from 'lucide-react';

import { uploadLogFile, getSummary, postQuery } from './services/apiService';
import Sidebar from './components/Sidebar';
import DashboardView from './components/DashboardView';
import ChatView from './components/ChatView';
import SummaryView from './components/SummaryView';

import './App.css';

const UPLOAD_STEPS = [ "Uploading file...", "Analyzing structure...", "Processing content...", "Finalizing... (Generating Summary)" ];

function App() {
    const [file, setFile] = useState(null);
    const [fileName, setFileName] = useState('');
    const [analysisResult, setAnalysisResult] = useState(null);
    const [summaryReport, setSummaryReport] = useState(null);
    
    const [view, setView] = useState('dashboard');
    const [error, setError] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState([]);
    
    const [query, setQuery] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [isChatting, setIsChatting] = useState(false);

    useEffect(() => {
        let timer;
        if (isUploading && uploadProgress.length < UPLOAD_STEPS.length) {
            timer = setTimeout(() => {
                setUploadProgress(prev => [...prev, UPLOAD_STEPS[prev.length]]);
            }, 750);
        }
        return () => clearTimeout(timer);
    }, [isUploading, uploadProgress]);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setFileName(selectedFile.name);
            setError('');
            setAnalysisResult(null);
            setSummaryReport(null);
            setUploadProgress([]);
            setChatHistory([]);
            setView('dashboard');
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setError('A log file is required.');
            return;
        }
        setError('');
        setAnalysisResult(null);
        setSummaryReport(null);
        setUploadProgress([]);
        setIsUploading(true);
        
        try {
            const uploadData = await uploadLogFile(file);
            setAnalysisResult(uploadData);

            const summaryData = await getSummary();
            setSummaryReport(summaryData);

            setChatHistory([]);
            setView('dashboard');
        } catch (err) {
            setError(err.message);
        } finally {
            setIsUploading(false);
        }
    };

    const submitQuery = async (queryText) => {
        if (!queryText.trim() || !analysisResult) return;

        const userMessage = { sender: 'user', text: queryText };
        setChatHistory(prev => [...prev, userMessage]);
        setQuery('');
        setIsChatting(true);
        setView('chat');

        try {
            const response = await postQuery(queryText);
            const aiMessage = {
                sender: 'ai',
                answer: response.answer,
                suggested_followup: response.suggested_followup,
                relevant_logs: response.relevant_logs,
            };
            setChatHistory(prev => [...prev, aiMessage]);
        } catch (err) {
            setChatHistory(prev => [...prev, { sender: 'ai', answer: `Error: ${err.message}` }]);
        } finally {
            setIsChatting(false);
        }
    };

    const handleChatSubmit = (e) => {
        e.preventDefault();
        submitQuery(query);
    };
    
    const handleSuggestionClick = (suggestion) => {
        submitQuery(suggestion);
    };

    return (
        <div className="appContainer">
            <Sidebar
                fileName={fileName}
                onFileChange={handleFileChange}
                onAnalyze={handleUpload}
                isAnalyzing={isUploading}
                analysisProgress={uploadProgress}
                error={error}
                analysisResult={analysisResult}
            />

            <div className="mainContent">
                <div className='viewToggler'>
                    <button onClick={() => setView('dashboard')} className={view === 'dashboard' ? 'active' : ''} disabled={!analysisResult}>
                        <LayoutGrid size={14}/> Dashboard
                    </button>
                    <button onClick={() => setView('summary')} className={view === 'summary' ? 'active' : ''} disabled={!summaryReport}>
                        <MessageSquare size={14}/> Summary
                    </button>
                    <button onClick={() => setView('chat')} className={view === 'chat' ? 'active' : ''} disabled={!analysisResult}>
                        <MessageSquare size={14}/> Chat
                    </button>
                </div>

                {view === 'dashboard' && <DashboardView analysisResult={analysisResult} />}
                {view === 'summary' && <SummaryView summaryReport={summaryReport} />}
                {view === 'chat' && (
                    <>
                        <ChatView chatHistory={chatHistory} isChatting={isChatting} onSuggestionClick={handleSuggestionClick} />
                        <form className="chatInputForm" onSubmit={handleChatSubmit}>
                            <input
                                type="text"
                                className="inputField"
                                placeholder={analysisResult ? "Ask a question or try a suggestion..." : "Upload a file to enable chat"}
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                disabled={!analysisResult || isChatting}
                            />
                            <button
                                type="submit"
                                className="sendButton"
                                disabled={!analysisResult || isChatting || !query.trim()}
                            >
                                <Send size={18} />
                            </button>
                        </form>
                    </>
                )}
            </div>
        </div>
    );
}

export default App;
