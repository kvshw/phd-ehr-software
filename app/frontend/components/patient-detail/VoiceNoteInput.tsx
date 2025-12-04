/**
 * Voice Note Input Component
 * Quick voice-to-text for clinical notes with medical terminology support
 */
'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

interface VoiceNoteInputProps {
  onTextChange: (text: string) => void;
  initialText?: string;
  placeholder?: string;
  language?: 'en-US' | 'fi-FI' | 'sv-SE'; // English, Finnish, Swedish
  className?: string;
}

export function VoiceNoteInput({
  onTextChange,
  initialText = '',
  placeholder = 'Start speaking or type your clinical notes...',
  language = 'en-US',
  className = '',
}: VoiceNoteInputProps) {
  const [text, setText] = useState(initialText);
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentLanguage, setCurrentLanguage] = useState(language);
  const recognitionRef = useRef<any>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Medical term expansions for voice input
  const medicalAbbreviations: Record<string, string> = {
    'bp': 'blood pressure',
    'hr': 'heart rate',
    'rr': 'respiratory rate',
    'o2 sat': 'oxygen saturation',
    'temp': 'temperature',
    'sob': 'shortness of breath',
    'cp': 'chest pain',
    'abd': 'abdominal',
    'hx': 'history',
    'rx': 'prescription',
    'dx': 'diagnosis',
    'tx': 'treatment',
    'sx': 'symptoms',
    'pt': 'patient',
    'prn': 'as needed',
    'bid': 'twice daily',
    'tid': 'three times daily',
    'qid': 'four times daily',
    'stat': 'immediately',
    'po': 'by mouth',
    'iv': 'intravenous',
    'im': 'intramuscular',
  };

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setIsSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = currentLanguage;

    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript + ' ';
        }
      }

      if (finalTranscript) {
        // Apply medical abbreviation expansion if enabled
        const processedText = processMedicalTerms(finalTranscript);
        
        setText(prev => {
          const newText = prev + processedText;
          onTextChange(newText);
          return newText;
        });
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      if (event.error !== 'no-speech') {
        setError(`Error: ${event.error}`);
      }
    };

    recognition.onend = () => {
      if (isListening) {
        try {
          recognition.start();
        } catch (e) {
          // Already started
        }
      }
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [currentLanguage, onTextChange]);

  // Update language when recognition is available
  useEffect(() => {
    if (recognitionRef.current) {
      recognitionRef.current.lang = currentLanguage;
    }
  }, [currentLanguage]);

  const processMedicalTerms = (text: string): string => {
    // Optionally expand medical abbreviations
    // For now, just return as-is (can be toggled by user preference)
    return text;
  };

  const toggleListening = useCallback(() => {
    if (!recognitionRef.current) return;

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setError(null);
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (e) {
        setError('Could not start voice recognition');
      }
    }
  }, [isListening]);

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value;
    setText(newText);
    onTextChange(newText);
  };

  const clearText = () => {
    setText('');
    onTextChange('');
  };

  const insertTemplate = (template: string) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const newText = text.substring(0, start) + template + text.substring(end);
    
    setText(newText);
    onTextChange(newText);
    
    // Move cursor to end of inserted text
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + template.length, start + template.length);
    }, 0);
  };

  const languageOptions = [
    { code: 'en-US', label: 'English (UK)', flag: 'EN' },
    { code: 'fi-FI', label: 'Suomi', flag: 'FI' },
    { code: 'sv-SE', label: 'Svenska', flag: 'SV' },
  ];

  const clinicalTemplates = [
    { label: 'SOAP', text: 'Subjective:\n\nObjective:\n\nAssessment:\n\nPlan:\n' },
    { label: 'HPI', text: 'Chief Complaint:\nHistory of Present Illness:\nOnset:\nLocation:\nDuration:\nCharacter:\nAggravating/Alleviating:\nRadiation:\nTiming:\nSeverity:\n' },
    { label: 'Physical Exam', text: 'General:\nVitals:\nHEENT:\nNeck:\nLungs:\nCardiac:\nAbdomen:\nExtremities:\nNeuro:\nSkin:\n' },
  ];

  return (
    <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-200 bg-gray-50 rounded-t-lg">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">Voice Notes</span>
          {!isSupported && (
            <span className="text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded">
              Voice not supported
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          {/* Language Selector */}
          <select
            value={currentLanguage}
            onChange={(e) => setCurrentLanguage(e.target.value as any)}
            className="text-xs border border-gray-300 rounded px-2 py-1 bg-white"
            disabled={isListening}
          >
            {languageOptions.map((opt) => (
              <option key={opt.code} value={opt.code}>
                {opt.label}
              </option>
            ))}
          </select>

          {/* Voice Button */}
          {isSupported && (
            <button
              onClick={toggleListening}
              className={`p-2 rounded-lg transition-all ${
                isListening
                  ? 'bg-red-100 text-red-600 hover:bg-red-200 ring-2 ring-red-300 ring-offset-1'
                  : 'bg-indigo-100 text-indigo-600 hover:bg-indigo-200'
              }`}
              title={isListening ? 'Stop listening' : 'Start voice input'}
            >
              {isListening ? (
                <div className="relative">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
                  </svg>
                  <span className="absolute -top-1 -right-1 h-2 w-2 bg-red-500 rounded-full animate-pulse"></span>
                </div>
              ) : (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                </svg>
              )}
            </button>
          )}

          {/* Clear Button */}
          {text && (
            <button
              onClick={clearText}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
              title="Clear text"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="px-3 py-2 bg-red-50 border-b border-red-100 text-xs text-red-600">
          {error}
        </div>
      )}

      {/* Recording Indicator */}
      {isListening && (
        <div className="px-3 py-2 bg-red-50 border-b border-red-100 flex items-center gap-2">
          <div className="h-2 w-2 bg-red-500 rounded-full animate-pulse"></div>
          <span className="text-xs font-medium text-red-700">
            Listening in {languageOptions.find(l => l.code === currentLanguage)?.label}...
          </span>
        </div>
      )}

      {/* Clinical Templates */}
      <div className="px-3 py-2 border-b border-gray-100 flex items-center gap-2 overflow-x-auto">
        <span className="text-xs text-gray-500 whitespace-nowrap">Templates:</span>
        {clinicalTemplates.map((template) => (
          <button
            key={template.label}
            onClick={() => insertTemplate(template.text)}
            className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 whitespace-nowrap"
          >
            {template.label}
          </button>
        ))}
      </div>

      {/* Textarea */}
      <textarea
        ref={textareaRef}
        value={text}
        onChange={handleTextChange}
        placeholder={placeholder}
        className="w-full p-3 min-h-[200px] text-sm text-gray-700 resize-y border-none focus:ring-0 focus:outline-none"
        style={{ fontFamily: 'ui-monospace, monospace' }}
      />

      {/* Footer Stats */}
      <div className="px-3 py-2 border-t border-gray-100 flex items-center justify-between text-xs text-gray-400 bg-gray-50 rounded-b-lg">
        <span>{text.length} characters</span>
        <span>{text.split(/\s+/).filter(Boolean).length} words</span>
      </div>
    </div>
  );
}

export default VoiceNoteInput;

