from app.database import db


class Contact(db.Model):
    __tablename__ = "contacts"

    # id = db.Column(db.Integer, primary_key=True)
    jnid = db.Column(db.String, primary_key=True)
    recid = db.Column(db.Integer, unique=True)

    # Basic info
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    display_name = db.Column(db.String(255))
    company = db.Column(db.String(255))

    # Classification
    record_type = db.Column(db.Integer, nullable=True)
    record_type_name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Integer, nullable=True)
    status_name = db.Column(db.String(50), nullable=False)

    # Optional fields
    customer = db.Column(db.Boolean)
    type = db.Column(db.String(50))
    external_id = db.Column(db.String(255))
    class_id = db.Column(db.String(255))
    class_name = db.Column(db.String(255))
    number = db.Column(db.String(255))
    created_by = db.Column(db.String(255))
    created_by_name = db.Column(db.String(255))
    date_created = db.Column(db.String(255))
    date_updated = db.Column(db.String(255))
    location = db.Column(db.String(255))
    is_active = db.Column(db.Boolean)
    rules = db.Column(db.Text)
    is_archived = db.Column(db.Boolean)
    owners = db.Column(db.Text)
    subcontractors = db.Column(db.Text)
    color = db.Column(db.String(50))
    date_start = db.Column(db.String(255))
    date_end = db.Column(db.String(255))
    tags = db.Column(db.Text)
    related = db.Column(db.Text)
    sales_rep = db.Column(db.String(255))
    sales_rep_name = db.Column(db.String(255))
    date_status_change = db.Column(db.String(255))
    description = db.Column(db.Text)

    # Address info
    address_line1 = db.Column(db.String(255))
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state_text = db.Column(db.String(255))
    zip = db.Column(db.String(50))
    country_name = db.Column(db.String(255))

    # Meta
    source = db.Column(db.String(255))
    source_name = db.Column(db.String, nullable=True)
    geo = db.Column(db.Text)
    image_id = db.Column(db.String(255))

    # Time tracking
    estimated_time = db.Column(db.Float)
    actual_time = db.Column(db.Float)
    task_count = db.Column(db.Integer)

    # Financials
    last_estimate = db.Column(db.Float)
    last_invoice = db.Column(db.Float)
    last_budget_gross_margin = db.Column(db.Float)
    last_budget_gross_profit = db.Column(db.Float)
    last_budget_revenue = db.Column(db.Float)

    # Flags
    is_lead = db.Column(db.Boolean)
    is_closed = db.Column(db.Boolean)
    is_sub_contractor = db.Column(db.Boolean)

    # Contact details
    email = db.Column(db.String(50))
    home_phone = db.Column(db.String(50))
    mobile_phone = db.Column(db.String(50))
    work_phone = db.Column(db.String(50))
    fax_number = db.Column(db.String(50))
    website = db.Column(db.String(255))

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
