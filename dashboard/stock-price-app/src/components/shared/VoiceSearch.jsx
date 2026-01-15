import { useState, useEffect, useCallback } from 'react';

/**
 * Voice Search Component
 * Uses Web Speech API for speech-to-text conversion
 * Integrates with Smart Search for AI-powered query processing
 */
export default function VoiceSearch({ onSearch, onTranscript, disabled = false }) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(true);
  const [error, setError] = useState(null);

  // Check for browser support
  useEffect(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setIsSupported(false);
      setError('Voice recognition is not supported in this browser. Try Chrome or Edge.');
    }
  }, []);

  const startListening = useCallback(() => {
    if (!isSupported || disabled) return;

    setError(null);
    setTranscript('');

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      const currentTranscript = finalTranscript || interimTranscript;
      setTranscript(currentTranscript);

      if (onTranscript) {
        onTranscript(currentTranscript);
      }

      // If we have a final transcript, trigger search
      if (finalTranscript && onSearch) {
        onSearch(finalTranscript);
      }
    };

    recognition.onerror = (event) => {
      setIsListening(false);
      switch (event.error) {
        case 'no-speech':
          setError('No speech detected. Please try again.');
          break;
        case 'audio-capture':
          setError('No microphone found. Please check your microphone.');
          break;
        case 'not-allowed':
          setError('Microphone access denied. Please allow microphone access.');
          break;
        default:
          setError(`Error: ${event.error}`);
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    try {
      recognition.start();
    } catch (err) {
      setError('Failed to start voice recognition');
      setIsListening(false);
    }
  }, [isSupported, disabled, onSearch, onTranscript]);

  const stopListening = useCallback(() => {
    setIsListening(false);
  }, []);

  if (!isSupported) {
    return (
      <div style={{ color: '#ef4444', fontSize: '12px', padding: '8px' }}>
        {error}
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      {/* Microphone Button */}
      <button
        onClick={isListening ? stopListening : startListening}
        disabled={disabled}
        style={{
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          border: 'none',
          background: isListening
            ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
            : 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
          color: 'white',
          cursor: disabled ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.3s ease',
          boxShadow: isListening
            ? '0 0 20px rgba(239, 68, 68, 0.5)'
            : '0 4px 12px rgba(59, 130, 246, 0.3)',
          animation: isListening ? 'pulse 1.5s infinite' : 'none',
          opacity: disabled ? 0.5 : 1,
        }}
        title={isListening ? 'Stop listening' : 'Start voice search'}
      >
        {isListening ? (
          // Stop icon
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="6" width="12" height="12" rx="2" />
          </svg>
        ) : (
          // Microphone icon
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
          </svg>
        )}
      </button>

      {/* Status/Transcript Display */}
      <div style={{ flex: 1, minWidth: 0 }}>
        {isListening && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: '#ef4444',
            fontSize: '14px',
            fontWeight: '500',
          }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#ef4444',
              animation: 'blink 1s infinite',
            }} />
            Listening...
          </div>
        )}

        {transcript && (
          <div style={{
            color: '#64748b',
            fontSize: '14px',
            fontStyle: 'italic',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}>
            "{transcript}"
          </div>
        )}

        {error && (
          <div style={{
            color: '#ef4444',
            fontSize: '12px',
          }}>
            {error}
          </div>
        )}
      </div>

      {/* CSS Animations */}
      <style>{`
        @keyframes pulse {
          0% { transform: scale(1); }
          50% { transform: scale(1.05); }
          100% { transform: scale(1); }
        }
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
      `}</style>
    </div>
  );
}
