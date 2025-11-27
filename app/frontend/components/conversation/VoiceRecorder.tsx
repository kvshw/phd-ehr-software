/**
 * Voice Recorder Component
 * Records doctor-patient conversations and transcribes in real-time
 */
'use client';

import { useState, useEffect, useRef } from 'react';

interface VoiceRecorderProps {
  patientId: string;
  onTranscriptUpdate?: (transcript: string) => void;
  onSessionComplete?: (sessionId: string) => void;
}

type Speaker = 'doctor' | 'patient';

export function VoiceRecorder({ patientId, onTranscriptUpdate, onSessionComplete }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [currentSpeaker, setCurrentSpeaker] = useState<Speaker>('doctor');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [recognition, setRecognition] = useState<any>(null);
  const transcriptRef = useRef<string>('');

  // Initialize Web Speech API
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      
      if (!SpeechRecognition) {
        setError('Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.');
        return;
      }

      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = true;
      // Support multiple languages: English, Finnish, Swedish
      recognitionInstance.lang = 'en-US'; // Default, can be changed via language prop

      recognitionInstance.onresult = (event: any) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimTranscript += transcript;
          }
        }

        const speakerLabel = currentSpeaker === 'doctor' ? '[Doctor]' : '[Patient]';
        const newText = finalTranscript ? `${speakerLabel} ${finalTranscript.trim()}\n` : '';
        
        if (newText) {
          transcriptRef.current += newText;
          setTranscript(transcriptRef.current);
          
          // Send to backend
          if (sessionId) {
            sendTranscriptToBackend(newText.trim(), currentSpeaker);
          }
          
          if (onTranscriptUpdate) {
            onTranscriptUpdate(transcriptRef.current);
          }
        }
      };

      recognitionInstance.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        if (event.error === 'no-speech') {
          // Ignore no-speech errors (common when pausing)
          return;
        }
        setError(`Speech recognition error: ${event.error}`);
      };

      recognitionInstance.onend = () => {
        // Auto-restart if still recording
        if (isRecording) {
          try {
            recognitionInstance.start();
          } catch (e) {
            // Already started or error
          }
        }
      };

      setRecognition(recognitionInstance);
    }
  }, [currentSpeaker, isRecording, sessionId]);

  const startRecording = async () => {
    try {
      // Create conversation session
      const response = await fetch('http://localhost:8000/api/v1/conversations/sessions', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          patient_id: patientId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create conversation session');
      }

      const data = await response.json();
      setSessionId(data.id);
      transcriptRef.current = '';
      setTranscript('');

      // Start speech recognition
      if (recognition) {
        recognition.start();
        setIsRecording(true);
        setError(null);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to start recording');
      console.error('Error starting recording:', err);
    }
  };

  const stopRecording = async () => {
    if (recognition) {
      recognition.stop();
      setIsRecording(false);
    }

    // Finalize session
    if (sessionId) {
      try {
        await fetch(`http://localhost:8000/api/v1/conversations/sessions/${sessionId}/complete`, {
          method: 'POST',
          credentials: 'include',
        });

        // Trigger analysis
        await fetch(`http://localhost:8000/api/v1/conversations/sessions/${sessionId}/analyze`, {
          method: 'POST',
          credentials: 'include',
        });

        if (onSessionComplete) {
          onSessionComplete(sessionId);
        }
      } catch (err) {
        console.error('Error finalizing session:', err);
      }
    }
  };

  const sendTranscriptToBackend = async (text: string, speaker: Speaker) => {
    if (!sessionId || !text.trim()) return;

    try {
      await fetch(`http://localhost:8000/api/v1/conversations/transcripts`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          speaker: speaker,
          text: text.trim(),
        }),
      });
    } catch (err) {
      console.error('Error sending transcript:', err);
    }
  };

  const toggleSpeaker = () => {
    setCurrentSpeaker(currentSpeaker === 'doctor' ? 'patient' : 'doctor');
  };

  const clearTranscript = () => {
    transcriptRef.current = '';
    setTranscript('');
  };

  return (
    <div className="bg-white rounded-xl shadow border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-indigo-100">
            <svg className="h-5 w-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900">Voice Conversation</h2>
        </div>
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          Experimental
        </span>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Recording Controls */}
      <div className="mb-4 flex items-center gap-4">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={!!error}
          className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
            isRecording
              ? 'bg-red-600 text-white hover:bg-red-700'
              : 'bg-indigo-600 text-white hover:bg-indigo-700'
          } disabled:opacity-50 disabled:cursor-not-allowed shadow`}
        >
          {isRecording ? (
            <>
              <div className="h-3 w-3 bg-white rounded-full animate-pulse"></div>
              Stop Recording
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
              </svg>
              Start Recording
            </>
          )}
        </button>

        {/* Speaker Toggle */}
        <button
          onClick={toggleSpeaker}
          disabled={!isRecording}
          className={`px-4 py-2 rounded-lg border-2 font-medium transition-all ${
            currentSpeaker === 'doctor'
              ? 'border-blue-400 bg-blue-50 text-blue-700'
              : 'border-purple-400 bg-purple-50 text-purple-700'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {currentSpeaker === 'doctor' ? '👨‍⚕️ Doctor' : '👤 Patient'}
        </button>

        {transcript && (
          <button
            onClick={clearTranscript}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Clear
          </button>
        )}
      </div>

      {/* Recording Status */}
      {isRecording && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
          <div className="h-2 w-2 bg-red-600 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium text-red-800">Recording as {currentSpeaker === 'doctor' ? 'Doctor' : 'Patient'}...</span>
        </div>
      )}

      {/* Transcript Display */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 min-h-[200px] max-h-[400px] overflow-y-auto">
        {transcript ? (
          <div className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
            {transcript}
          </div>
        ) : (
          <div className="text-center text-gray-400 py-8">
            <svg className="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
            <p>Click "Start Recording" to begin transcribing the conversation</p>
            <p className="text-xs mt-2">Make sure to toggle between Doctor and Patient when speaking</p>
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-xs text-blue-800">
          <strong>Note:</strong> This feature uses browser speech recognition. For best results, use Chrome or Edge. 
          Toggle between Doctor and Patient roles when different speakers are talking.
        </p>
      </div>
    </div>
  );
}

