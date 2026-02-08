from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from config import get_supabase, get_user_id
from typing import Optional
import logging
import os
from supabase import Client
from datetime import datetime, timedelta
import random
import string


logger = logging.getLogger(__name__)
router = APIRouter()

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str = ""

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: dict
    session: Optional[dict] = None

@router.post("/signup", response_model=AuthResponse)
async def signup(
    request: SignupRequest,
    supabase = Depends(get_supabase)
):
    """Sign up a new user with profile creation"""
    try:
        # Create auth user
        logger.info(f"Creating auth user for email: {request.email}")
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "name": request.name or request.email.split("@")[0]
                }
            }
        })
        
        if not auth_response.user:
            logger.error(f"Auth signup failed for {request.email}")
            raise HTTPException(status_code=400, detail="Signup failed - could not create user")
        
        # Create user profile (database trigger should also create it)
        user_id = auth_response.user.id
        name = request.name or request.email.split("@")[0]
        
        try:
            logger.info(f"Creating profile for user {user_id}")
            profile_response = supabase.table("user_profiles").insert({
                "id": user_id,
                "email": request.email,
                "name": name,
                "monthly_income": 0,
                "fixed_bills": 0,
                "savings_goal": 0,
                "telegram_connected": False,
                "push_notification_enabled": True
            }).execute()
            logger.info(f"Profile created successfully: {profile_response}")
        except Exception as profile_error:
            logger.warning(f"Profile creation warning (may be created by trigger): {profile_error}")
            # This is not critical - the database trigger might have already created it
        
        logger.info(f"Signup successful for user {user_id}")
        
        # Build session data
        session_data = {}
        if auth_response.session:
            session_data = {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
                "expires_in": auth_response.session.expires_in,
                "token_type": "bearer"
            }
        
        return AuthResponse(
            success=True,
            message="Signup successful. You can now log in.",
            user={
                "id": user_id,
                "email": request.email,
                "name": name
            },
            session=session_data if session_data else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Signup failed: {str(e)[:100]}")

@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    supabase: Client = Depends(get_supabase)
):
    """Login user"""
    try:
        logger.info(f"Login attempt for email: {request.email}")
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user:
            logger.warning(f"Login failed - invalid credentials for {request.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Get user profile for additional info
        profile_data = {}
        try:
            profile_response = supabase.table("user_profiles").select("*").eq(
                "id", auth_response.user.id
            ).execute()
            if profile_response.data:
                profile_data = profile_response.data[0]
        except Exception as e:
            logger.warning(f"Could not fetch profile: {e}")
        
        logger.info(f"Login successful for user {auth_response.user.id}")
        
        # Build session data
        session_data = {}
        if auth_response.session:
            session_data = {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
                "expires_in": auth_response.session.expires_in,
                "token_type": "bearer"
            }
        
        return AuthResponse(
            success=True,
            message="Login successful",
            user={
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "name": profile_data.get("name", ""),
                "telegram_connected": profile_data.get("telegram_connected", False)
            },
            session=session_data if session_data else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.post("/logout")
async def logout(
    supabase: Client = Depends(get_supabase)
):
    """Logout user"""
    try:
        supabase.auth.sign_out()
        return {
            "success": True,
            "message": "Logout successful"
        }
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=400, detail="Logout failed")




@router.get("/profile")
async def get_profile(
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """Get user profile"""
    
    try:
        # Try anon first
        response = supabase.table("user_profiles").select("*").eq("id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        
        # If not found with anon, try with service role
        logger.warning(f"Profile not found with anon client, attempting with service role for user {user_id}")
        from config import get_supabase_admin
        admin_supabase = get_supabase_admin()
        response = admin_supabase.table("user_profiles").select("*").eq("id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        
        # Profile doesn't exist - create it with default values
        logger.warning(f"Profile not found for user {user_id}, creating new profile with defaults")
        profile_data = {
            "id": user_id,
            "email": "",
            "name": "User",
            "monthly_income": 0,
            "fixed_bills": 0,
            "savings_goal": 0,
            "telegram_connected": False,
            "push_notification_enabled": True,
            "preferred_currency": "NGN"
        }
        
        # Use admin to create profile
        create_response = admin_supabase.table("user_profiles").insert(profile_data).execute()
        if create_response.data and len(create_response.data) > 0:
            logger.info(f"Created default profile for user {user_id}")
            return create_response.data[0]
        
        raise HTTPException(status_code=404, detail="Could not create or retrieve profile")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching/creating profile: {e}", exc_info=True)
        # Return a default profile for development
        if os.getenv("ENVIRONMENT") == "development":
            return {
                "id": user_id,
                "email": "user@example.com",
                "name": "Demo User",
                "monthly_income": 100000,
                "fixed_bills": 30000,
                "savings_goal": 20000,
                "telegram_connected": False,
                "push_notification_enabled": True,
                "preferred_currency": "NGN"
            }
        raise HTTPException(status_code=500, detail="Error fetching profile")

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    monthly_income: Optional[float] = None
    fixed_bills: Optional[float] = None
    savings_goal: Optional[float] = None

@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdate,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """Update user profile"""
    
    try:
        update_dict = profile_data.model_dump(exclude_none=True)
        if not update_dict:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Try with anon first
        response = supabase.table("user_profiles").update(update_dict).eq("id", user_id).execute()
        
        if response.data:
            logger.info(f"Profile updated for user {user_id}")
            return {
                "success": True,
                "message": "Profile updated",
                "profile": response.data[0] if response.data else None
            }
        
        # Fallback to service role
        logger.warning(f"Anon update failed, trying with service role for user {user_id}")
        from config import get_supabase_admin
        admin_supabase = get_supabase_admin()
        response = admin_supabase.table("user_profiles").update(update_dict).eq("id", user_id).execute()
        
        if response.data:
            logger.info(f"Profile updated with service role for user {user_id}")
            return {
                "success": True,
                "message": "Profile updated",
                "profile": response.data[0] if response.data else None
            }
        
        raise HTTPException(status_code=400, detail="Failed to update profile")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error updating profile")