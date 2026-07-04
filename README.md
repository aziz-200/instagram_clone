# 📸 Instagram Clone — Django REST Framework API

A production-grade **Instagram-like REST API** built with **Django 6**, **Django REST Framework**, and **PostgreSQL**. Implements a complete 4-step user onboarding pipeline, JWT authentication with token blacklisting, threaded comments with nested replies, and a toggle-based like system — all backed by a clean shared infrastructure with UUID primary keys and async email delivery.

---

## 🚀 Features

### 👤 User & Authentication
- **4-Step Registration Pipeline** — `NEW → CODE_VERIFIED → DONE → PHOTO_DONE` onboarding flow
- **Email & Phone Sign-up** — Auto-detects input type via regex and routes OTP accordingly
- **OTP Verification** — 4-digit code delivered via async HTML email or Twilio SMS
- **JWT Authentication** — Short-lived access tokens (5 min) + refresh tokens (1 day) via `simplejwt`
- **Token Blacklisting** — Logout invalidates the refresh token server-side
- **Flexible Login** — Accepts username, email, or phone number in a single input field
- **Token Refresh** — Custom refresh view that also updates `last_login` timestamp
- **Auto-generated Username** — UUID-based fallback if user doesn't provide one
- **Secure Password Handling** — Auto-hashes plain-text passwords on save (`pbkdf2_sha256`)
- **Forgot & Reset Password** — Sends OTP, returns fresh JWT pair after successful reset
- **Profile Photo Upload** — Validates `jpg`, `jpeg`, `png`, `heif` formats via `FileExtensionValidator`
- **User Roles** — `ordinary_user`, `manager`, `administrator`

### 📝 Posts
- **Full CRUD** — Create, list, retrieve, update, and delete posts
- **Image Upload** — Restricted to `jpg` / `png` via validator
- **Caption** — Up to 5,000 characters
- **Computed Fields** — `post_likes_count`, `post_comment_count`, `me_liked` per post response

### 💬 Comments
- **Post Comments** — Create and list comments linked to a specific post
- **Nested Replies** — Self-referential `parent` FK enables threaded comment trees
- **Computed Fields** — `likes_count`, `me_liked`, and recursive `replies` in each response

### ❤️ Likes
- **Toggle Likes** — Single endpoint handles both like and unlike via POST/DELETE
- **Post & Comment Likes** — Separate like models for posts and comments
- **Uniqueness Enforced** — DB-level `UniqueConstraint` on `(author, post)` and `(author, comment)`

### 🔧 Shared / Infrastructure
- **BaseModel** — UUID primary key, `created_time`, `updated_time` inherited by all models
- **Custom Pagination** — 10 items/page with `next`, `previous`, `count`, `results` envelope
- **Async Email** — `threading.Thread` wrapper prevents email from blocking the request cycle
- **Regex Validators** — Utility functions detect whether input is email, phone, or username
- **Twilio SMS** — `send_phone_code()` ready to plug in with account credentials
- **Environment Config** — All secrets via `python-decouple` / `.env` file

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.14 |
| **Framework** | Django 6.0.6 |
| **REST API** | Django REST Framework |
| **Auth** | JWT — `djangorestframework-simplejwt` |
| **Database** | PostgreSQL (`psycopg2`) |
| **ORM** | Django ORM |
| **SMS** | Twilio |
| **Email** | Django Email + HTML templates + Threading |
| **Phone Validation** | `phonenumbers` |
| **Image Handling** | Pillow |
| **Config** | `python-decouple` (.env) |
| **Package Manager** | Pipenv |

---

## 📁 Project Structure

```
instagram_clone/
├── instagram_clone/               # Project config
│   ├── settings.py                # JWT, DRF, DB, media config
│   ├── urls.py                    # Root URL routing
│   └── wsgi.py
│
├── users/                         # User auth & profile app
│   ├── models.py                  # User (AbstractUser), UserConfirmation
│   ├── serializers.py             # SignUp, Login, ChangeInfo, ForgotPassword, Reset
│   ├── views.py                   # All auth & profile views
│   └── urls.py
│
├── post/                          # Posts, comments & likes app
│   ├── models.py                  # Post, PostComment, PostLike, CommentLike
│   ├── serializers.py             # PostSerializer, CommentSerializer, LikeSerializers
│   ├── views.py                   # CRUD + Like toggle views
│   └── urls.py
│
├── shared/                        # Reusable utilities & base classes
│   ├── models.py                  # BaseModel (UUID pk, timestamps)
│   ├── custom_pagination.py       # CustomPagination (10/page)
│   └── utils.py                   # Email/SMS senders, regex validators
│
├── templates/
│   └── email/authentication/
│       └── activate_account.html  # OTP email HTML template
│
├── .env                           # Environment variables (not committed)
├── Pipfile
└── manage.py
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/aziz-200/instagram_clone.git
cd instagram_clone
```

### 2. Install dependencies
```bash
pip install pipenv
pipenv install
pipenv shell
```

### 3. Configure environment variables

Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True

DB_NAME=instagram_db
USER=your_db_user
PASSWORD=your_db_password
HOST=localhost
PORT=5432

# Optional: Twilio for SMS
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
```

### 4. Create PostgreSQL database
```sql
CREATE DATABASE instagram_db;
```

### 5. Apply migrations
```bash
python manage.py migrate
```

### 6. Create a superuser
```bash
python manage.py createsuperuser
```

### 7. Run the development server
```bash
python manage.py runserver
```

---

## 📦 Dependencies

```
django
djangorestframework
djangorestframework-simplejwt
djangorestframework-stubs
pillow
psycopg2
phonenumbers
twilio
python-decouple
```

---

## 🔐 Authentication Flow

Registration follows a strict **4-step pipeline**. Each step advances `auth_status`:

```
Step 1 — Sign Up
  POST /users/signup/
  Body: { "email_phone_number": "user@example.com" }
  ← system sends OTP to email/phone
  ← auth_status: "new"

Step 2 — Verify OTP
  POST /users/verify/
  Body: { "code": "4821" }
  ← auth_status: "code_verified"

Step 3 — Set Profile Info
  PATCH /users/update-info/
  Body: { "first_name": "Aziz", "last_name": "Doe",
          "username": "aziz_dev", "password": "...", "confirm_password": "..." }
  ← auth_status: "done"

Step 4 — Upload Photo
  PUT /users/update-photo/
  Body: form-data { "photo": <file> }
  ← auth_status: "photo_done"
```

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

---

## 📌 API Endpoints

### 🔑 Users (`/users/`)

| Method | Endpoint | Auth | Request Body | Response |
|---|---|---|---|---|
| `POST` | `/users/signup/` | ❌ | `{ "email_phone_number": "..." }` | `{ id, auth_type, auth_status, access, refresh_token }` |
| `POST` | `/users/verify/` | ✅ | `{ "code": "1234" }` | `{ success, auth_status, access, refresh }` |
| `GET` | `/users/newverify/` | ✅ | — | `{ success, message }` |
| `PATCH` | `/users/update-info/` | ✅ | `{ first_name, last_name, username, password, confirm_password }` | `{ success, auth_status }` |
| `PUT` | `/users/update-photo/` | ✅ | `form-data { photo }` | `{ success, message }` |
| `POST` | `/users/login/` | ❌ | `{ "userinput": "aziz_dev", "password": "..." }` | `{ access, refresh_token, auth_status, full_name }` |
| `POST` | `/users/login/refresh/` | ❌ | `{ "refresh": "..." }` | `{ access }` |
| `POST` | `/users/logout/` | ✅ | `{ "refresh": "..." }` | `{ success, message }` |
| `POST` | `/users/forgot-password/` | ❌ | `{ "email_or_phone_number": "..." }` | `{ success, access_token, refresh_token, user_status }` |
| `PATCH` | `/users/reset-password/` | ✅ | `{ "password": "...", "confirm_password": "..." }` | `{ success, access, refresh }` |

---

### 📝 Posts (`/post/`)

| Method | Endpoint | Auth | Request Body | Response |
|---|---|---|---|---|
| `GET` | `/post/list/` | Optional | — | Paginated `{ next, previous, count, results: [posts] }` |
| `POST` | `/post/create/` | ✅ | `form-data { image, caption }` | Created post object |
| `GET` | `/post/<uuid>/` | Optional | — | Single post with likes count, comment count, me_liked |
| `PUT` | `/post/<uuid>/` | ✅ | `{ caption }` | `{ success, message }` |
| `DELETE` | `/post/<uuid>/` | ✅ | — | `{ success, message }` |
| `GET` | `/post/<uuid>/comments/` | ✅ | — | List of comments with nested replies |
| `POST` | `/post/<uuid>/comments/create/` | ✅ | `{ "comment": "...", "parent": null }` | Created comment object |
| `GET` | `/post/<uuid>/likes/` | ❌ | — | List of users who liked the post |
| `POST` | `/post/<uuid>/create-delete-likes/` | ✅ | — | `{ success, message, data }` — creates like |
| `DELETE` | `/post/<uuid>/create-delete-likes/` | ✅ | — | `{ success, message }` — removes like |

---

### 💬 Comments (`/post/comments/`)

| Method | Endpoint | Auth | Request Body | Response |
|---|---|---|---|---|
| `GET` | `/post/comments/<uuid>/` | ❌ | — | Comment detail with replies and like count |
| `PUT` | `/post/comments/<uuid>/` | ✅ | `{ "comment": "..." }` | Updated comment object |
| `DELETE` | `/post/comments/<uuid>/` | ✅ | — | 204 No Content |
| `GET` | `/post/comments/<uuid>/likes/` | ❌ | — | List of users who liked the comment |
| `POST` | `/post/comments/<uuid>/create-delete-likes/` | ✅ | — | Toggle like on comment |

---

### 📦 Sample Response — Post List

```json
{
  "next": "http://localhost:8000/post/list/?page=2",
  "previous": null,
  "count": 42,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "author": {
        "id": "...",
        "username": "aziz_dev",
        "photo": "/media/user_photos/aziz.jpg"
      },
      "image": "/media/posts_images/photo.jpg",
      "caption": "Hello world!",
      "created_time": "2025-06-01T10:30:00Z",
      "post_likes_count": 14,
      "post_comment_count": 3,
      "me_liked": true
    }
  ]
}
```

---

### 📦 Sample Response — Login

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "auth_status": "photo_done",
  "full_name": "Aziz Doe"
}
```

---

## 🗄️ Data Models

### User (extends `AbstractUser`)
| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `user_role` | CharField | `ordinary_user` / `manager` / `administrator` |
| `auth_type` | CharField | `via_email` / `via_phone` |
| `auth_status` | CharField | `new` → `code_verified` → `done` → `photo_done` |
| `email` | EmailField | Unique, nullable |
| `phone_number` | CharField | Unique, nullable |
| `photo` | ImageField | `user_photos/` |

### UserConfirmation
| Field | Type | Notes |
|---|---|---|
| `code` | CharField(4) | Random 4-digit OTP |
| `verify_type` | CharField | `via_email` / `via_phone` |
| `expiration_time` | DateTimeField | 5 min (email), 2 min (phone) |
| `is_verified` | BooleanField | Marks code as used |

### Post
| Field | Type | Notes |
|---|---|---|
| `author` | FK → User | |
| `image` | ImageField | `posts_images/` |
| `caption` | TextField | Max 5,000 chars |

### PostComment
| Field | Type | Notes |
|---|---|---|
| `author` | FK → User | |
| `post` | FK → Post | |
| `comment` | TextField | Max 1,000 chars |
| `parent` | FK → self | Nullable — enables nested replies |

### PostLike / CommentLike
- `UniqueConstraint` on `(author, post)` and `(author, comment)` — one like per user per item

---

## 🔄 JWT Configuration

```python
ACCESS_TOKEN_LIFETIME  = 5 minutes
REFRESH_TOKEN_LIFETIME = 1 day
ALGORITHM              = HS256
AUTH_HEADER_TYPES      = ("Bearer",)
TOKEN_BLACKLIST        = enabled   # used on logout
```

---

## 👤 Author

**Aziz** — [github.com/aziz-200](https://github.com/aziz-200)
