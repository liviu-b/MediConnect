import resend
import logging
from datetime import datetime
from ..config import RESEND_API_KEY, DEFAULT_FROM_EMAIL

logger = logging.getLogger("mediconnect")
resend.api_key = RESEND_API_KEY


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
<h2 style="color: #1f2937;">Password Reset Request</h2>
<p style="color: #4b5563;">Hello {recipient_name},</p>
<p style="color: #4b5563;">Click the button below to reset your password.</p>
<div style="text-align: center; margin: 30px 0;">
<a href="{reset_link}" style="background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%); color: white; text-decoration: none; padding: 14px 40px; border-radius: 8px; font-weight: 600;">Reset Your Password</a>
</div>
<p style="color: #6b7280; font-size: 14px;">Or copy this link: {reset_link}</p>
<p style="color: #9ca3af; font-size: 12px;">This link expires in 1 hour.</p>
</div>
</div>
</body>
</html>"""
        text_content = f"Password Reset\n\nHello {recipient_name},\n\nReset your password: {reset_link}\n\nThis link expires in 1 hour."
        resend.Emails.send({
            "from": DEFAULT_FROM_EMAIL,
            "to": recipient_email,
            "subject": f"Reset Your Password - {center_name}",
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
            'ASSISTANT': 'Assistant',
            'RECEPTIONIST': 'Receptionist',
            'NURSE': 'Nurse',
            'ADMIN': 'Administrator'
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
<h2 style="color: #1f2937;">You're Invited to Join {clinic_name}</h2>
<p style="color: #4b5563;">Hello {recipient_name},</p>
<p style="color: #4b5563;">{inviter_name} has invited you to join <strong>{clinic_name}</strong> as a <strong>{role_display}</strong> on MediConnect.</p>
<p style="color: #4b5563;">Click the button below to accept your invitation and set up your account:</p>
<div style="text-align: center; margin: 30px 0;">
<a href="{invitation_link}" style="background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%); color: white; text-decoration: none; padding: 14px 40px; border-radius: 8px; font-weight: 600;">Accept Invitation</a>
</div>
<p style="color: #6b7280; font-size: 14px;">Or copy this link: {invitation_link}</p>
<p style="color: #9ca3af; font-size: 12px;">This invitation expires in 7 days.</p>
</div>
</div>
</body>
</html>"""
        text_content = f"Staff Invitation\n\nHello {recipient_name},\n\n{inviter_name} has invited you to join {clinic_name} as a {role_display}.\n\nAccept your invitation: {invitation_link}\n\nThis invitation expires in 7 days."
        resend.Emails.send({
            "from": DEFAULT_FROM_EMAIL,
            "to": recipient_email,
            "subject": f"You're Invited to Join {clinic_name} - MediConnect",
            "html": html_content,
            "text": text_content
        })
        logger.info(f"Staff invitation email sent to {recipient_email}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to send staff invitation email: {str(e)}")
        return {"success": False, "error": str(e)}


def send_cancellation_notification_email(patient_email: str, patient_name: str, doctor_name: str, clinic_name: str, appointment_date: str, cancellation_reason: str):
    try:
        try:
            dt = datetime.fromisoformat(appointment_date.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%B %d, %Y at %H:%M")
        except Exception:
            formatted_date = appointment_date
        html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; background-color: #f5f7fa; margin: 0; padding: 20px;">
<div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden;">
<div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); padding: 30px; text-align: center;">
<h1 style="color: white; margin: 0;">Appointment Cancelled</h1>
</div>
<div style="padding: 40px 30px;">
<p style="color: #4b5563;">Hello {patient_name},</p>
<p style="color: #4b5563;">We regret to inform you that your appointment has been cancelled.</p>
<div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
<p style="margin: 5px 0; color: #374151;"><strong>Doctor:</strong> Dr. {doctor_name}</p>
<p style="margin: 5px 0; color: #374151;"><strong>Clinic:</strong> {clinic_name}</p>
<p style="margin: 5px 0; color: #374151;"><strong>Original Date:</strong> {formatted_date}</p>
</div>
<div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0;">
<p style="margin: 0; color: #991b1b;"><strong>Reason for Cancellation:</strong></p>
<p style="margin: 5px 0 0 0; color: #7f1d1d;">{cancellation_reason}</p>
</div>
<p style="color: #4b5563;">Please contact us or book a new appointment at your convenience.</p>
<p style="color: #6b7280; font-size: 14px;">We apologize for any inconvenience caused.</p>
</div>
</div>
</body>
</html>"""
        text_content = f"Appointment Cancelled\n\nHello {patient_name},\n\nYour appointment with Dr. {doctor_name} at {clinic_name} on {formatted_date} has been cancelled.\n\nReason: {cancellation_reason}\n\nPlease contact us or book a new appointment at your convenience."
        resend.Emails.send({
            "from": DEFAULT_FROM_EMAIL,
            "to": patient_email,
            "subject": f"Appointment Cancelled - {clinic_name}",
            "html": html_content,
            "text": text_content
        })
        logger.info(f"Cancellation email sent to {patient_email}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to send cancellation email: {str(e)}")
        return {"success": False, "error": str(e)}
