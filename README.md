# SmartAgri

SmartAgri is a Flask + MySQL agriculture platform for farmers, service providers, buyers, and administrators. It provides role-based dashboards, marketplace and machinery listings, agricultural information, community features, and administrative tools.

## Features

- Role-based registration, editable profiles, and dashboards for farmers, service providers, and buyers
- Provider-owned machinery and service listings with create, edit, availability, and delete controls
- Administrator dashboard and management of users, machinery, schemes, technologies, and community moderation
- Machinery listings and a searchable technology library with educational content, images, and videos
- Government scheme catalog
- Community feed with editable posts, threaded comments/replies, likes, and direct messages
- Buyer/provider reviews for farmers who have exchanged direct messages, with administrator visibility controls
- Guided crop-diagnosis workflow with photo upload, crop selection, symptom questions, and saved results
- Weather lookup with location search, forecasts, alerts, and agricultural advisories
- Market-price pages with optional external API configuration and database-backed fallback data
- Interface translations for English and ten Indian languages

## Tech stack

- Python 3.10+
- Flask
- MySQL
- mysql-connector-python
- Bootstrap 5
- Werkzeug security
- Flask session-based role authentication

## Diagnosis workflow

The crop-diagnosis feature accepts JPG, JPEG, and PNG photos up to 5 MB. Users select a crop, answer symptom questions, and receive a suggested diagnosis with recommendations. Uploaded images are stored under `static/uploads/diagnosis/`, and saved results are kept in the database.

**The current diagnosis is a demonstration workflow, not a trained image-recognition model.** Disease candidates and confidence values are demo data; do not rely on the result as professional agricultural advice. Consult a local agricultural expert before treating crops.

## Project structure

- app.py — application entry point
- config.py — database and app configuration
- database.py — schema creation and database setup
- routes/ — Flask blueprints for auth, admin, farmer, buyer, provider, machinery, market, weather, schemes, community, and AI
- templates/ — HTML pages for all app screens
- static/ — CSS, JS, and uploaded assets
- translations/ — English and Indian-language translation dictionaries (English, Telugu, Hindi, Tamil, Kannada, Malayalam, Marathi, Bengali, Gujarati, Punjabi, and Odia)
- tests/ — validation tests for registration and admin flows

## Prerequisites

- Python 3.10+
- MySQL server running locally
- Access to the database named smartagri

## Setup

1. Open a terminal in the project root.
2. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Ensure MySQL is running. On first connection, the runtime initializer creates the `smartagri` database if it does not exist, then creates or updates the application schema. The configured MySQL account therefore needs permission to create the database and tables and to add missing columns.

5. Create a .env file in the project root if it does not already exist:

```env
SECRET_KEY=replace-with-a-long-random-secret
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=smartagri
WEATHER_API_KEY=
OPENWEATHER_API_KEY=
MARKET_API_URL=
MARKET_API_KEY=
MARKET_API_TIMEOUT=10
WEATHER_API_TIMEOUT=10
ADMIN_EMAIL=
ADMIN_PHONE=
ADMIN_PASSWORD=
ADMIN_FULL_NAME=SmartAgri Administrator
DEMO_USER_PASSWORD=
```

`SECRET_KEY` must be a private, random value for deployments. If it is omitted,
the app uses a randomly generated process-local key; sessions will not survive
restarts or be shared across workers. The optional `ADMIN_EMAIL`, `ADMIN_PHONE`,
and `ADMIN_PASSWORD` variables create an initial administrator only when that
email and phone are not already present. Set all three to create the account;
choose a strong, private password. The project does not ship a default
administrator password. Alternatively, register through the application as a
farmer, provider, or buyer; administrator accounts are configured separately.

`WEATHER_API_KEY` (or `OPENWEATHER_API_KEY`) enables live weather information.
Without a valid key, weather information is unavailable. `MARKET_API_URL` and
`MARKET_API_KEY` are optional; without an external market provider, the
application uses its database-backed market data rather than presenting
fabricated live prices.

## Run the app

```bash
python app.py
```

Then open:

- http://localhost:5000

## Admin access

The admin dashboard is available after logging in as an admin user. The admin can manage:

- farmers
- providers
- buyers
- machinery
- schemes
- technologies
- dashboard data and records

## Role workspaces, profiles, and community

Each account role has a separate dashboard. Users can edit their own contact,
address, and role-specific profile details at `/auth/profile/edit`. Service
providers manage their own marketplace listings from `/provider/services`;
listing changes are scoped to the signed-in provider. The public marketplace
shows available listings and links to provider details and reviews.

### Farmer dashboard

The farmer workspace brings common farming tools together in one dashboard.
Farmers can open their profile, browse the technology library and marketplace,
find buyer crop requirements, check weather and government schemes, visit the
community, and access the AI assistant or guided crop diagnosis. Dashboard
panels also show recent community activity, available machinery and services,
recent database-backed market prices, active schemes, and technologies. Panels
with no available records display an empty state. Market prices shown here are
stored observations and are not necessarily live prices.

Community members can create and manage their own posts and comments, reply to
comments, and exchange direct messages. Farmers can leave one review per buyer
or provider after an actual direct-message exchange; this eligibility check does
not claim that a purchase or other transaction took place. Administrators can
hide or restore posts, comments, and reviews. Moderation preserves the content
and records visibility actions in the database.

The Messages page separately lists existing conversations and supports a
server-side search of active farmers, buyers, and service providers by name or
email, with role filtering and pagination. Starting a chat opens or reuses the
participant pair's conversation and retains existing messages.

### Provider reviews

Provider reviews are available from a provider's machinery details page. The
link uses the listing's `provider_id` (the provider's user ID), not the
machinery record ID. Signed-in farmers can submit or update one review per
provider after at least one message exists between the farmer and provider.
Eligibility checks the `sender_id` and `receiver_id` columns in `messages`,
including older messages without a `conversation_id`. Ratings are limited to
1–5 stars and comments to 2,000 characters. Other users can read public reviews;
moderated reviews remain hidden.

The runtime schema initializer already creates `user_reviews` with reviewer and
target user IDs, rating, comment, timestamps, a unique reviewer/target key, and
moderation fields. No separate migration is needed for this feature. Existing
reviews are retained.

The buyer Marketplace combines saved mandi price observations with approved
seller product listings. Farmers and providers can publish and manage their own
produce listings, including the `Grains & Cereals` and `Vegetables` categories,
asking price, quantity, unit, location, availability, and optional image URL.
Mandi prices remain distinct from seller-entered listing prices. Product
ownership, quantity, unit, and availability use additive advertisement-table
columns; existing listings and stored prices are retained.

Buyers can also publish crop purchase requirements from the Buyer dashboard.
Each request stores the buyer-entered crop, category, required quantity, unit,
per-unit offer, server-calculated estimated budget, and optional quality,
location, delivery, and additional requirements. Farmers can filter active
requests and send one current offer per request through SmartAgri. Buyers review,
accept, or reject offers in **My Crop Requirements** and can message farmers
privately. Accepting an offer changes the request to `accepted`, not
`fulfilled`; the buyer must explicitly mark it fulfilled. Buyers can close or
cancel active requests, and only the request owner can edit or change its
status. Admins have a read-only requirements and offer-count report.

The feature routes are `GET/POST /crop-requirements/new` and
`GET /crop-requirements/mine` for buyers, `GET /crop-requirements/` and
`POST /crop-requirements/<id>/offers` for farmers, buyer-owned
`GET/POST /crop-requirements/<id>/edit`, buyer status/offer response POSTs,
and the admin report at `GET /crop-requirements/admin` with an admin-only
`POST /crop-requirements/admin/<id>/close` moderation action. Mutating forms
use the existing session-backed CSRF protection.

The runtime schema initializer creates `crop_purchase_requirements` and
`crop_requirement_offers` with foreign keys and indexes on startup. Matching
`CREATE TABLE IF NOT EXISTS` definitions are included in the SQL reference
files; the runtime initializer in `database.py` is canonical. Existing user,
listing, message, and market-price records are not replaced.

The runtime schema initializer applies additive community updates, including
threaded-comment and visibility fields, user reviews, and moderation records.
It does not require replacing existing user, profile, listing, or community
tables. Updated authentication, profile, provider-listing, community, review,
scheme, and community-moderation forms use session-backed CSRF tokens.
See [IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md) for the
route/template/table/permission crosswalk and remaining scope notes.

## Technology library

The public Technologies link opens the searchable technology library. Active entries are read from the existing `technology_library` table; selecting a card opens one database-driven detail page by slug. Older numeric detail URLs remain supported.

### Public routes

| Route | Purpose |
| --- | --- |
| `GET /technologies/` | Search and filter active technologies |
| `GET /technologies/<slug>` | View the technology overview, educational sections, images, videos, and related technologies |
| `GET /technologies/<id>` | Compatibility route for older links |
| `GET /technologies/<id>/reels` | Open the existing technology-specific reels feed |

Search matches technology name, short description, description, and category. The category filter uses the active categories stored in the database. The public grid uses four columns on wide screens, two on tablet widths, and one on mobile.

### Technology data and defaults

`technology_library` remains the source of technology records; the older `technologies` table is not duplicated or repurposed. The runtime initializer adds missing library columns and creates `technology_images` as needed. It backfills unique slugs for existing records and inserts each of the 30 configured defaults only when its technology name is absent. Blank educational fields on matching defaults may be filled, but populated values are preserved. Existing library records and admin-created entries are not deleted. As a result, an existing installation may show more than 30 technologies.

The detail template reads these fields from the selected technology: overview, what it is, how it works, main uses, benefits, components, applications, advantages, limitations, and future scope. Text-area lists may use one item per line; the page presents those lines as a list or process steps.

### Related images and videos

Images are stored in `technology_images` and associated by `technology_id`. Active images appear in the detail-page gallery; selecting one opens a larger view. The admin uploader accepts JPG, JPEG, PNG, and WebP files up to 5 MB. Uploads are stored under `static/uploads/technologies/` with generated filenames.

Videos are stored in the existing `technology_videos` table and associated by `technology_id`. Detail pages show all active videos for that technology. YouTube watch, short, Shorts, and embed URLs are validated and normalized to an individual video ID before embedding. No video URLs are seeded: an administrator must provide a real video URL. Invalid URLs are rejected, and an embedding-disabled video keeps its original YouTube link.

The related-content schema is:

- `technology_library`: unique technology name and slug, category, icon, descriptions, educational sections, banner path, status, and timestamps.
- `technology_images`: technology ID, image path, title, alt text, description, active status, and timestamps. Its foreign key cascades only when its owning technology is deleted.
- `technology_videos`: technology ID, title, description, original YouTube URL, extracted video ID, thumbnail URL, active status, and timestamps. Its existing foreign key and per-technology/video unique key are retained.

### Admin workflow

After logging in as an administrator, open `/technologies/admin` or choose Technology Management from the admin dashboard. The manager supports name search, category/status filters, sorting, and counts for related videos and images. Administrators can add technologies without a source-code limit, edit their slug and educational sections, activate/deactivate them, and delete them with confirmation.

Use the manager’s Add Video form to select a technology from the database, enter a YouTube URL, title, description, and status. For images, open a technology’s View page to add, replace, edit metadata/status, or delete images. That page also lists its videos with edit, activate/deactivate, and delete actions. Normal users cannot access these management routes.

The runtime schema and additive migrations are managed by `database.py`; the MySQL account needs permission to create the database and tables and to add missing columns. The app does not require manual SQL scripts to start. `database.sql` and `database_updates.sql` are legacy SQL references with different schema assumptions; review them and back up the database before any manual use. They are not an alternative to the runtime initializer.

## Database seeding

The project includes a demo seeding script for realistic sample data. It inserts only the missing records needed to reach the target totals and preserves the current schema.

Run:

```bash
python seed_data.py
```

Set `DEMO_USER_PASSWORD` to a private password in `.env` before running the
optional seeder. It is used to hash passwords for newly created demo accounts;
there is no built-in shared demo password.

This generates demo records for:

- Farmers: 20
- Providers: 20
- Buyers: 20
- Machinery: 20

## Weather module

The weather module reads from WEATHER_API_KEY or OPENWEATHER_API_KEY. If no valid key is configured, it shows an unavailable state instead of fake data.

## Market price module

The marketplace reads from the database and can also use a configured MARKET_API_URL if available. Without an external provider, the app keeps its safe fallback behavior and avoids fabricated pricing.

## Testing

Run the project tests with:

```bash
.\.venv\Scripts\python.exe -m pytest -q
```

Technology-specific tests can be run with:

```bash
.\.venv\Scripts\python.exe -m pytest tests/test_technology_video_urls.py -q
```

Provider-review flow tests can be run with:

```bash
.\.venv\Scripts\python.exe -m pytest tests/test_provider_reviews.py -q
```

For a manual check, sign in as a farmer, open a provider's machinery details,
choose **Provider reviews**, follow **Message [provider]** and send a message,
then return to the review page. Submit a 1–5 star rating and non-empty comment;
the page should show a success notice and the saved review. Also try an invalid
rating and an empty comment; neither should be saved.

## Notes

- The project is built around role-based access control.
- Data validation and access restrictions are enforced by the existing Flask routes.
- The app is designed to reuse the existing database tables and schemas rather than creating duplicate structures.

## License

This project is intended for academic and demonstration use within the SmartAgri project workspace.
