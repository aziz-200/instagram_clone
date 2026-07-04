# 📸 Instagram Clone — Django REST Framework API

A production-grade **Instagram-like REST API** built with **Django 6**, **Django REST Framework**, and **PostgreSQL**. Features a complete multi-step user authentication system with email/phone verification, JWT token auth, post & comment management, nested replies, and a like/unlike toggle system.

---

## 🚀 Features

### 👤 User & Authentication
- **Multi-step Registration Flow** — `NEW → CODE_VERIFIED → DONE → PHOTO_DONE` status pipeline
- **Email & Phone Sign-up** — Auto-detects input type (email or phone number) and routes accordingly
- **OTP Verification** — 4-digit code sent via email (HTML template); phone via Twilio SMS
- **JWT Authentication** — Access + Refresh tokens via `djangorestframework-simplejwt`
- **Token Blacklisting** — Secure logout invalidates refresh tokens
- **Auto-generated Username** — UUID-based fallback username if not provided
- **Password Hashing** — Auto-hashes plain-text passwords on save using `pbkdf2_sha256`
- **Login Flexibility** — Login with username, email, or phone number
- **Token Refresh** — Custom refresh view that also updates `last_login`
- **Forgot Password** — Sends reset code via email or phone
- **Reset Password** — Returns new JWT tokens after successful reset
- **Profile Photo Upload** — Restricted to `jpg`, `jpeg`, `png`, `heif` formats
- **User Roles** — `ordinary_user`, `manager`, `administrator`

### 📝 Posts
- **Create / List / Retrieve / Update / Delete** posts
- **Image Upload** — Only `jpg` and `png` allowed
- **Caption** — Up to 5000 characters
- **Like Count** — Annotated per post via `SerializerMethodField`
- **Comment Count** — Annotated per post via `SerializerMethodField`
- **Me Liked** — Returns `true/false` based on requesting user

### 💬 Comments
- **Post Comments** — Create and list comments on a specific post
- **Nested Replies** — Comments support a self-referential `parent` ForeignKey for threaded replies
- **Comment Likes Count** — Annotated per comment
- **Me Liked** — Returns whether the requesting user liked the comment

### ❤️ Likes
- **Post Likes** — Like/unlike a post via toggle (`PostLikeAPIView`)
- **Comment Likes** — Like/unlike a comment (`CommentLikeAPIView`)
- **Unique Constraint** — DB-level uniqueness enforced for user+post and user+comment likes

### 🔧 Shared / Infrastructure
- **BaseModel** — UUID primary key, `created_time`, `updated_time` for all models
- **Custom Pagination** — 10 items per page with `next`, `previous`, `count`, `results`
- **Async Email Sending** — `threading.Thread` used for non-blocking email delivery
- **Input Validation Utilities** — Regex-based email/phone/username type checker
- **Twilio SMS Integration** — Ready-to-use `send_phone_code()` utility
- **Environment Variables** — All secrets managed via `python-decouple`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.14 |
| **Framework** | Django 6.0.6 |
| **REST API** | Django REST Framework |
| **Auth** | JWT via `djangorestframework-simplejwt` |
| **Database** | PostgreSQL (`psycopg2`) |
| **ORM** | Django ORM |
| **SMS** | Twilio |
| **Email** | Django Email + HTML templates + Threading |
| **Phone Validation** | `phonenumbers` library |
| **Image Handling** | Pillow |
| **Config** | `python-decouple` (.env) |
| **Package Manager** | Pipenv |

---

## 📁 Project Structure

```
instagram_clone/
├── instagram_clone/          # Project config
│   ├── settings.py           # JWT, DRF, DB, media config
│   ├── urls.py               # Root URL routing
│   └── wsgi.py
│
├── users/                    # User auth app
│   ├── models.py             # User (AbstractUser), UserConfirmation
│   ├── serializers.py        # SignUp, Login, ChangeInfo, ForgotPassword, Reset
│   ├── views.py              # All auth views
│   └── urls.py
│
├── post/                     # Post & social features app
│   ├── models.py             # Post, PostComment, PostLike, CommentLike
│   ├── serializers.py        # PostSerializer, CommentSerializer, LikeSerializers
│   ├── views.py              # CRUD + Like toggle views
│   └── urls.py
│
├── shared/                   # Reusable utilities
│   ├── models.py             # BaseModel (UUID, timestamps)
│   ├── custom_pagination.py  # CustomPagination
│   └── utils.py              # Email/SMS sender, regex validators
│
├── templates/
│   └── email/authentication/
│       └── activate_account.html   # OTP email template
│
├── .env                      # Environment variables (not committed)
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

Install all:
```bash
pipenv install
```

---

## 🔐 Authentication Flow

The registration process follows a **4-step pipeline**:

```
Step 1: POST /users/signup/
        → provide email or phone
        → system sends OTP code
        → auth_status: NEW

Step 2: POST /users/verify/
        → submit OTP code
        → auth_status: CODE_VERIFIED

Step 3: PATCH /users/update-info/
        → set first_name, last_name, username, password
        → auth_status: DONE

Step 4: PUT /users/update-photo/
        → upload profile photo
        → auth_status: PHOTO_DONE
```

All endpoints use **JWT Bearer tokens**:
```
Authorization: Bearer <access_token>
```

---

## 📌 API Endpoints

### Users (`/users/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/users/signup/` | ❌ | Register with email or phone |
| `POST` | `/users/verify/` | ✅ | Submit OTP verification code |
| `GET` | `/users/newverify/` | ✅ | Request a new OTP code |
| `PATCH` | `/users/update-info/` | ✅ | Set username, name, password |
| `PUT` | `/users/update-photo/` | ✅ | Upload profile photo |
| `POST` | `/users/login/` | ❌ | Login (email/phone/username) |
| `POST` | `/users/login/refresh/` | ❌ | Refresh access token |
| `POST` | `/users/logout/` | ✅ | Logout & blacklist token |
| `POST` | `/users/forgot-password/` | ❌ | Send reset OTP |
| `PATCH` | `/users/reset-password/` | ✅ | Set new password |

### Posts (`/post/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/post/list/` | Optional | List all posts (paginated) |
| `POST` | `/post/create/` | ✅ | Create a post |
| `GET/PUT/DELETE` | `/post/<uuid>/` | Optional/✅ | Get, update, or delete a post |
| `GET` | `/post/<uuid>/comments/` | ✅ | List comments on a post |
| `POST` | `/post/<uuid>/comments/create/` | ✅ | Add a comment to a post |
| `GET` | `/post/<uuid>/likes/` | ❌ | List likes on a post |
| `POST/DELETE` | `/post/<uuid>/create-delete-likes/` | ✅ | Like or unlike a post |
| `GET/PUT/DELETE` | `/post/comments/<uuid>/` | ❌ | Get, update, delete a comment |
| `GET` | `/post/comments/<uuid>/likes/` | ❌ | List likes on a comment |
| `POST/DELETE` | `/post/comments/<uuid>/create-delete-likes/` | ✅ | Like or unlike a comment |

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
| `photo` | ImageField | `user_photos/` upload path |

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
| `caption` | TextField | Max 5000 chars |

### PostComment
| Field | Type | Notes |
|---|---|---|
| `author` | FK → User | |
| `post` | FK → Post | |
| `comment` | TextField | Max 1000 chars |
| `parent` | FK → self | Nullable, for nested replies |

### PostLike / CommentLike
- Unique constraint on `(author, post)` and `(author, comment)` — one like per user per item

---

## 🔄 JWT Configuration

```python
ACCESS_TOKEN_LIFETIME  = 5 minutes
REFRESH_TOKEN_LIFETIME = 1 day
ALGORITHM              = HS256
AUTH_HEADER_TYPES      = ("Bearer",)
TOKEN_BLACKLIST        = enabled (for logout)
```

---

## 👤 Author

**Aziz** — [github.com/aziz-200](https://github.com/aziz-200)
