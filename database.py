import os
from typing import Any

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()


class Row(dict):
    def __init__(self, data):
        if isinstance(data, dict):
            super().__init__(data)
        elif isinstance(data, (tuple, list)):
            super().__init__()
        else:
            super().__init__({"value": data})

    def __getitem__(self, key):
        if isinstance(key, int):
            values = list(self.values())
            if 0 <= key < len(values):
                return values[key]
            raise IndexError(key)
        return super().__getitem__(key)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


class DBConnection:
    def __init__(self, connection):
        self._connection = connection

    def execute(self, query, params=None):
        params = () if params is None else params
        if isinstance(params, (list, tuple)):
            param_tuple = tuple(params)
        else:
            param_tuple = (params,)

        if "?" in query:
            query = query.replace("?", "%s")

        cursor = self._connection.cursor(dictionary=True)
        cursor.execute(query, param_tuple)
        return DBCursor(cursor)

    def cursor(self, dictionary=True):
        return DBCursor(self._connection.cursor(dictionary=dictionary))

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()

    def __getattr__(self, name):
        return getattr(self._connection, name)


class DBCursor:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=None):
        params = () if params is None else params
        if isinstance(params, (list, tuple)):
            param_tuple = tuple(params)
        else:
            param_tuple = (params,)

        if "?" in query:
            query = query.replace("?", "%s")
        self._cursor.execute(query, param_tuple)
        return self

    def executemany(self, query, params):
        if "?" in query:
            query = query.replace("?", "%s")
        self._cursor.executemany(query, params)
        return self

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        if isinstance(row, dict):
            return Row(row)
        if isinstance(row, (tuple, list)):
            columns = getattr(self._cursor, "column_names", []) or []
            if columns:
                return Row(dict(zip(columns, row)))
            return Row(row)
        return Row({"value": row})

    def fetchall(self):
        rows = self._cursor.fetchall()
        result = []
        for row in rows:
            if isinstance(row, dict):
                result.append(Row(row))
            elif isinstance(row, (tuple, list)):
                columns = getattr(self._cursor, "column_names", []) or []
                if columns:
                    result.append(Row(dict(zip(columns, row))))
                else:
                    result.append(Row(row))
            else:
                result.append(Row({"value": row}))
        return result

    def close(self):
        self._cursor.close()

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def description(self):
        return self._cursor.description

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class Config:
    DB_HOST = os.getenv("DB_HOST") or os.getenv("MYSQL_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT") or os.getenv("MYSQL_PORT", "3306"))
    DB_USER = os.getenv("DB_USER") or os.getenv("MYSQL_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("MYSQL_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME") or os.getenv("MYSQL_DATABASE", "smartagri")
    DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")
    DB_COLLATION = os.getenv("DB_COLLATION", "utf8mb4_unicode_ci")


def _get_connection_kwargs(database=None):
    kwargs = {
        "host": Config.DB_HOST,
        "port": Config.DB_PORT,
        "user": Config.DB_USER,
        "password": Config.DB_PASSWORD,
        "charset": Config.DB_CHARSET,
        "use_pure": True,
    }
    if database:
        kwargs["database"] = database
    return kwargs


def ensure_database_exists():
    connection = mysql.connector.connect(**_get_connection_kwargs())
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET {Config.DB_CHARSET} COLLATE {Config.DB_COLLATION}"
        )
        connection.commit()
        cursor.close()
    finally:
        connection.close()


def get_db_connection():
    try:
        connection = mysql.connector.connect(**_get_connection_kwargs(database=Config.DB_NAME))
    except Error as exc:
        if getattr(exc, "errno", None) == 1049:
            ensure_database_exists()
            connection = mysql.connector.connect(**_get_connection_kwargs(database=Config.DB_NAME))
        else:
            raise
    return DBConnection(connection)


def _create_table(connection, statement):
    cursor = connection.cursor()
    cursor.execute(statement)
    cursor.close()


def initialize_database(connection=None):
    ensure_database_exists()
    if connection is None:
        connection = get_db_connection()

    statements = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL UNIQUE,
            role VARCHAR(30) NOT NULL,
            full_name VARCHAR(150) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            phone VARCHAR(20) NOT NULL UNIQUE,
            alternate_phone VARCHAR(20) DEFAULT NULL,
            password VARCHAR(255) NOT NULL,
            profile_photo VARCHAR(255) DEFAULT NULL,
            house_no VARCHAR(100) DEFAULT NULL,
            street VARCHAR(150) DEFAULT NULL,
            village VARCHAR(150) DEFAULT NULL,
            mandal VARCHAR(150) DEFAULT NULL,
            district VARCHAR(150) DEFAULT NULL,
            state VARCHAR(150) DEFAULT NULL,
            pin_code VARCHAR(20) DEFAULT NULL,
            country VARCHAR(100) DEFAULT 'India',
            status VARCHAR(30) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_users_role (role),
            INDEX idx_users_email (email),
            INDEX idx_users_phone (phone),
            INDEX idx_users_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS farmers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            farm_name VARCHAR(150) DEFAULT NULL,
            land_acres VARCHAR(50) DEFAULT NULL,
            main_crops VARCHAR(255) DEFAULT NULL,
            farming_type VARCHAR(100) DEFAULT NULL,
            irrigation_type VARCHAR(100) DEFAULT NULL,
            preferred_language VARCHAR(50) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            CONSTRAINT fk_farmers_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_farmers_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS providers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            business_name VARCHAR(150) DEFAULT NULL,
            owner_name VARCHAR(150) DEFAULT NULL,
            machinery_category VARCHAR(150) DEFAULT NULL,
            service_category VARCHAR(150) DEFAULT NULL,
            equipment VARCHAR(255) DEFAULT NULL,
            rental_available VARCHAR(50) DEFAULT NULL,
            service_area VARCHAR(255) DEFAULT NULL,
            gst_number VARCHAR(50) DEFAULT NULL,
            website VARCHAR(255) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            CONSTRAINT fk_providers_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_providers_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS buyers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            company_name VARCHAR(150) DEFAULT NULL,
            contact_person VARCHAR(150) DEFAULT NULL,
            business_type VARCHAR(100) DEFAULT NULL,
            interested_crops VARCHAR(255) DEFAULT NULL,
            buying_locations VARCHAR(255) DEFAULT NULL,
            daily_buying_capacity VARCHAR(100) DEFAULT NULL,
            gst_number VARCHAR(50) DEFAULT NULL,
            website VARCHAR(255) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            CONSTRAINT fk_buyers_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_buyers_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS technologies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            category VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            working_principle TEXT NOT NULL,
            advantages TEXT NOT NULL,
            limitations TEXT NOT NULL,
            estimated_cost VARCHAR(100) DEFAULT NULL,
            suitable_crops VARCHAR(255) DEFAULT NULL,
            suitable_farm_size VARCHAR(100) DEFAULT NULL,
            image_url VARCHAR(255) DEFAULT NULL,
            video_link VARCHAR(255) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_technologies_category (category),
            INDEX idx_technologies_name (name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS machinery_categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS machinery (
            id INT AUTO_INCREMENT PRIMARY KEY,
            provider_id INT NOT NULL,
            name VARCHAR(150) NOT NULL,
            category VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            brand VARCHAR(100) DEFAULT NULL,
            model VARCHAR(100) DEFAULT NULL,
            purchase_price DECIMAL(10,2) DEFAULT 0.00,
            rental_price_per_day DECIMAL(10,2) DEFAULT 0.00,
            availability VARCHAR(30) DEFAULT 'available',
            location VARCHAR(150) DEFAULT NULL,
            image_url VARCHAR(255) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            CONSTRAINT fk_machinery_provider FOREIGN KEY (provider_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_machinery_provider (provider_id),
            INDEX idx_machinery_category (category),
            INDEX idx_machinery_location (location)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS machinery_bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            machinery_id INT NOT NULL,
            user_id INT NOT NULL,
            booking_date DATE NOT NULL,
            rental_days INT NOT NULL DEFAULT 1,
            status VARCHAR(30) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            CONSTRAINT fk_bookings_machinery FOREIGN KEY (machinery_id) REFERENCES machinery(id) ON DELETE CASCADE,
            CONSTRAINT fk_bookings_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_bookings_status (status),
            INDEX idx_bookings_date (booking_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS weather (
            id INT AUTO_INCREMENT PRIMARY KEY,
            district VARCHAR(150) NOT NULL,
            state VARCHAR(150) NOT NULL,
            temperature VARCHAR(50) DEFAULT NULL,
            humidity VARCHAR(50) DEFAULT NULL,
            rainfall VARCHAR(50) DEFAULT NULL,
            forecast TEXT DEFAULT NULL,
            weather_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_weather_date (weather_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS government_schemes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            scheme_name VARCHAR(150) NOT NULL,
            description TEXT NOT NULL,
            eligibility TEXT NOT NULL,
            benefits TEXT NOT NULL,
            required_documents TEXT NOT NULL,
            application_process TEXT NOT NULL,
            official_link VARCHAR(255) DEFAULT NULL,
            start_date DATE DEFAULT NULL,
            end_date DATE DEFAULT NULL,
            is_sample TINYINT(1) DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_schemes_name (scheme_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS market_prices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            crop_name VARCHAR(100) NOT NULL,
            market_name VARCHAR(150) NOT NULL,
            district VARCHAR(100) NOT NULL,
            state VARCHAR(100) NOT NULL,
            min_price DECIMAL(10,2) NOT NULL,
            max_price DECIMAL(10,2) NOT NULL,
            modal_price DECIMAL(10,2) NOT NULL,
            price_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_market_prices_crop (crop_name),
            INDEX idx_market_prices_date (price_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS crops (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(150) NOT NULL UNIQUE,
            season VARCHAR(100) DEFAULT NULL,
            description TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            expense_date DATE NOT NULL,
            category VARCHAR(100) NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            description TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_expenses_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_expenses_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS profits (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            profit_date DATE NOT NULL,
            category VARCHAR(100) NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            description TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_profits_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_profits_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS ai_predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            crop_name VARCHAR(100) NOT NULL,
            prediction_text TEXT NOT NULL,
            confidence_score DECIMAL(5,2) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_ai_predictions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_ai_predictions_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(150) NOT NULL,
            message TEXT NOT NULL,
            is_read TINYINT(1) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_notifications_user (user_id),
            INDEX idx_notifications_read (is_read)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS community_posts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(150) DEFAULT NULL,
            content TEXT NOT NULL,
            image_path VARCHAR(255) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            CONSTRAINT fk_community_posts_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_community_posts_user (user_id),
            INDEX idx_community_posts_created (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS community_post_images (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            image_path VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_post_images_post FOREIGN KEY (post_id) REFERENCES community_posts(id) ON DELETE CASCADE,
            INDEX idx_post_images_post (post_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS community_comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            user_id INT NOT NULL,
            comment_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_comments_post FOREIGN KEY (post_id) REFERENCES community_posts(id) ON DELETE CASCADE,
            CONSTRAINT fk_comments_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_comments_post (post_id),
            INDEX idx_comments_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS community_likes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            user_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(post_id, user_id),
            CONSTRAINT fk_likes_post FOREIGN KEY (post_id) REFERENCES community_posts(id) ON DELETE CASCADE,
            CONSTRAINT fk_likes_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_likes_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS friendships (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            friend_id INT NOT NULL,
            status VARCHAR(30) DEFAULT 'accepted',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, friend_id),
            CONSTRAINT fk_friendships_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_friendships_friend FOREIGN KEY (friend_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS follow_requests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender_id INT NOT NULL,
            receiver_id INT NOT NULL,
            status VARCHAR(30) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(sender_id, receiver_id),
            CONSTRAINT fk_follow_sender FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_follow_receiver FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender_id INT NOT NULL,
            receiver_id INT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_chat_sender FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_chat_receiver FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_chat_sender (sender_id),
            INDEX idx_chat_receiver (receiver_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS `groups` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            description TEXT DEFAULT NULL,
            created_by INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_groups_creator FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_groups_name (name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS group_members (
            id INT AUTO_INCREMENT PRIMARY KEY,
            group_id INT NOT NULL,
            user_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(group_id, user_id),
            CONSTRAINT fk_group_members_group FOREIGN KEY (group_id) REFERENCES `groups`(id) ON DELETE CASCADE,
            CONSTRAINT fk_group_members_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_group_members_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS advertisements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_name VARCHAR(150) NOT NULL,
            category VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            seller VARCHAR(150) NOT NULL,
            location VARCHAR(150) DEFAULT NULL,
            contact_details VARCHAR(255) DEFAULT NULL,
            image_url VARCHAR(255) DEFAULT NULL,
            status VARCHAR(30) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_ads_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            report_type VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            status VARCHAR(30) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_reports_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_reports_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            subject VARCHAR(150) DEFAULT NULL,
            message TEXT NOT NULL,
            rating INT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_feedback_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_feedback_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            email VARCHAR(150) NOT NULL,
            phone VARCHAR(20) DEFAULT NULL,
            subject VARCHAR(150) DEFAULT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_contact_email (email)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT DEFAULT NULL,
            activity_type VARCHAR(100) NOT NULL,
            description TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_activity_logs_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            INDEX idx_activity_user (user_id),
            INDEX idx_activity_type (activity_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS farmer_profiles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            farm_name VARCHAR(150) DEFAULT NULL,
            land_acres VARCHAR(50) DEFAULT NULL,
            main_crops VARCHAR(255) DEFAULT NULL,
            farming_type VARCHAR(100) DEFAULT NULL,
            irrigation_type VARCHAR(100) DEFAULT NULL,
            preferred_language VARCHAR(50) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_farmer_profiles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_farmer_profiles_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS provider_profiles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            business_name VARCHAR(150) DEFAULT NULL,
            owner_name VARCHAR(150) DEFAULT NULL,
            machinery_category VARCHAR(150) DEFAULT NULL,
            service_category VARCHAR(150) DEFAULT NULL,
            equipment VARCHAR(255) DEFAULT NULL,
            rental_available VARCHAR(50) DEFAULT NULL,
            service_area VARCHAR(255) DEFAULT NULL,
            gst_number VARCHAR(50) DEFAULT NULL,
            website VARCHAR(255) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_provider_profiles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_provider_profiles_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS buyer_profiles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            company_name VARCHAR(150) DEFAULT NULL,
            contact_person VARCHAR(150) DEFAULT NULL,
            business_type VARCHAR(100) DEFAULT NULL,
            interested_crops VARCHAR(255) DEFAULT NULL,
            buying_locations VARCHAR(255) DEFAULT NULL,
            daily_buying_capacity VARCHAR(100) DEFAULT NULL,
            gst_number VARCHAR(50) DEFAULT NULL,
            website VARCHAR(255) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_buyer_profiles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_buyer_profiles_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS post_comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            user_id INT NOT NULL,
            comment_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_post_comments_post FOREIGN KEY (post_id) REFERENCES community_posts(id) ON DELETE CASCADE,
            CONSTRAINT fk_post_comments_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_post_comments_post (post_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS post_likes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            user_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(post_id, user_id),
            CONSTRAINT fk_post_likes_post FOREIGN KEY (post_id) REFERENCES community_posts(id) ON DELETE CASCADE,
            CONSTRAINT fk_post_likes_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_post_likes_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS friend_requests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender_id INT NOT NULL,
            receiver_id INT NOT NULL,
            status VARCHAR(30) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(sender_id, receiver_id),
            CONSTRAINT fk_friend_requests_sender FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_friend_requests_receiver FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS chats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender_id INT NOT NULL,
            receiver_id INT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_chats_sender FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_chats_receiver FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_chats_sender (sender_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    ]

    for statement in statements:
        _create_table(connection, statement)

    connection.commit()
    ensure_admin_account(connection)
    return connection


def ensure_admin_account(connection=None):
    if connection is None:
        connection = get_db_connection()

    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users WHERE email = %s", ("adminsmartagri@gmail.com",))
    existing = cursor.fetchone()
    if existing:
        cursor.close()
        return None

    password_hash = generate_password_hash("Admin@1722")
    cursor.execute(
        """
        INSERT INTO users (
            user_id, role, full_name, email, phone, password, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        ("smartagri", "admin", "SmartAgri Administrator", "adminsmartagri@gmail.com", "7842647363", password_hash, "active"),
    )
    connection.commit()
    cursor.close()
    return True


def password_matches(stored_password, provided_password):
    if not stored_password:
        return False
    if stored_password.startswith("pbkdf2") or stored_password.startswith("scrypt") or stored_password.startswith("argon"):
        try:
            return check_password_hash(stored_password, provided_password)
        except ValueError:
            return False
    return stored_password == provided_password
