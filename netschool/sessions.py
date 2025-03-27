import os
import json

from netschoolapi.session import Session


class NSSession:
    def __init__(self, sessions_path: str):
        self.sessions_path = sessions_path
        os.makedirs(sessions_path, exist_ok=True)

    def save(self, user_id: int, session: Session):
        session_json = session.to_json()

        path = os.path.join(self.sessions_path, f"{user_id}.json")

        with open(path, "w") as f:
            json.dump(session_json, f)

    def get(self, user_id: int):
        path = os.path.join(self.sessions_path, f"{user_id}.json")
        if os.path.exists(path):
            return Session.from_json(path)
