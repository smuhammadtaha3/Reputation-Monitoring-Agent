from supabase import create_client, Client
from app.core.config import settings

print("SUPABASE_URL =", settings.supabase_url)

if settings.supabase_key:
    print("SUPABASE_KEY =", settings.supabase_key[:10] + "...")
else:
    print("SUPABASE_KEY = EMPTY")
    
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)