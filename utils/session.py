from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class Session:
    initiator_id: int
    initiator_role: str
    status: str
    created_at: datetime
    expires_at: datetime
    initiator_limit: Optional[int] = None
    invited_id: Optional[int] = None
    invited_limit: Optional[int] = None

class SessionManager:
    def __init__(self, timeout_hours: int = 24):
        self.sessions: Dict[str, Session] = {}
        self.user_sessions: Dict[int, List[str]] = {}
        self.timeout_hours = timeout_hours
    
    def create_session(self, user_id: int, role: str) -> str:
        session_id = f"session_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        session = Session(
            initiator_id=user_id,
            initiator_role=role,
            status='pending',
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=self.timeout_hours)
        )
        self.sessions[session_id] = session
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        self.user_sessions[user_id].append(session_id)
        
        return session_id

    def get_session(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, **updates) -> None:
        if session_id in self.sessions:
            session = self.sessions[session_id]
            for key, value in updates.items():
                setattr(session, key, value)

    def end_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            self.sessions[session_id].status = 'ended'
            del self.sessions[session_id]

    def find_active_session(self, user_id: int) -> Optional[str]:
        for session_id, session in self.sessions.items():
            if ((session.initiator_id == user_id or session.invited_id == user_id) and
                session.status in ['pending', 'awaiting_updates']):
                if session.expires_at > datetime.now():
                    return session_id
                else:
                    session.status = 'expired'
                    return None
        return None

    def is_deal_successful(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if not session or not session.initiator_limit or not session.invited_limit:
            return False
            
        if session.initiator_role == 'buyer':
            buyer_limit = session.initiator_limit
            seller_limit = session.invited_limit
        else:
            buyer_limit = session.invited_limit
            seller_limit = session.initiator_limit
            
        return buyer_limit >= seller_limit