from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Session:
    initiator_id: int
    initiator_role: str
    initiator_limit: Optional[int] = None
    participant_id: Optional[int] = None
    participant_limit: Optional[int] = None
    status: str = "waiting_for_limit"
    created_at: datetime = None
    expires_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(hours=24)

class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._user_sessions: Dict[int, List[str]] = {}
        
    def save_session(self, session_id: str, session: Session) -> None:
        self._sessions[session_id] = session
        if session.initiator_id:
            if session.initiator_id not in self._user_sessions:
                self._user_sessions[session.initiator_id] = []
            if session_id not in self._user_sessions[session.initiator_id]:
                self._user_sessions[session.initiator_id].append(session_id)
        if session.participant_id:
            if session.participant_id not in self._user_sessions:
                self._user_sessions[session.participant_id] = []
            if session_id not in self._user_sessions[session.participant_id]:
                self._user_sessions[session.participant_id].append(session_id)
        
    def get_session(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)
        
    def find_active_session(self, user_id: int) -> Optional[str]:
        if user_id not in self._user_sessions:
            return None
        for session_id in self._user_sessions[user_id]:
            if session_id in self._sessions:
                return session_id
        return None
        
    def delete_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            session = self._sessions[session_id]
            if session.initiator_id in self._user_sessions:
                self._user_sessions[session.initiator_id].remove(session_id)
            if session.participant_id and session.participant_id in self._user_sessions:
                self._user_sessions[session.participant_id].remove(session_id)
            del self._sessions[session_id]
            
    def get_user_sessions(self, user_id: int) -> List[str]:
        return self._user_sessions.get(user_id, [])
