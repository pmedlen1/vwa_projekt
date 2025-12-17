import sqlite3
from typing import List, Dict, Any, Optional
from repositories.trainings import (
    list_trainings as repo_list_trainings, get_training as repo_get_training, insert_training as repo_insert_training,
    update_training as repo_update_training, delete_training as repo_delete_training,
    get_training_attendance as repo_get_training_attendance, set_training_attendance as repo_set_training_attendance,
)

class TrainingsService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_all_trainings(self) -> List[Dict[str, Any]]:
        return repo_list_trainings(self.conn)

    def get_training_by_id(self, training_id: int) -> Optional[Dict[str, Any]]:
        return repo_get_training(self.conn, training_id)

    def create_training(self, date: str, location: str, description: str, team_id: int = 1) -> int:
        return repo_insert_training(self.conn, date, location, description, team_id)

    def edit_training(self, training_id: int, date: str, location: str, description: str):
        repo_update_training(self.conn, training_id, date, location, description)

    def remove_training(self, training_id: int):
        repo_delete_training(self.conn, training_id)

#     UCAST

    def get_player_attendance(self, user_id: int, training_id: int) -> bool:
        att = repo_get_training_attendance(self.conn, user_id, training_id)
        if att and att['confirmed']:
            return True
        return False

    def confirm_attendance(self, user_id: int, training_id: int, confirmed: bool = True):
        repo_set_training_attendance(self.conn, user_id, training_id, confirmed)