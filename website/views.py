from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from .models import Client
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for


views = Blueprint('views', __name__)




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
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob = request.form.get('dob')
        email = request.form.get('email')
        staff = request.form.get('staff')

        new_client = Client(first_name=first_name, last_name=last_name, dob=dob, email=email, staff=staff)
        db.session.add(new_client)
        db.session.commit()
        flash('New client added!', category='success')

    clients = Client.query.all()
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
