from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Session:
    initiator_id: int
    initiator_role: str
    initiator_limit: Optional[int]
    participant_id: Optional[int]
    participant_limit: Optional[int]
    status: str

class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        
    def save_session(self, session_id: str, session: Session) -> None:
        self._sessions[session_id] = session
        
    def get_session(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)
        
    def find_active_session(self, user_id: int) -> Optional[str]:
        for session_id, session in self._sessions.items():
            if session.initiator_id == user_id or session.participant_id == user_id:
                return session_id
        return None
        
    def delete_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]
