CREATE DATABASE IF NOT EXISTS smartagri;
USE smartagri;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(150) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  phone VARCHAR(20) DEFAULT NULL,
  password VARCHAR(255) DEFAULT NULL,
  role ENUM('farmer','provider','buyer','admin') NOT NULL,
  status ENUM('active','pending','blocked') DEFAULT 'active',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_users_role (role)
);

CREATE TABLE IF NOT EXISTS farmer_profiles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  state VARCHAR(100) DEFAULT NULL,
  district VARCHAR(100) DEFAULT NULL,
  village VARCHAR(100) DEFAULT NULL,
  preferred_language VARCHAR(50) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS provider_profiles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  business_name VARCHAR(150) DEFAULT NULL,
  owner_name VARCHAR(150) DEFAULT NULL,
  address TEXT DEFAULT NULL,
  service_area VARCHAR(150) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS buyer_profiles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  company_name VARCHAR(150) DEFAULT NULL,
  contact_person VARCHAR(150) DEFAULT NULL,
  address TEXT DEFAULT NULL,
  buying_locations VARCHAR(255) DEFAULT NULL,
  verification_status ENUM('pending','approved','rejected') DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

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
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS machinery (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  category VARCHAR(100) NOT NULL,
  description TEXT NOT NULL,
  brand VARCHAR(100) DEFAULT NULL,
  model VARCHAR(100) DEFAULT NULL,
  purchase_price DECIMAL(10,2) DEFAULT 0.00,
  rental_price_per_day DECIMAL(10,2) DEFAULT 0.00,
  availability ENUM('available','rented','maintenance') DEFAULT 'available',
  location VARCHAR(150) DEFAULT NULL,
  provider_id INT NOT NULL,
  image_url VARCHAR(255) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (provider_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS machinery_reviews (
  id INT AUTO_INCREMENT PRIMARY KEY,
  machinery_id INT NOT NULL,
  user_id INT NOT NULL,
  rating INT NOT NULL,
  review_text TEXT DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (machinery_id) REFERENCES machinery(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS buyer_requirements (
  id INT AUTO_INCREMENT PRIMARY KEY,
  buyer_id INT NOT NULL,
  crop_name VARCHAR(100) NOT NULL,
  quantity_required VARCHAR(100) DEFAULT NULL,
  buying_price DECIMAL(10,2) DEFAULT 0.00,
  location VARCHAR(150) DEFAULT NULL,
  service_area VARCHAR(150) DEFAULT NULL,
  contact_info VARCHAR(255) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ai_recommendations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  crop VARCHAR(100) NOT NULL,
  farm_size VARCHAR(100) DEFAULT NULL,
  soil_type VARCHAR(100) DEFAULT NULL,
  water_availability VARCHAR(100) DEFAULT NULL,
  budget VARCHAR(100) DEFAULT NULL,
  location VARCHAR(100) DEFAULT NULL,
  season VARCHAR(100) DEFAULT NULL,
  recommendation_text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS crop_diseases (
  id INT AUTO_INCREMENT PRIMARY KEY,
  crop_name VARCHAR(100) NOT NULL,
  disease_name VARCHAR(150) NOT NULL,
  symptoms TEXT NOT NULL,
  causes TEXT NOT NULL,
  recommended_actions TEXT NOT NULL,
  prevention_tips TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS diagnosis_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  crop_name VARCHAR(100) NOT NULL,
  symptoms TEXT NOT NULL,
  problem_description TEXT DEFAULT NULL,
  result_text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS community_posts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(150) DEFAULT NULL,
  content TEXT NOT NULL,
  image_url VARCHAR(255) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS post_comments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  post_id INT NOT NULL,
  user_id INT NOT NULL,
  comment_text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES community_posts(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS post_likes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  post_id INT NOT NULL,
  user_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(post_id, user_id),
  FOREIGN KEY (post_id) REFERENCES community_posts(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_connections (
  id INT AUTO_INCREMENT PRIMARY KEY,
  follower_id INT NOT NULL,
  following_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(follower_id, following_id),
  FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (following_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS community_groups (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  description TEXT DEFAULT NULL,
  created_by INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS group_members (
  id INT AUTO_INCREMENT PRIMARY KEY,
  group_id INT NOT NULL,
  user_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(group_id, user_id),
  FOREIGN KEY (group_id) REFERENCES community_groups(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS messages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sender_id INT NOT NULL,
  receiver_id INT NOT NULL,
  message_text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
);

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
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS saved_schemes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  scheme_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, scheme_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (scheme_id) REFERENCES government_schemes(id) ON DELETE CASCADE
);

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
  status ENUM('pending','approved','rejected') DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(150) NOT NULL,
  message TEXT NOT NULL,
  is_read TINYINT(1) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS enquiries (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  item_type VARCHAR(50) NOT NULL,
  item_id INT NOT NULL,
  message TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

INSERT INTO users (full_name, email, phone, password, role, status) VALUES
('Admin User', 'adminsmartagri@gmail.com', '7842647363', 'Admin@1722', 'admin', 'active'),
('Farmer One', 'farmer@smartagri.com', '8888888888', 'Vishnu@1722', 'farmer', 'active'),
('Provider One', 'provider@smartagri.com', '7777777777', 'Vishnu@1722', 'provider', 'active'),
('Buyer One', 'buyer@smartagri.com', '6666666666', 'Vishnu@1722', 'buyer', 'active');

INSERT INTO farmer_profiles (user_id, state, district, village, preferred_language) VALUES
(2, 'Maharashtra', 'Pune', 'Khed', 'Marathi');

INSERT INTO provider_profiles (user_id, business_name, owner_name, address, service_area) VALUES
(3, 'AgriTech Services', 'Asha Rao', 'Pune, Maharashtra', 'Pune District');

INSERT INTO buyer_profiles (user_id, company_name, contact_person, address, buying_locations, verification_status) VALUES
(4, 'FreshMart', 'Ravi Sharma', 'Mumbai, Maharashtra', 'Pune, Nashik', 'approved');

INSERT INTO technologies (name, category, description, working_principle, advantages, limitations, estimated_cost, suitable_crops, suitable_farm_size, image_url, video_link) VALUES
('Drone Spraying', 'Drones', 'Aerial crop spraying with precision application.', 'Uses GPS-enabled drones to spray nutrients and pesticides precisely.', 'Saves time and reduces chemical wastage.', 'Needs skilled operation and regulatory approval.', '₹1,50,000', 'Vegetables, Rice, Cotton', '5 acres and above', 'https://via.placeholder.com/300', 'https://www.youtube.com/watch?v=example'),
('Smart Irrigation Controller', 'Smart irrigation', 'Automated irrigation based on soil moisture and weather.', 'Uses sensors and timers to optimize water application.', 'Reduces water use and labor.', 'Requires initial setup and maintenance.', '₹40,000', 'Vegetables, Fruits, Sugarcane', '2 acres and above', 'https://via.placeholder.com/300', 'https://www.youtube.com/watch?v=example');

INSERT INTO machinery (name, category, description, brand, model, purchase_price, rental_price_per_day, availability, location, provider_id, image_url) VALUES
('Tractor 35 HP', 'Automated machinery', 'Reliable tractor for tilling and transport.', 'Mahindra', 'Yuvraj', 850000.00, 2500.00, 'available', 'Pune', 3, 'https://via.placeholder.com/300');

INSERT INTO crop_diseases (crop_name, disease_name, symptoms, causes, recommended_actions, prevention_tips) VALUES
('Tomato', 'Late Blight', 'Dark patches on leaves, white fungal growth', 'Cool humid weather', 'Remove infected leaves, use fungicide', 'Ensure good spacing and airflow'),
('Rice', 'Blast', 'Spindle-shaped lesions on leaves', 'High humidity and nitrogen overload', 'Use resistant seed and fungicide', 'Avoid over-fertilization');

INSERT INTO market_prices (crop_name, market_name, district, state, min_price, max_price, modal_price, price_date) VALUES
('Tomato', 'Pune Mandi', 'Pune', 'Maharashtra', 1200.00, 1800.00, 1500.00, '2026-07-17'),
('Wheat', 'Nashik Mandi', 'Nashik', 'Maharashtra', 2200.00, 2600.00, 2400.00, '2026-07-17');

INSERT INTO government_schemes (scheme_name, description, eligibility, benefits, required_documents, application_process, official_link, start_date, end_date, is_sample) VALUES
('PM-KISAN', 'Income support for farmers', 'Small and marginal farmers', 'Direct cash support', 'Aadhaar, land records', 'Apply through portal', 'https://pmkisan.gov.in', '2026-01-01', '2026-12-31', 1),
('Kisan Credit Card', 'Credit support for crop cultivation', 'Farmers with valid identity', 'Credit facility', 'Aadhaar, bank account', 'Apply through bank', 'https://example.gov.in', '2026-01-01', '2026-12-31', 1);

INSERT INTO advertisements (product_name, category, description, price, seller, location, contact_details, image_url, status) VALUES
('Organic Fertilizer', 'Fertilizers', 'Organic fertilizer for vegetables.', 1200.00, 'Green Valley', 'Pune', '9999999999', 'https://via.placeholder.com/300', 'approved');

INSERT INTO notifications (user_id, title, message) VALUES
(2, 'Weather Alert', 'High temperature expected today.');
