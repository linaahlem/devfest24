create database financeDB;
show databases;
SELECT * from industries;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Create the 'countries' table
CREATE TABLE countries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Create the 'industries' table
CREATE TABLE industries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Create the 'sizes' table for company sizes (small, medium, large)
CREATE TABLE sizes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Insert all countries into the 'countries' table
INSERT INTO countries (name) VALUES
('Afghanistan'), ('Albania'), ('Algeria'), ('Andorra'), ('Angola'), 
('Antigua and Barbuda'), ('Argentina'), ('Armenia'), ('Australia'), 
('Austria'), ('Azerbaijan'), ('Bahamas'), ('Bahrain'), ('Bangladesh'), 
('Barbados'), ('Belarus'), ('Belgium'), ('Belize'), ('Benin'), 
('Bhutan'), ('Bolivia'), ('Bosnia and Herzegovina'), ('Botswana'), 
('Brazil'), ('Brunei Darussalam'), ('Bulgaria'), ('Burkina Faso'), 
('Burundi'), ('Cabo Verde'), ('Cambodia'), ('Cameroon'), ('Canada'), 
('Central African Republic'), ('Chad'), ('Chile'), ('China'), 
('Colombia'), ('Comoros'), ('Congo'), ('Czech Republic'), ('Denmark'), 
('Djibouti'), ('Dominica'), ('Dominican Republic'), ('Ecuador'), 
('Egypt'), ('El Salvador'), ('Equatorial Guinea'), ('Eritrea'), 
('Estonia'), ('Eswatini'), ('Ethiopia'), ('Fiji'), ('Finland'), 
('France'), ('Gabon'), ('Gambia'), ('Georgia'), ('Germany'), 
('Ghana'), ('Greece'), ('Grenada'), ('Guatemala'), ('Guinea'), 
('Guinea-Bissau'), ('Guyana'), ('Haiti'), ('Honduras'), ('Hungary'), 
('Iceland'), ('India'), ('Indonesia'), ('Iran'), ('Iraq'), 
('Ireland'), ('Palestine'), ('Italy'), ('Jamaica'), ('Japan'), 
('Jordan'), ('Kazakhstan'), ('Kenya'), ('Kiribati'), ('Korea (Democratic Peoples Republic)'), 
('Korea (Republic of)'), ('Kuwait'), ('Kyrgyzstan'), ('Lao People\'s Democratic Republic'), 
('Latvia'), ('Lebanon'), ('Lesotho'), ('Liberia'), ('Libya'), 
('Liechtenstein'), ('Lithuania'), ('Luxembourg'), ('Madagascar'), 
('Malawi'), ('Malaysia'), ('Maldives'), ('Mali'), ('Malta'), 
('Marshall Islands'), ('Mauritania'), ('Mauritius'), ('Mexico'), 
('Micronesia (Federated States of)'), ('Moldova (Republic of)'), ('Monaco'), 
('Mongolia'), ('Montenegro'), ('Morocco'), ('Mozambique'), ('Myanmar'), 
('Namibia'), ('Nauru'), ('Nepal'), ('Netherlands'), ('New Zealand'), 
('Nicaragua'), ('Niger'), ('Nigeria'), ('North Macedonia'), 
('Norway'), ('Oman'), ('Pakistan'), ('Palau'), ('Panama'), 
('Papua New Guinea'), ('Paraguay'), ('Peru'), ('Philippines'), 
('Poland'), ('Portugal'), ('Qatar'), ('Romania'), ('Russian Federation'), 
('Rwanda'), ('Saint Kitts and Nevis'), ('Saint Lucia'), ('Saint Vincent and the Grenadines'), 
('Samoa'), ('San Marino'), ('Sao Tome and Principe'), ('Saudi Arabia'), 
('Senegal'), ('Serbia'), ('Seychelles'), ('Sierra Leone'), ('Singapore'), 
('Slovakia'), ('Slovenia'), ('Solomon Islands'), ('Somalia'), ('South Africa'), 
('South Georgia and the South Sandwich Islands'), ('South Sudan'), 
('Spain'), ('Sri Lanka'), ('Sudan'), ('Suriname'), ('Sweden'), 
('Switzerland'), ('Syrian Arab Republic'), ('Taiwan'), ('Tajikistan'), 
('Tanzania (United Republic of)'), ('Thailand'), ('Timor-Leste'), 
('Togo'), ('Tokelau'), ('Tonga'), ('Trinidad and Tobago'), ('Tunisia'), 
('Turkey'), ('Turkmenistan'), ('Tuvalu'), ('Uganda'), ('Ukraine'), 
('United Arab Emirates'), ('United Kingdom'), ('United States of America'), 
('Uruguay'), ('Uzbekistan'), ('Vanuatu'), ('Venezuela (Bolivarian Republic of)'), 
('Viet Nam'), ('Western Sahara'), ('Yemen'), ('Zambia'), ('Zimbabwe');

-- Insert sample data into the 'industries' table
INSERT INTO industries (name) VALUES
('Technology/Software'),
('Healthcare'),
('Finance/Banking'),
('Manufacturing'),
('Retail/E-commerce'),
('Education'),
('Real Estate'),
('Construction'),
('Transportation/Logistics'),
('Hospitality/Travel'),
('Entertainment/Media'),
('Energy/Utilities'),
('Agriculture'),
('Telecommunications'),
('Government/Public Sector'),
('Non-Profit'),
('Consulting/Professional Services'),
('Pharmaceuticals'),
('Automotive'),
('Food & Beverage'),
('Insurance'),
('Legal Services'),
('Marketing/Advertising'),
('Fashion/Apparel'),
('Mining & Metals');

-- Insert sample data into the 'sizes' table
INSERT INTO sizes (name) VALUES
('Small'),
('Medium'),
('Large');
RENAME TABLE sizes TO company_sizes;


drop table users;
-- Step 1: Create the users table without the company_id foreign key
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Finance Manager', 'Other') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 2: Create the companies table without the admin_id foreign key
CREATE TABLE companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    industry_id INT,
    country_id INT,
    address VARCHAR(255) NOT NULL,
    company_size_id INT,
    admin_id INT NULL,
    FOREIGN KEY (industry_id) REFERENCES industries(id),
    FOREIGN KEY (country_id) REFERENCES countries(id),
    FOREIGN KEY (company_size_id) REFERENCES company_sizes(id)
);

-- Step 3: Add the company_id foreign key to users (referencing companies)
ALTER TABLE users
ADD COLUMN company_id INT,
ADD CONSTRAINT fk_company_id FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;

-- Step 4: Add the admin_id foreign key to companies (referencing users)
ALTER TABLE companies
ADD CONSTRAINT fk_admin_id FOREIGN KEY (admin_id) REFERENCES users(user_id) ON DELETE SET NULL;
SELECT name FROM industries;
