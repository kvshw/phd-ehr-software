/**
 * Conversation Section Component
 * Main component for voice conversation recording and viewing
 */
'use client';

import { useState, useEffect } from 'react';
import { VoiceRecorder } from './VoiceRecorder';
import { ConversationTranscript } from './ConversationTranscript';
import { ConversationSummary } from './ConversationSummary';
import { conversationService, ConversationSession } from '@/lib/conversationService';

interface ConversationSectionProps {
  patientId: string;
}

export function ConversationSection({ patientId }: ConversationSectionProps) {
  const [sessions, setSessions] = useState<ConversationSession[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessions();
  }, [patientId]);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const data = await conversationService.getPatientSessions(patientId, 10);
      setSessions(data);
      if (data.length > 0 && !selectedSessionId) {
        setSelectedSessionId(data[0].id);
      }
    } catch (err) {
      console.error('Error fetching sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSessionComplete = (sessionId: string) => {
    setSelectedSessionId(sessionId);
    fetchSessions(); // Refresh sessions list
  };

  return (
    <div className="space-y-6">
      {/* Voice Recorder */}
      <VoiceRecorder
        patientId={patientId}
        onSessionComplete={handleSessionComplete}
      />

      {/* Previous Sessions */}
      {sessions.length > 0 && (
        <div className="bg-white rounded-xl shadow border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Previous Conversations</h3>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => setSelectedSessionId(session.id)}
                className={`w-full text-left p-3 rounded-lg border transition-all ${
                  selectedSessionId === session.id
                    ? 'border-indigo-400 bg-indigo-50'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {new Date(session.session_date).toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500">
                      Status: {session.status} {session.duration_seconds && `• ${Math.floor(session.duration_seconds / 60)} min`}
                    </p>
                  </div>
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Selected Session Details */}
      {selectedSessionId && (
        <div className="space-y-6">
          <ConversationTranscript sessionId={selectedSessionId} />
          <ConversationSummary sessionId={selectedSessionId} />
        </div>
      )}
    </div>
  );
}

