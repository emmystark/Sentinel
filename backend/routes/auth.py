from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from config import get_supabase, get_user_id
from typing import Optional
import logging
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
            message="Signup successful. Please check your email to verify your account.",
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
        response = supabase.table("user_profiles").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return response.data[0]
        
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
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
        response = supabase.table("user_profiles").update(update_dict).eq("id", user_id).execute()
        return {
            "success": True,
            "message": "Profile updated",
            "profile": response.data[0] if response.data else None
        }
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail="Error updating profile")
