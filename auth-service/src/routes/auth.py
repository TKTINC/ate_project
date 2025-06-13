"""
ATE Authentication Service - Authentication Routes
JWT-based authentication with multi-tenant support
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from datetime import datetime, timedelta
import uuid

from src.models.user import db, User, Tenant, RefreshToken, AuditLog

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user and organization"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'organization_name', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Create new tenant (organization)
        tenant = Tenant(
            name=data['organization_name'],
            organization=data['organization_name'],
            plan=data.get('plan', 'basic')
        )
        db.session.add(tenant)
        db.session.flush()  # Get tenant ID
        
        # Create new user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            tenant_id=tenant.id,
            role='admin',  # First user in organization is admin
            permissions=['tenant:manage', 'users:manage', 'analyses:create'],
            active=True,
            email_verified=False  # Would need email verification in production
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user.id,
            tenant_id=tenant.id,
            event_type='user_registered',
            event_data={'email': user.email, 'organization': tenant.name},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'tenant_id': user.tenant_id,
                'role': user.role,
                'permissions': user.permissions
            }
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'tenant': tenant.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return tokens"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            # Create audit log for failed login
            audit_log = AuditLog(
                event_type='login_failed',
                event_data={'email': data['email'], 'reason': 'invalid_credentials'},
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if user is active
        if not user.active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Check if tenant is active
        tenant = Tenant.query.get(user.tenant_id)
        if not tenant or not tenant.active:
            return jsonify({'error': 'Organization account is deactivated'}), 401
        
        # Update last login
        user.update_last_login()
        
        # Generate tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'tenant_id': user.tenant_id,
                'role': user.role,
                'permissions': user.permissions
            }
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        # Store refresh token
        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=refresh_token,  # In production, hash this
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(refresh_token_record)
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user.id,
            tenant_id=user.tenant_id,
            event_type='login_success',
            event_data={'email': user.email},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'tenant': tenant.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.active:
            return jsonify({'error': 'User not found or inactive'}), 404
        
        # Generate new access token
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'tenant_id': user.tenant_id,
                'role': user.role,
                'permissions': user.permissions
            }
        )
        
        return jsonify({
            'access_token': access_token
        })
        
    except Exception as e:
        return jsonify({'error': f'Token refresh failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user and revoke tokens"""
    try:
        current_user_id = get_jwt_identity()
        jti = get_jwt()['jti']  # JWT ID
        
        # Revoke all refresh tokens for this user
        refresh_tokens = RefreshToken.query.filter_by(user_id=current_user_id).all()
        for token in refresh_tokens:
            token.revoke()
        
        # Create audit log
        audit_log = AuditLog(
            user_id=current_user_id,
            event_type='logout',
            event_data={'jti': jti},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({'message': 'Logout successful'})
        
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token and return user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.active:
            return jsonify({'error': 'User account is deactivated'}), 401
        
        tenant = Tenant.query.get(user.tenant_id)
        if not tenant or not tenant.active:
            return jsonify({'error': 'Organization account is deactivated'}), 401
        
        return jsonify({
            'valid': True,
            'user': user.to_dict(),
            'tenant': tenant.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': f'Token verification failed: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Set new password
        user.set_password(data['new_password'])
        db.session.commit()
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user.id,
            tenant_id=user.tenant_id,
            event_type='password_changed',
            event_data={'email': user.email},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Password change failed: {str(e)}'}), 500

