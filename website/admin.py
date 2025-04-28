from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import User
from . import db
from .utils import admin_required

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
