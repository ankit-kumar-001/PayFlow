Continuing payment-gateway. Today: user signup/login with JWT.

1. app/schemas/user.py: UserSignup (email, password, full_name), UserLogin
   (email, password), UserOut (id, email, full_name, created_at),
   TokenResponse (access_token, token_type).

2. app/repositories/user_repo.py: create_user(...), get_user_by_email(email),
   get_user_by_id(id) — raw SQL only, via the cursor helper from Day 1.

3. app/core/security.py: password hashing/verification with passlib(bcrypt);
   JWT create/decode with python-jose using JWT_SECRET/JWT_EXPIRE_MINUTES;
   payload includes sub (user id) and exp.

4. app/services/auth_service.py: signup (check email not taken, hash, insert),
   login (verify password, issue JWT).

5. app/routers/auth.py: POST /auth/signup, POST /auth/login. Register under
   /auth in main.py.

6. app/core/dependencies.py: get_current_user — reads Authorization: Bearer
   <token>, decodes, loads the user, 401 on invalid/expired. Add a protected
   GET /auth/me to prove it works.

Test: signup, login, call /auth/me with the token. Commit: "Day 3: user
authentication (signup, login, JWT)"