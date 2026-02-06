from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from config import get_supabase, get_user_id
from typing import Optional
import logging
from supabase import Client


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

@router.post("/signup", response_model=AuthResponse)
async def signup(
    request: SignupRequest,
    supabase = Depends(get_supabase)
):
    """Sign up a new user"""
    try:
        # Create auth user
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Signup failed")
        
        # Create user profile
        user_id = auth_response.user.id
        name = request.name or request.email.split("@")[0]
        
        try:
            supabase.table("user_profiles").insert({
                "id": user_id,
                "email": request.email,
                "name": name,
                "monthly_income": 0,
                "fixed_bills": 0,
                "savings_goal": 0,
                "telegram_connected": False
            }).execute()
        except Exception as profile_error:
            logger.error(f"Profile creation error: {profile_error}")
        
        return {
            "success": True,
            "message": "Signup successful",
            "user": {
                "id": user_id,
                "email": request.email,
                "name": name
            }
        }
        
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(
    request: LoginRequest,
    supabase: Client = Depends(get_supabase)
):
    """Login user"""
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email
            },
            "session": {
                "access_token": auth_response.session.access_token if auth_response.session else None
            }
        }
        
    except Exception as e:
        logger.error(f"Login error: {e}")
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
    user_id: str = Depends(lambda: None),  # Get from header
    supabase: Client = Depends(get_supabase)
):
    """Get user profile"""
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID required")
    
    try:
        response = supabase.table("user_profiles").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return response.data[0]
        
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        raise HTTPException(status_code=500, detail="Error fetching profile")

@router.put("/profile")
async def update_profile(
    profile_data: dict,
    user_id: str = Depends(lambda: None),
    supabase: Client = Depends(get_supabase)
):
    """Update user profile"""
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID required")
    
    try:
        response = supabase.table("user_profiles").update(profile_data).eq("id", user_id).execute()
        return {
            "success": True,
            "message": "Profile updated",
            "profile": response.data[0] if response.data else None
        }
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail="Error updating profile")
