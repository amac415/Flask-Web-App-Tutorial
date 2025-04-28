from website import create_app, db
from website.models import User

app = create_app()
with app.app_context():
    u = User.query.filter_by(email='andresmaciel5@gmail.com').first()
    if not u:
        print("User not found – check the email address")
    else:
        u.role = 'admin'
        db.session.commit()
        print(f"Promoted {u.email} to {u.role}")
