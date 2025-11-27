# Quick Fix: Conversation & AI Issues

## ✅ Issue 1: Conversation Tables Missing

**Error:** `relation "conversation_sessions" does not exist`

### Fix (2 minutes):

1. **Open Supabase Dashboard:**
   - Go to your Supabase project
   - Click **SQL Editor** in left sidebar

2. **Run this SQL:**
   ```sql
   -- Copy and paste the entire contents of scripts/create_conversation_tables.sql
   -- Or run the SQL below:
   ```

3. **Or use the file:**
   - Open `scripts/create_conversation_tables.sql`
   - Copy all SQL
   - Paste into Supabase SQL Editor
   - Click **Run**

4. **Restart Backend:**
   ```bash
   docker compose -f devops/docker-compose.yml restart backend
   ```

---

## ✅ Issue 2: CORS Errors

**Error:** `Access to XMLHttpRequest ... blocked by CORS policy`

### Fix (1 minute):

1. **Restart Backend:**
   ```bash
   docker compose -f devops/docker-compose.yml restart backend
   ```

2. **Verify CORS is working:**
   - Check backend logs: `docker compose -f devops/docker-compose.yml logs backend --tail=10`
   - Should see no CORS-related errors

---

## ✅ Issue 3: AI Suggestions

**Status:** ✅ AI services are running (verified)

### If AI suggestions still don't work:

1. **Check diagnosis helper service:**
   ```bash
   docker compose -f devops/docker-compose.yml logs diagnosis-helper-service --tail=20
   ```

2. **Test the endpoint:**
   - Make sure you're logged in
   - Go to patient detail page
   - Click "Generate Suggestions" in AI Suggestions section
   - Check browser console for errors

3. **Common fixes:**
   - Restart diagnosis helper: `docker compose -f devops/docker-compose.yml restart diagnosis-helper-service`
   - Check backend can reach service (should work if services are running)

---

## 🎯 Complete Fix Steps (5 minutes total):

```bash
# 1. Create conversation tables in Supabase SQL Editor
#    (Copy scripts/create_conversation_tables.sql and run it)

# 2. Restart backend
docker compose -f devops/docker-compose.yml restart backend

# 3. Verify services are running
docker compose -f devops/docker-compose.yml ps

# 4. Test in browser
#    - Log in
#    - Go to patient "Sarah Chen"
#    - Try Conversation section (should work now)
#    - Try AI Suggestions (should work)
```

---

## 📋 Verification Checklist:

After fixing, verify:

- [ ] Conversation section loads without errors
- [ ] Can create a conversation session
- [ ] AI Suggestions section works
- [ ] "Generate Suggestions" button works
- [ ] No CORS errors in browser console
- [ ] No 500 errors in browser console

---

## 🔍 If Still Not Working:

1. **Check backend logs:**
   ```bash
   docker compose -f devops/docker-compose.yml logs backend --tail=50
   ```

2. **Check frontend console:**
   - Open browser DevTools (F12)
   - Check Console tab for errors
   - Check Network tab for failed requests

3. **Verify database:**
   - Go to Supabase → Table Editor
   - Should see `conversation_sessions`, `conversation_transcripts`, `conversation_analysis` tables

4. **Verify authentication:**
   - Make sure you're logged in
   - Check user role is `clinician` or `admin`

---

**Most likely fix:** Just need to create the conversation tables in Supabase! 🎯

