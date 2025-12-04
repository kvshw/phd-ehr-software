/**
 * Conversation Transcript Component
 * Displays full conversation transcript with speaker identification
 */
'use client';

import { useState, useEffect } from 'react';
import { conversationService, ConversationSessionWithAnalysis } from '@/lib/conversationService';

interface ConversationTranscriptProps {
  sessionId: string;
}

export function ConversationTranscript({ sessionId }: ConversationTranscriptProps) {
  const [session, setSession] = useState<ConversationSessionWithAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSession();
  }, [sessionId]);

  const fetchSession = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await conversationService.getSession(sessionId);
      setSession(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load conversation');
      console.error('Error fetching session:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow border border-gray-200 p-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow border border-gray-200 p-6">
        <div className="text-red-600">{error}</div>
      </div>
    );
  }

  if (!session) {
    return null;
  }

  return (
    <div className="bg-white rounded-xl shadow border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-indigo-100">
            <svg className="h-5 w-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900">Conversation Transcript</h2>
        </div>
        <span className="text-xs text-gray-500">
          {new Date(session.session_date).toLocaleString()}
        </span>
      </div>

      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-[500px] overflow-y-auto">
        {session.transcripts && session.transcripts.length > 0 ? (
          <div className="space-y-3">
            {session.transcripts.map((transcript) => (
              <div
                key={transcript.id}
                className={`p-3 rounded-lg ${
                  transcript.speaker === 'doctor'
                    ? 'bg-blue-50 border-l-4 border-blue-400'
                    : 'bg-purple-50 border-l-4 border-purple-400'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-semibold">
                    {transcript.speaker === 'doctor' ? 'Doctor' : 'Patient'}
                  </span>
                  {transcript.timestamp_seconds && (
                    <span className="text-xs text-gray-500">
                      {Math.floor(transcript.timestamp_seconds / 60)}:{(transcript.timestamp_seconds % 60).toString().padStart(2, '0')}
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-700">{transcript.text}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-gray-400 py-8">
            <p>No transcripts available</p>
          </div>
        )}
      </div>
    </div>
  );
}

