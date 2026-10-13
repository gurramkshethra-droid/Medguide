from datetime import datetime, timezone
import json
from extensions import db

class Assessment(db.Model):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    symptoms_json = db.Column(db.Text, nullable=False)
    top_disease = db.Column(db.String(120), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    results_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    @property
    def symptoms_list(self):
        try:
            return json.loads(self.symptoms_json)
        except Exception:
            return []

    @property
    def results_list(self):
        try:
            return json.loads(self.results_json)
        except Exception:
            return []

    def __repr__(self):
        return f"<Assessment #{self.id} user={self.user_id} disease={self.top_disease}>"
