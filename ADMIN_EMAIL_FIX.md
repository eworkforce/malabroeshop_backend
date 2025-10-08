# Admin Email Configuration Fix

## Problem
The notification system was still sending emails to `sergeziehi@eworkforce.africa` instead of the new admin email `leader@malabrocloud.com`.

## Root Cause
The notification endpoint was accepting `admin_email` as a parameter from the frontend request, which could be hardcoded in the frontend code. This was:
1. A security concern (allowing frontend to specify admin email)
2. Causing inconsistency (different email than configured in environment)

## Solution

### 1. Updated Environment Variables (`.env`)
```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=<SENDGRID_API_KEY>  # Configured in environment
SENDGRID_FROM_EMAIL=leader@malabrocloud.com
ADMIN_EMAIL=leader@malabrocloud.com
```

### 2. Modified Backend Code

**File**: `app/api/v1/endpoints/notification.py`

**Changes**:
- Removed `admin_email` field from `PaymentNotificationRequest` model
- Modified `send_admin_notification()` to accept `admin_email` as a parameter
- Updated both endpoints to load `admin_email` from `settings.ADMIN_EMAIL` instead of request body

**Before**:
```python
class PaymentNotificationRequest(BaseModel):
    admin_email: EmailStr  # Received from frontend - BAD!
    ...

def send_admin_notification(notification_data: PaymentNotificationRequest):
    return send_email(notification_data.admin_email, ...)  # Uses frontend value
```

**After**:
```python
class PaymentNotificationRequest(BaseModel):
    # admin_email removed from request model
    ...

def send_admin_notification(notification_data: PaymentNotificationRequest, admin_email: str):
    return send_email(admin_email, ...)  # Uses parameter

@router.post("/payment-started")
async def notify_payment_started(...):
    from app.core.config import settings
    # Always use admin email from environment settings
    background_tasks.add_task(send_admin_notification, notification_data, settings.ADMIN_EMAIL)
```

## Benefits
1. ✅ **Security**: Admin email can only be set by backend environment, not by frontend
2. ✅ **Consistency**: Single source of truth for admin email
3. ✅ **Flexibility**: Easy to update admin email by changing only environment variable
4. ✅ **No frontend changes needed**: API remains backward compatible (frontend can still send admin_email, but it will be ignored)

## Testing
Both endpoints tested successfully:
- ✅ `/api/v1/notifications/test-email` - sends to configured admin
- ✅ `/api/v1/notifications/payment-started` - sends to configured admin

All emails now go to: `leader@malabrocloud.com`

## Date
Applied: October 8, 2025 (14:13 UTC)
