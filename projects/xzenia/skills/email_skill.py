#!/usr/bin/env python3
"""
END-TO-END EMAIL SKILL
=======================
Learned from failures - executes email sending properly
"""
import subprocess
import time
import json
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')

class EmailSkill:
    """End-to-end email delivery skill with verification"""
    
    def __init__(self):
        self.log = []
    
    def pre_flight(self):
        """Check prerequisites"""
        # Check Chrome is running
        result = subprocess.run(['osascript', '-e', 'tell application "Google Chrome" to return name'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return {'status': 'fail', 'reason': 'Chrome not running'}
        
        return {'status': 'ready'}
    
    def open_compose(self, recipient, subject, body):
        """Open one compose window"""
        # URL encode the body
        body_encoded = body.replace(' ', '%20').replace('\n', '%0A')
        subject_encoded = subject.replace(' ', '%20')
        
        url = f"https://mail.google.com/mail/u/0/?view=cm&to={recipient}&su={subject_encoded}&body={body_encoded}"
        
        script = f'''
tell application \"Google Chrome\"
    activate
    open location \"{url}\"
end tell
'''
        subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=10)
        time.sleep(3)
        
        return {'status': 'opened', 'recipient': recipient}
    
    def request_user_click(self, recipient):
        """Request user to click send"""
        print(f"=== ACTION REQUIRED ===")
        print(f"Please click SEND for: {recipient}")
        print("=====================")
        return {'status': 'waiting_for_user'}
    
    def verify_delivery(self, recipient):
        """Verify email is in Sent folder"""
        # Open Sent folder
        script = 'tell application "Google Chrome" to open location "https://mail.google.com/mail/u/0/#sent"'
        subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=10)
        time.sleep(3)
        
        # Try to get content (JS may be disabled)
        script2 = '''
tell application "Google Chrome"
    tell active tab of first window
        try
            return execute javascript "document.body.innerText"
        on error
            return "JS_DISABLED"
        end try
    end tell
'''
        result = subprocess.run(['osascript', '-e', script2], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and result.stdout:
            content = result.stdout.lower()
            # Check for recipient in content
            email_part = recipient.split('@')[0]  # Check username part
            if email_part in content or recipient.lower() in content:
                return {'status': 'verified', 'method': 'js'}
        
        # JS disabled - return unknown
        return {'status': 'unknown', 'reason': 'JS disabled or email not found'}
    
    def log_operation(self, recipient, result, verification):
        """Log to operation log"""
        entry = {
            'recipient': recipient,
            'result': result,
            'verification': verification,
            'timestamp': time.time()
        }
        self.log.append(entry)
        
        # Save log
        log_file = WORKSPACE / 'state/email_log.json'
        log_file.write_text(json.dumps(self.log, indent=2))
    
    def execute(self, recipient, subject, body):
        """Execute end-to-end with user assistance"""
        # Step 1: Pre-flight
        pf = self.pre_flight()
        if pf['status'] == 'fail':
            return {'status': 'fail', 'reason': pf['reason']}
        
        # Step 2: Open compose
        self.open_compose(recipient, subject, body)
        
        # Step 3: Request user click (since automation doesn't work)
        self.request_user_click(recipient)
        
        # Step 4: Return instructions to user
        return {
            'status': 'user_action_required',
            'recipient': recipient,
            'instruction': 'Click the blue SEND button in Gmail compose'
        }


def send_email(recipient, subject, body):
    """Main entry point"""
    skill = EmailSkill()
    return skill.execute(recipient, subject, body)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) >= 4:
        recipient = sys.argv[1]
        subject = sys.argv[2]
        body = ' '.join(sys.argv[3:])
        
        result = send_email(recipient, subject, body)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: email_skill.py <recipient> <subject> <body>")