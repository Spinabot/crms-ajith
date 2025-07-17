from datetime import datetime
from app import db

class SyncLog(db.Model):
    """Model to track synchronization between CRM systems"""
    __tablename__ = 'sync_logs'

    id = db.Column(db.Integer, primary_key=True)
    crm_system = db.Column(db.String(50), nullable=False)
    operation = db.Column(db.String(50), nullable=False)  # create, update, delete, sync
    status = db.Column(db.String(20), nullable=False)  # success, failed, pending
    lead_id = db.Column(
        db.Integer,
        db.ForeignKey('unified_leads.id', ondelete='SET NULL'),
        nullable=True
    )  # Made nullable for delete operations with ON DELETE SET NULL
    external_id = db.Column(db.String(100))
    error_message = db.Column(db.Text)
    sync_data = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lead = db.relationship('UnifiedLead', backref='sync_logs')

    def to_dict(self):
        return {
            'id': self.id,
            'crmSystem': self.crm_system,
            'operation': self.operation,
            'status': self.status,
            'leadId': self.lead_id,
            'externalId': self.external_id,
            'errorMessage': self.error_message,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }