'use client';

import { useState, useEffect } from 'react';
import { timetableAPI } from '@/lib/api';

interface GenerationSession {
  session_id: string;
  status: 'started' | 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
  start_time: string;
  current_stage?: string;
  generation_time?: number;
  evaluation_score?: number;
  timetable_id?: string;
  conflicts?: string[];
  suggestions?: string[];
}

interface GenerationRequest {
  schoolId: string;
  academicYearId: string;
  name: string;
  description?: string;
  startDate: string;
  endDate: string;
  engineVersion: string;
  periodsPerDay: number;
  daysPerWeek: number;
  periodDuration: number;
  breakDuration: number;
  lunchDuration: number;
  constraints: Record<string, any>;
  hardRules: Record<string, boolean>;
  softRules: Record<string, boolean>;
}

interface Props {
  initialRequest: GenerationRequest;
  onComplete?: (session: GenerationSession) => void;
  onError?: (error: string) => void;
}

export default function EnhancedTimetableGenerator({ initialRequest, onComplete, onError }: Props) {
  const [session, setSession] = useState<GenerationSession | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `${timestamp}: ${message}`]);
  };

  const startGeneration = async () => {
    try {
      setIsGenerating(true);
      setSession(null);
      setLogs([]);
      
      addLog('🚀 Starting timetable generation with Engine v3.5...');
      
      // Start generation
      const response = await timetableAPI.engineGenerate(initialRequest);
      const newSession = response.data;
      
      setSession(newSession);
      addLog(`✅ Generation session started: ${newSession.session_id}`);
      
      // Start polling for status
      pollStatus(newSession.session_id);
      
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to start generation';
      addLog(`❌ Generation failed: ${errorMessage}`);
      onError?.(errorMessage);
      setIsGenerating(false);
    }
  };

  const pollStatus = async (sessionId: string) => {
    const maxAttempts = 120; // 2 minutes max
    let attempts = 0;
    
    const poll = async () => {
      try {
        attempts++;
        const response = await timetableAPI.getGenerationStatus(sessionId);
        const status = response.data;
        
        setSession(status);
        addLog(`📊 ${status.current_stage || status.status}: ${status.message} (${status.progress}%)`);
        
        if (status.status === 'completed') {
          addLog('🎉 Generation completed successfully!');
          setIsGenerating(false);
          
          // Fetch full results
          try {
            const resultResponse = await timetableAPI.getGenerationResult(sessionId);
            const fullSession = { ...status, ...resultResponse.data };
            setSession(fullSession);
            onComplete?.(fullSession);
            addLog(`📈 Final score: ${fullSession.evaluation_score?.toFixed(2)}`);
          } catch (resultError) {
            console.error('Failed to fetch full results:', resultError);
          }
          
        } else if (status.status === 'failed') {
          addLog('❌ Generation failed');
          setIsGenerating(false);
          onError?.(status.message);
          
        } else if (attempts < maxAttempts) {
          // Continue polling
          setTimeout(poll, 1000);
        } else {
          addLog('⏰ Generation timeout');
          setIsGenerating(false);
          onError?('Generation timeout');
        }
        
      } catch (error) {
        console.error('Polling error:', error);
        if (attempts < maxAttempts) {
          setTimeout(poll, 2000); // Slower retry on error
        } else {
          setIsGenerating(false);
          onError?('Failed to check generation status');
        }
      }
    };
    
    poll();
  };

  const getProgressColor = (progress: number) => {
    if (progress < 30) return 'bg-blue-500';
    if (progress < 70) return 'bg-yellow-500'; 
    return 'bg-green-500';
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'started': return '🚀';
      case 'running': return '⚙️';
      case 'completed': return '✅';
      case 'failed': return '❌';
      default: return '⏳';
    }
  };

  return (
    <div className="space-y-6">
      {/* Generation Control */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-gray-900">
            Timetable Engine v3.5
          </h2>
          <button
            onClick={startGeneration}
            disabled={isGenerating}
            className={`px-4 py-2 rounded-md font-medium ${
              isGenerating
                ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isGenerating ? (
              <>
                <span className="inline-block animate-spin mr-2">⚙️</span>
                Generating...
              </>
            ) : (
              'Start Generation'
            )}
          </button>
        </div>

        <div className="text-sm text-gray-600">
          <p>Using production-ready engine with:</p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>CSP Constraint Solver</li>
            <li>Quality Evaluation System</li>
            <li>Solution Ranking & Comparison</li>
            <li>Genetic Algorithm Optimization</li>
            <li>Intelligent Caching</li>
          </ul>
        </div>
      </div>

      {/* Progress Display */}
      {session && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              {getStatusIcon(session.status)} Generation Progress
            </h3>
            <span className="text-sm text-gray-500">
              Session: {session.session_id.split('_')[1]}
            </span>
          </div>

          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>{session.current_stage || session.status}</span>
              <span>{session.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all duration-500 ${getProgressColor(session.progress)}`}
                style={{ width: `${session.progress}%` }}
              />
            </div>
          </div>

          {/* Status Message */}
          <p className="text-sm text-gray-700 mb-4">{session.message}</p>

          {/* Results Summary */}
          {session.status === 'completed' && (
            <div className="border-t pt-4">
              <h4 className="font-medium text-gray-900 mb-2">Generation Results</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-600">Generation Time:</span>
                  <span className="ml-2">{session.generation_time?.toFixed(2)}s</span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Quality Score:</span>
                  <span className="ml-2">{session.evaluation_score?.toFixed(1)}/1000</span>
                </div>
              </div>
            </div>
          )}

          {/* Conflicts & Suggestions */}
          {session.status === 'failed' && (session.conflicts || session.suggestions) && (
            <div className="border-t pt-4">
              {session.conflicts && session.conflicts.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-medium text-red-800 mb-2">❌ Issues Found</h4>
                  <ul className="space-y-1">
                    {session.conflicts.map((conflict, index) => (
                      <li key={index} className="text-sm text-red-700 bg-red-50 p-2 rounded">
                        • {conflict}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {session.suggestions && session.suggestions.length > 0 && (
                <div>
                  <h4 className="font-medium text-blue-800 mb-2">💡 Suggestions</h4>
                  <ul className="space-y-1">
                    {session.suggestions.map((suggestion, index) => (
                      <li key={index} className="text-sm text-blue-700 bg-blue-50 p-2 rounded">
                        ▶ {suggestion}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Generation Logs */}
      {logs.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Generation Log</h3>
          <div className="bg-gray-900 text-green-400 p-4 rounded-md font-mono text-sm max-h-64 overflow-y-auto">
            {logs.map((log, index) => (
              <div key={index} className="mb-1">
                {log}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System Info */}
      <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
        <h4 className="font-medium mb-2">Engine Information</h4>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <strong>Version:</strong> 3.5.0
          </div>
          <div>
            <strong>API Endpoint:</strong> localhost:8000
          </div>
          <div>
            <strong>Components:</strong> CSP + GA + Evaluation
          </div>
          <div>
            <strong>Data Source:</strong> Real CSV Import
          </div>
        </div>
      </div>
    </div>
  );
}