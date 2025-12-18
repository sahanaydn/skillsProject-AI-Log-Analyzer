import React, { useRef } from 'react';
import { Upload, Loader, AlertTriangle, Cpu, CheckCircle2 } from 'lucide-react';

const ANALYSIS_STEPS = [ "Reading log file...", "Splitting data into chunks...", "Generating embeddings...", "Creating search index...", "Finalizing analysis..." ];

const Sidebar = ({
    apiKey,
    onApiKeyChange,
    fileName,
    onFileChange,
    onAnalyze,
    isAnalyzing,
    analysisProgress,
    error,
    analysisResult
}) => {
    const fileInputRef = useRef(null);

    return (
        <div className="sidebar">
            <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px'}}>
                <Cpu size={24}/>
                <h2>AI Log Analyzer</h2>
            </div>

            <div className="inputGroup">
                <label>Log File</label>
                <input 
                    type="file" 
                    ref={fileInputRef} 
                    className="fileInput" 
                    onChange={onFileChange} 
                    accept=".log,.txt" 
                />
                <button 
                    className="actionButton secondary" 
                    onClick={() => fileInputRef.current.click()}
                >
                    <Upload size={16} />
                    <span>{fileName || 'Select File'}</span>
                </button>
            </div>

            <button 
                className="actionButton" 
                onClick={onAnalyze} 
                disabled={isAnalyzing || !fileName}
            >
                {isAnalyzing ? <><Loader size={16} className="spinner"/> Analyzing...</> : 'Analyze & Visualize'}
            </button>

            <div className="statusArea">
                <strong>Analysis Status</strong>
                {isAnalyzing && (
                    <ul className='progressList'>
                        {analysisProgress.map((step, index) => (
                            <li key={index} className={`progressStep ${index < analysisProgress.length - 1 ? 'completed' : ''}`}>
                                {index < analysisProgress.length - 1 ? <CheckCircle2 size={16} color="var(--accent-color)" /> : <Loader size={16} className="spinner"/>}
                                <span>{step}</span>
                            </li>
                        ))}
                    </ul>
                )}
                {error && <p className="errorText"><AlertTriangle size={14} /> {error}</p>}
                {analysisResult && (
                    <div>
                        <p>Analysis complete. {analysisResult.total_lines} lines processed.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Sidebar;
