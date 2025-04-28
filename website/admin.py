from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import User
from . import db
from .utils import admin_required
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    pending = User.query.filter_by(role='employee', approved=False).all()
    employees = User.query.filter_by(role='employee', approved=True).all()
    return render_template('admin/users.html', pending=pending, employees=employees, user=current_user)

@admin_bp.route('/approve-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.approved = True
    db.session.commit()
    flash(f'{user.email} approved.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/reject-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def reject_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'{user.email} rejected and removed.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/reset-password/<int:user_id>', methods=['GET','POST'])
@login_required
@admin_required
def reset_password(user_id):
    user_to_reset = User.query.get_or_404(user_id)
    if request.method == 'POST':
        new_pass = request.form['password']
        user_to_reset.password = generate_password_hash(new_pass, method='pbkdf2:sha256')
        db.session.commit()
        flash(f'Password for {user_to_reset.email} has been reset.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/reset_password.html',
                           user_to_reset=user_to_reset,
                           user=current_user)
@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash("Cannot delete an admin account.", "error")
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f"Deleted {user.email}", "success")
    return redirect(url_for('admin.users'))