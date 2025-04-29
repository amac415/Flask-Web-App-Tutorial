from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from .models import Client
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash

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


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

from .models import Client

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        child_name   = request.form.get('child_name')
        parent_name  = request.form.get('parent_name')
        age          = int(request.form.get('age') or 0)
        email        = request.form.get('email')
        phone        = request.form.get('phone')
        county       = request.form.get('county')
        working_with = request.form.get('working_with')

        new_client = Client(
        child_name=child_name,
        parent_name=parent_name,
        age=age,
        email=email,
        phone=phone,
        county=county,
        working_with=working_with
    )
        db.session.add(new_client)
        db.session.commit()
        flash('New client added!', category='success')

    if current_user.role == 'admin':
        clients = Client.query.all()
    else:
        clients = Client.query.filter_by(staff=current_user.first_name).all()

    return render_template("clients.html", clients=clients, user=current_user)

@views.route('/delete-client', methods=['POST'])
@login_required
def delete_client():
    client_id = request.form.get('client_id')
    client = Client.query.get(client_id)

    if client:
        db.session.delete(client)
        db.session.commit()
        flash('Client deleted successfully!', category='success')
    else:
        flash('Client not found.', category='error')

    return redirect(url_for('views.clients'))
