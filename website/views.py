from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


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

@views.route('/clients')
@login_required
def clients():
    # Example static data — replace this with a real database query
    clients = [
        {'id': 1, 'first_name': 'Alice', 'last_name': 'Smith', 'dob': '01/01/2010', 'email': 'alice@example.com', 'staff': 'Dr. Green'},
        {'id': 2, 'first_name': 'Bob', 'last_name': 'Johnson', 'dob': '03/15/2011', 'email': 'bob@example.com', 'staff': 'Dr. Lee'},
    ]
    return render_template("clients.html", clients=clients, user=current_user)
