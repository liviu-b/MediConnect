import resend
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from ..config import RESEND_API_KEY, DEFAULT_FROM_EMAIL, FRONTEND_URL

logger = logging.getLogger("mediconnect")

# Initialize Resend
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
    logger.info("Resend API initialized successfully")
else:
    logger.warning("RESEND_API_KEY not set - email functionality will be disabled")


def _send_email(to: str, subject: str, html: str, text: str) -> Dict[str, Any]:
    """
    Internal helper to send email via Resend.
    Returns dict with success status and optional error.
    """
    if not RESEND_API_KEY:
        logger.warning(f"Email not sent to {to} - RESEND_API_KEY not configured")
        return {"success": False, "error": "Email service not configured"}
    
    try:
        response = resend.Emails.send({
            "from": DEFAULT_FROM_EMAIL,
            "to": to,
            "subject": subject,
            "html": html,
            "text": text
        })
        logger.info(f"Email sent successfully to {to} - ID: {response.get('id', 'unknown')}")
        return {"success": True, "email_id": response.get('id')}
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {str(e)}")
        return {"success": False, "error": str(e)}


def _get_email_header(center_name: str = "MediConnect") -> str:
    """Generate consistent email header HTML."""
    return f"""
<div style="background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%); padding: 30px; text-align: center;">
    <h1 style="color: white; margin: 0; font-size: 28px;">{center_name}</h1>
</div>
"""


def _get_email_footer() -> str:
    """Generate consistent email footer HTML."""
    return """
<div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center;">
    <p style="color: #9ca3af; font-size: 12px; margin: 5px 0;">
        This is an automated message from MediConnect. Please do not reply to this email.
    </p>
    <p style="color: #9ca3af; font-size: 12px; margin: 5px 0;">
        © 2025 MediConnect. All rights reserved.
    </p>
</div>
"""


def _wrap_email_content(header: str, body: str, footer: str) -> str:
    """Wrap email content in consistent HTML structure."""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; background-color: #f5f7fa; margin: 0; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        {header}
        <div style="padding: 40px 30px;">
            {body}
            {footer}
        </div>
    </div>
</body>
</html>"""


def send_password_reset_email(recipient_email: str, recipient_name: str, reset_link: str, medical_center: dict | None = None):
    try:
        center_name = medical_center.get('name', 'MediConnect') if medical_center else 'MediConnect'
        html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; background-color: #f5f7fa; margin: 0; padding: 20px;">
<div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden;">
<div style="background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%); padding: 30px; text-align: center;">
<h1 style="color: white; margin: 0;">{center_name}</h1>
</div>
<div style="padding: 40px 30px;">
<h2 style="color: #1f2937;">Resetare Parolă</h2>
<p style="color: #4b5563;">Bună ziua {recipient_name},</p>
<p style="color: #4b5563;">Apăsați butonul de mai jos pentru a vă reseta parola.</p>
<div style="text-align: center; margin: 30px 0;">
<a href="{reset_link}" style="background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%); color: white; text-decoration: none; padding: 14px 40px; border-radius: 8px; font-weight: 600;">Resetează Parola</a>
</div>
<p style="color: #6b7280; font-size: 14px;">Sau copiați acest link: {reset_link}</p>
<p style="color: #9ca3af; font-size: 12px;">Acest link expiră în 1 oră.</p>
</div>
</div>
</body>
</html>"""
        text_content = f"Resetare Parolă\n\nBună ziua {recipient_name},\n\nResetați parola: {reset_link}\n\nAcest link expiră în 1 oră."
        resend.Emails.send({
            "from": DEFAULT_FROM_EMAIL,
            "to": recipient_email,
            "subject": f"Resetare Parolă - {center_name}",
            "html": html_content,
            "text": text_content
        })
        logger.info(f"Password reset email sent to {recipient_email}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to send password reset email: {str(e)}")
        return {"success": False, "error": str(e)}


def send_staff_invitation_email(recipient_email: str, recipient_name: str, role: str, invitation_link: str, clinic_name: str, inviter_name: str):
    try:
        role_display = {
            'DOCTOR': 'Doctor',
            'ASSISTANT': 'Asistent Medical',
            'RECEPTIONIST': 'Recepționer',
            'NURSE': 'Asistent',
            'ADMIN': 'Administrator',
            'LOCATION_ADMIN': 'Administrator Locație'
        }.get(role, role)
        html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; background-color: #f5f7fa; margin: 0; padding: 20px;">
<div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden;">
<div style="background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%); padding: 30px; text-align: center;">
<h1 style="color: white; margin: 0;">{clinic_name}</h1>
</div>
<div style="padding: 40px 30px;">
<h2 style="color: #1f2937;">Sunteți invitat să vă alăturați {clinic_name}</h2>
<p style="color: #4b5563;">Bună ziua {recipient_name},</p>
<p style="color: #4b5563;">{inviter_name} v-a invitat să vă alăturați <strong>{clinic_name}</strong> ca <strong>{role_display}</strong> pe MediConnect.</p>
<p style="color: #4b5563;">Apăsați butonul de mai jos pentru a accepta invitația și a vă configura contul:</p>
<div style="text-align: center; margin: 30px 0;">
<a href="{invitation_link}" style="background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%); color: white; text-decoration: none; padding: 14px 40px; border-radius: 8px; font-weight: 600;">Acceptă Invitația</a>
</div>
<p style="color: #6b7280; font-size: 14px;">Sau copiați acest link: {invitation_link}</p>
<p style="color: #9ca3af; font-size: 12px;">Această invitație expiră în 7 zile.</p>
</div>
</div>
</body>
</html>"""
        text_content = f"Invitație Personal\n\nBună ziua {recipient_name},\n\n{inviter_name} v-a invitat să vă alăturați {clinic_name} ca {role_display}.\n\nAcceptați invitația: {invitation_link}\n\nAceastă invitație expiră în 7 zile."
        resend.Emails.send({
            "from": DEFAULT_FROM_EMAIL,
            "to": recipient_email,
            "subject": f"Invitație de a vă alătura {clinic_name} - MediConnect",
            "html": html_content,
            "text": text_content
        })
        logger.info(f"Staff invitation email sent to {recipient_email}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to send staff invitation email: {str(e)}")
        return {"success": False, "error": str(e)}


def send_cancellation_notification_email(patient_email: str, patient_name: str, doctor_name: str, clinic_name: str, appointment_date: str, cancellation_reason: str):
    """Send appointment cancellation notification to patient."""
    try:
        try:
            dt = datetime.fromisoformat(appointment_date.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%B %d, %Y at %H:%M")
        except Exception:
            formatted_date = appointment_date
        
        header = _get_email_header("Appointment Cancelled")
        body = f"""
<p style="color: #4b5563; font-size: 16px;">Hello {patient_name},</p>
<p style="color: #4b5563;">We regret to inform you that your appointment has been cancelled.</p>

<div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
    <p style="margin: 5px 0; color: #374151;"><strong>Doctor:</strong> Dr. {doctor_name}</p>
    <p style="margin: 5px 0; color: #374151;"><strong>Clinic:</strong> {clinic_name}</p>
    <p style="margin: 5px 0; color: #374151;"><strong>Original Date:</strong> {formatted_date}</p>
</div>

<div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; border-radius: 4px;">
    <p style="margin: 0; color: #991b1b; font-weight: 600;">Reason for Cancellation:</p>
    <p style="margin: 5px 0 0 0; color: #7f1d1d;">{cancellation_reason}</p>
</div>

<p style="color: #4b5563;">Please contact us or book a new appointment at your convenience.</p>
<p style="color: #6b7280; font-size: 14px;">We apologize for any inconvenience caused.</p>
"""
        footer = _get_email_footer()
        html_content = _wrap_email_content(header, body, footer)
        
        text_content = f"""Appointment Cancelled

Hello {patient_name},

Your appointment with Dr. {doctor_name} at {clinic_name} on {formatted_date} has been cancelled.

Reason: {cancellation_reason}

Please contact us or book a new appointment at your convenience.

We apologize for any inconvenience caused."""
        
        return _send_email(
            to=patient_email,
            subject=f"Appointment Cancelled - {clinic_name}",
            html=html_content,
            text=text_content
        )
    except Exception as e:
        logger.error(f"Failed to send cancellation email: {str(e)}")
        return {"success": False, "error": str(e)}


def send_appointment_confirmation_email(
    patient_email: str,
    patient_name: str,
    doctor_name: str,
    clinic_name: str,
    appointment_date: str,
    appointment_id: str,
    clinic_address: Optional[str] = None
):
    """Send appointment confirmation email to patient."""
    try:
        try:
            dt = datetime.fromisoformat(appointment_date.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%B %d, %Y")
            formatted_time = dt.strftime("%H:%M")
        except Exception:
            formatted_date = appointment_date
            formatted_time = ""
        
        header = _get_email_header(clinic_name)
        
        address_html = ""
        if clinic_address:
            address_html = f'<p style="margin: 5px 0; color: #374151;"><strong>Address:</strong> {clinic_address}</p>'
        
        body = f"""
<h2 style="color: #1f2937; margin-bottom: 10px;">Appointment Confirmed! ✓</h2>
<p style="color: #4b5563; font-size: 16px;">Hello {patient_name},</p>
<p style="color: #4b5563;">Your appointment has been successfully confirmed.</p>

<div style="background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); padding: 25px; border-radius: 12px; margin: 25px 0; border-left: 4px solid #10b981;">
    <p style="margin: 8px 0; color: #065f46; font-size: 15px;"><strong>📅 Date:</strong> {formatted_date}</p>
    <p style="margin: 8px 0; color: #065f46; font-size: 15px;"><strong>🕐 Time:</strong> {formatted_time}</p>
    <p style="margin: 8px 0; color: #065f46; font-size: 15px;"><strong>👨‍⚕️ Doctor:</strong> Dr. {doctor_name}</p>
    <p style="margin: 8px 0; color: #065f46; font-size: 15px;"><strong>🏥 Clinic:</strong> {clinic_name}</p>
    {address_html}
</div>

<div style="background-color: #eff6ff; padding: 15px; border-radius: 8px; margin: 20px 0;">
    <p style="margin: 0; color: #1e40af; font-size: 14px;">
        <strong>📋 Appointment ID:</strong> {appointment_id}
    </p>
</div>

<p style="color: #4b5563;">Please arrive 10 minutes before your scheduled time.</p>

<div style="text-align: center; margin: 30px 0;">
    <a href="{FRONTEND_URL}/appointments" style="background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%); color: white; text-decoration: none; padding: 12px 30px; border-radius: 8px; font-weight: 600; display: inline-block;">View My Appointments</a>
</div>
"""
        footer = _get_email_footer()
        html_content = _wrap_email_content(header, body, footer)
        
        text_content = f"""Appointment Confirmed!

Hello {patient_name},

Your appointment has been successfully confirmed.

Date: {formatted_date}
Time: {formatted_time}
Doctor: Dr. {doctor_name}
Clinic: {clinic_name}
{f'Address: {clinic_address}' if clinic_address else ''}

Appointment ID: {appointment_id}

Please arrive 10 minutes before your scheduled time.

View your appointments: {FRONTEND_URL}/appointments"""
        
        return _send_email(
            to=patient_email,
            subject=f"Appointment Confirmed - {clinic_name}",
            html=html_content,
            text=text_content
        )
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {str(e)}")
        return {"success": False, "error": str(e)}


def send_appointment_reminder_email(
    patient_email: str,
    patient_name: str,
    doctor_name: str,
    clinic_name: str,
    appointment_date: str,
    clinic_address: Optional[str] = None
):
    """Send appointment reminder email to patient (24 hours before)."""
    try:
        try:
            dt = datetime.fromisoformat(appointment_date.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%B %d, %Y")
            formatted_time = dt.strftime("%H:%M")
        except Exception:
            formatted_date = appointment_date
            formatted_time = ""
        
        header = _get_email_header(clinic_name)
        
        address_html = ""
        if clinic_address:
            address_html = f'<p style="margin: 5px 0; color: #374151;"><strong>📍 Address:</strong> {clinic_address}</p>'
        
        body = f"""
<h2 style="color: #1f2937; margin-bottom: 10px;">Appointment Reminder 🔔</h2>
<p style="color: #4b5563; font-size: 16px;">Hello {patient_name},</p>
<p style="color: #4b5563;">This is a friendly reminder about your upcoming appointment.</p>

<div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 25px; border-radius: 12px; margin: 25px 0; border-left: 4px solid #f59e0b;">
    <p style="margin: 8px 0; color: #92400e; font-size: 15px;"><strong>📅 Tomorrow:</strong> {formatted_date}</p>
    <p style="margin: 8px 0; color: #92400e; font-size: 15px;"><strong>🕐 Time:</strong> {formatted_time}</p>
    <p style="margin: 8px 0; color: #92400e; font-size: 15px;"><strong>👨‍⚕️ Doctor:</strong> Dr. {doctor_name}</p>
    <p style="margin: 8px 0; color: #92400e; font-size: 15px;"><strong>🏥 Clinic:</strong> {clinic_name}</p>
    {address_html}
</div>

<div style="background-color: #dbeafe; padding: 15px; border-radius: 8px; margin: 20px 0;">
    <p style="margin: 0; color: #1e40af; font-size: 14px;">
        ⏰ <strong>Please arrive 10 minutes early</strong>
    </p>
</div>

<p style="color: #4b5563;">If you need to reschedule or cancel, please contact us as soon as possible.</p>

<div style="text-align: center; margin: 30px 0;">
    <a href="{FRONTEND_URL}/appointments" style="background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%); color: white; text-decoration: none; padding: 12px 30px; border-radius: 8px; font-weight: 600; display: inline-block;">Manage Appointment</a>
</div>
"""
        footer = _get_email_footer()
        html_content = _wrap_email_content(header, body, footer)
        
        text_content = f"""Appointment Reminder

Hello {patient_name},

This is a friendly reminder about your upcoming appointment.

Tomorrow: {formatted_date}
Time: {formatted_time}
Doctor: Dr. {doctor_name}
Clinic: {clinic_name}
{f'Address: {clinic_address}' if clinic_address else ''}

Please arrive 10 minutes early.

If you need to reschedule or cancel, please contact us as soon as possible.

Manage your appointment: {FRONTEND_URL}/appointments"""
        
        return _send_email(
            to=patient_email,
            subject=f"Reminder: Appointment Tomorrow - {clinic_name}",
            html=html_content,
            text=text_content
        )
    except Exception as e:
        logger.error(f"Failed to send reminder email: {str(e)}")
        return {"success": False, "error": str(e)}


def send_welcome_email(
    recipient_email: str,
    recipient_name: str,
    user_role: str
):
    """Send welcome email to new user."""
    try:
        role_display = {
            'USER': 'Patient',
            'DOCTOR': 'Doctor',
            'ASSISTANT': 'Medical Assistant',
            'RECEPTIONIST': 'Receptionist',
            'LOCATION_ADMIN': 'Location Administrator',
            'CLINIC_ADMIN': 'Clinic Administrator',
            'SUPER_ADMIN': 'Super Administrator'
        }.get(user_role, 'User')
        
        header = _get_email_header("Welcome to MediConnect")
        
        body = f"""
<h2 style="color: #1f2937; margin-bottom: 10px;">Welcome to MediConnect! 🎉</h2>
<p style="color: #4b5563; font-size: 16px;">Hello {recipient_name},</p>
<p style="color: #4b5563;">Thank you for joining MediConnect as a <strong>{role_display}</strong>.</p>

<div style="background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%); padding: 25px; border-radius: 12px; margin: 25px 0;">
    <h3 style="color: #5b21b6; margin-top: 0;">Getting Started</h3>
    <ul style="color: #6b21a8; line-height: 1.8; padding-left: 20px;">
        <li>Complete your profile information</li>
        <li>Explore the dashboard and features</li>
        <li>Set up your preferences</li>
        <li>Start managing your healthcare journey</li>
    </ul>
</div>

<p style="color: #4b5563;">If you have any questions or need assistance, our support team is here to help.</p>

<div style="text-align: center; margin: 30px 0;">
    <a href="{FRONTEND_URL}/dashboard" style="background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%); color: white; text-decoration: none; padding: 12px 30px; border-radius: 8px; font-weight: 600; display: inline-block;">Go to Dashboard</a>
</div>
"""
        footer = _get_email_footer()
        html_content = _wrap_email_content(header, body, footer)
        
        text_content = f"""Welcome to MediConnect!

Hello {recipient_name},

Thank you for joining MediConnect as a {role_display}.

Getting Started:
- Complete your profile information
- Explore the dashboard and features
- Set up your preferences
- Start managing your healthcare journey

If you have any questions or need assistance, our support team is here to help.

Go to your dashboard: {FRONTEND_URL}/dashboard"""
        
        return _send_email(
            to=recipient_email,
            subject="Welcome to MediConnect!",
            html=html_content,
            text=text_content
        )
    except Exception as e:
        logger.error(f"Failed to send welcome email: {str(e)}")
        return {"success": False, "error": str(e)}


def send_access_request_notification_email(
    admin_email: str,
    admin_name: str,
    requester_name: str,
    requester_email: str,
    clinic_name: str,
    request_id: str
):
    """Send notification to admin about new access request."""
    try:
        header = _get_email_header(clinic_name)
        
        body = f"""
<h2 style="color: #1f2937; margin-bottom: 10px;">New Access Request 📬</h2>
<p style="color: #4b5563; font-size: 16px;">Hello {admin_name},</p>
<p style="color: #4b5563;">A new user has requested access to <strong>{clinic_name}</strong>.</p>

<div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
    <p style="margin: 5px 0; color: #374151;"><strong>Name:</strong> {requester_name}</p>
    <p style="margin: 5px 0; color: #374151;"><strong>Email:</strong> {requester_email}</p>
    <p style="margin: 5px 0; color: #374151;"><strong>Request ID:</strong> {request_id}</p>
</div>

<p style="color: #4b5563;">Please review this request and approve or deny access.</p>

<div style="text-align: center; margin: 30px 0;">
    <a href="{FRONTEND_URL}/access-requests" style="background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%); color: white; text-decoration: none; padding: 12px 30px; border-radius: 8px; font-weight: 600; display: inline-block;">Review Request</a>
</div>
"""
        footer = _get_email_footer()
        html_content = _wrap_email_content(header, body, footer)
        
        text_content = f"""New Access Request

Hello {admin_name},

A new user has requested access to {clinic_name}.

Name: {requester_name}
Email: {requester_email}
Request ID: {request_id}

Please review this request and approve or deny access.

Review request: {FRONTEND_URL}/access-requests"""
        
        return _send_email(
            to=admin_email,
            subject=f"New Access Request - {clinic_name}",
            html=html_content,
            text=text_content
        )
    except Exception as e:
        logger.error(f"Failed to send access request notification: {str(e)}")
        return {"success": False, "error": str(e)}
