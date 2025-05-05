from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash
from datetime import datetime
from .models import Parent, Child

views = Blueprint('views', __name__)

@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        pw1 = request.form.get('password1')
        pw2 = request.form.get('password2')
        # Validate name
        if len(first_name) < 2:
            flash('Name must be at least 2 characters.', 'error')
            return redirect(url_for('views.settings'))
        current_user.first_name = first_name
        # Handle password change if provided
        if pw1 or pw2:
            if pw1 != pw2:
                flash("Passwords don't match.", 'error')
                return redirect(url_for('views.settings'))
            if len(pw1) < 7:
                flash('Password must be at least 7 characters.', 'error')
                return redirect(url_for('views.settings'))
            current_user.password = generate_password_hash(pw1, method='pbkdf2:sha256')
        db.session.commit()
        flash('Settings saved!', 'success')
    return render_template('settings.html', user=current_user)




@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        # ──── 1) Grab parent fields ──────────────────────
        parent_name  = request.form.get('parent_name')
        phone        = request.form.get('phone')
        email        = request.form.get('email')
        county       = request.form.get('county')
        working_with = request.form.get('working_with')

        # Validate required parent fields:
        missing_parent = [f for f in ('parent_name','email') if not request.form.get(f)]
        if missing_parent:
            for f in missing_parent:
                flash(f"{f.replace('_',' ').title()} is required", 'error')
            return render_template('clients.html', parents=Parent.query.all(), user=current_user)

        # ──── 2) Grab child-1 fields ─────────────────────
        child1_name = request.form.get('child_name')
        child1_age  = request.form.get('age')
        if not child1_name:
            flash("Child’s name is required", 'error')
            return render_template('clients.html', parents=Parent.query.all(), user=current_user)

        # ──── 3) Create Parent, then Child ──────────────
        new_parent = Parent(
            parent_name=parent_name,
            phone=phone,
            email=email,
            county=county,
            working_with=working_with,
            staff_id=current_user.id
        )
        db.session.add(new_parent)
        db.session.flush()   # this assigns new_parent.id

        new_child = Child(
            parent_id=new_parent.id,
            first_name=child1_name,
            age=int(child1_age) if child1_age and child1_age.isdigit() else None
        )
        db.session.add(new_child)

        db.session.commit()
        flash('New client and child added!', 'success')
        return redirect(url_for('views.home'))

    # ──── 4) List parents based on role ─────────────
    if current_user.role == 'admin':
        parents = Parent.query.all()
    else:
        parents = Parent.query.filter_by(staff_id=current_user.id).all()

    return render_template("clients.html", parents=parents, user=current_user)


from .utils import admin_required
@views.route('/add-client', methods=['GET','POST'])
@login_required
def add_client():
    if request.method == 'POST':
        # 1) Validate Parent fields
        required_parent = ['parent_name','email','address','language','ethnicity']
        missing_parent = [f for f in required_parent if not request.form.get(f)]
        if missing_parent:
            for f in missing_parent:
                flash(f"{f.replace('_',' ').title()} is required", 'error')
            return render_template('add_client.html', user=current_user)

        # 2) Validate at least child1 presence
        if not (request.form.get('child1_first_name') and request.form.get('child1_last_name')):
            flash("At least Child 1's First and Last Name are required", 'error')
            return render_template('add_client.html', user=current_user)

        # ─── Services Seeking ─────────────────────────────────────────────
        # grab all checked services
        services = request.form.getlist('services_seeking')
        other    = request.form.get('services_other','').strip()
        if 'Other' in services and other:
            # replace “Other” placeholder with the actual text
            services = [s for s in services if s!='Other']
            services.append(f"Other: {other}")

        services_str = ', '.join(services)  # e.g. "Childcare, Food Assistance, Other: Adult Ed"
        # ──────────────────────────────────────────────────────────────────

        # Helper to parse dates
        def parse_date(name):
            v = request.form.get(name)
            return datetime.strptime(v, '%Y-%m-%d').date() if v else None

        # 3) Create Parent (now including services_seeking)
        parent = Parent(
            parent_name     = request.form['parent_name'],
            phone           = request.form.get('phone'),
            email           = request.form['email'],
            address         = request.form['address'],
            zipcode         = request.form.get('zipcode'),
            relationship    = request.form.get('relationship'),
            language        = request.form['language'],
            ethnicity       = request.form['ethnicity'],
            services_seeking= services_str,       # ← here
            staff_id        = current_user.id
        )
        db.session.add(parent)
        db.session.flush()  # assigns parent.id

        # 4) Loop over up to 3 children
        for i in (1,2,3):
            fn = request.form.get(f'child{i}_first_name')
            ln = request.form.get(f'child{i}_last_name')
            if fn and ln:
                child = Child(
                    parent_id     = parent.id,
                    first_name    = fn,
                    last_name     = ln,
                    dob           = parse_date(f'child{i}_dob'),
                    gender        = request.form.get(f'child{i}_gender'),
                    language      = request.form[f'child{i}_language'],
                    ethnicity     = request.form[f'child{i}_ethnicity'],
                    insurance     = request.form.get(f'child{i}_insurance'),
                    doctor_visit  = request.form.get(f'child{i}_doctor_visit'),
                    dentist_visit = request.form.get(f'child{i}_dentist_visit'),
                    working_with  = request.form.get(f'child{i}_working_with'),
                    disability    = request.form.get(f'child{i}_disability'),
                )
                db.session.add(child)

        # 5) Commit all
        db.session.commit()
        flash('Client and children added!', 'success')
        return redirect(url_for('views.home'))

    return render_template('add_client.html', user=current_user)

@views.route('/delete-client', methods=['POST'])
@login_required
def delete_client():
    parent_id = request.form.get('client_id')
    parent    = Parent.query.get(parent_id)
    if parent:
        db.session.delete(parent)
        db.session.commit()
        flash('Client deleted successfully!', 'success')
    else:
        flash('Client not found.', 'error')
    return redirect(url_for('views.home'))

@views.route('/view-client/<int:parent_id>')
@login_required
def view_client(parent_id):
    parent = Parent.query.get_or_404(parent_id)
    # Ensure non-admin staff only see their own clients
    if current_user.role != 'admin' and parent.staff_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('views.home'))
    return render_template('view_client.html', parent=parent, user=current_user)

