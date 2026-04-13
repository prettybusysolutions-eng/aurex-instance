#!/usr/bin/env python3
"""
Real-Time Screen Capture — System 1 Input
Captures screen for 5-second window (per Tesla Digital Optimus spec).
Uses macOS screencapture CLI.
"""
import subprocess
import time
import json
import base64
from pathlib import Path
from datetime import datetime, timezone
from collections import deque

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
CAPTURE_DIR = WORKSPACE / 'projects/xzenia/agents/outputs/screen_captures'
SCREEN_STATE = WORKSPACE / 'projects/xzenia/state/screen-buffer.json'

# 5-second window as per Digital Optimus spec
WINDOW_SECONDS = 5
CAPTURE_INTERVAL_MS = 1000  # 1 frame per second


class ScreenCapture:
    """Real-time screen capture with 5-second rolling buffer."""
    
    def __init__(self):
        self.buffer = deque(maxlen=WINDOW_SECONDS)
        self.capture_cmd = '/usr/sbin/screencapture'
        CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    
    def capture(self, filename: str = None) -> dict:
        """Capture single frame."""
        if filename is None:
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
            filename = f'frame_{timestamp}.png'
        
        filepath = CAPTURE_DIR / filename
        
        # Capture screen
        result = subprocess.run(
            [self.capture_cmd, '-x', str(filepath)],  # -x = no sound
            capture_output=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return {'success': False, 'error': result.stderr.decode()}
        
        # Get file info
        size = filepath.stat().st_size if filepath.exists() else 0
        
        frame = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'filename': filename,
            'path': str(filepath),
            'size_bytes': size
        }
        
        self.buffer.append(frame)
        
        return {'success': True, 'frame': frame}
    
    def capture_sequence(self, seconds: int = WINDOW_SECONDS) -> list:
        """Capture N seconds of screen."""
        frames = []
        start = time.time()
        
        while time.time() - start < seconds:
            frame = self.capture()
            if frame.get('success'):
                frames.append(frame['frame'])
            time.sleep(1)  # 1 fps
        
        return frames
    
    def get_window(self) -> list:
        """Get current 5-second window."""
        return list(self.buffer)
    
    def get_screen_context(self) -> dict:
        """Get context for System 1 decision."""
        window = self.get_window()
        
        # Calculate stability (simplified: would compare pixels in real impl)
        stable = len(window) >= WINDOW_SECONDS
        
        return {
            'window_seconds': len(window),
            'max_seconds': WINDOW_SECONDS,
            'screen_stable': stable,
            'frames': window,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def detect_change(self, frame1: dict, frame2: dict) -> bool:
        """Detect if two frames are different."""
        # Simple: compare file sizes (proxy for content change)
        return frame1.get('size_bytes') != frame2.get('size_bytes')


def run_continuous_capture(duration_seconds: int = 60):
    """Run continuous capture for N seconds."""
    capture = ScreenCapture()
    
    print(f"Starting continuous capture for {duration_seconds}s...")
    start = time.time()
    frames = []
    
    while time.time() - start < duration_seconds:
        result = capture.capture()
        if result.get('success'):
            frames.append(result['frame'])
            print(f"Captured frame {len(frames)}: {result['frame']['filename']}")
        time.sleep(1)
    
    context = capture.get_screen_context()
    
    print(f"\nCapture complete: {len(frames)} frames")
    print(f"Screen stable: {context['screen_stable']}")
    
    return context


if __name__ == '__main__':
    import sys
    
    capture = ScreenCapture()
    
    if len(sys.argv) == 1:
        # Single capture
        result = capture.capture()
        print(json.dumps(result, indent=2))
    
    elif sys.argv[1] == '--context':
        # Get screen context for System 1
        print(json.dumps(capture.get_screen_context(), indent=2))
    
    elif sys.argv[1] == '--window':
        # Get 5-second window
        print(json.dumps(capture.get_window(), indent=2))
    
    elif sys.argv[1] == '--continuous':
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        run_continuous_capture(duration)
    
    else:
        print('Usage: screen_capture.py [--context|--window|--continuous [seconds]]')
