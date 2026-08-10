-- ================================================================
-- AI-Based Package Delivery Time Prediction System
-- MySQL Schema
-- ================================================================

CREATE DATABASE IF NOT EXISTS delivery_db;
USE delivery_db;

-- ----------------------------------------------------------------
-- delivery_records: Historical & incoming delivery data
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS delivery_records (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    tracking_id         VARCHAR(20)  UNIQUE NOT NULL,
    origin_city         VARCHAR(100) NOT NULL,
    destination_city    VARCHAR(100) NOT NULL,
    origin_lat          DECIMAL(9,6),
    origin_lng          DECIMAL(9,6),
    destination_lat     DECIMAL(9,6),
    destination_lng     DECIMAL(9,6),
    distance_km         FLOAT        NOT NULL,
    base_duration_min   FLOAT        NOT NULL COMMENT 'Without traffic',
    traffic_duration_min FLOAT       NOT NULL COMMENT 'With traffic',
    traffic_level       ENUM('LOW','MODERATE','HIGH','SEVERE') NOT NULL,
    weather_condition   ENUM('CLEAR','CLOUDY','RAIN','HEAVY_RAIN','SNOW','FOG','STORM') NOT NULL,
    temperature_celsius FLOAT,
    wind_speed_kmh      FLOAT,
    precipitation_mm    FLOAT        DEFAULT 0,
    package_weight_kg   FLOAT        NOT NULL,
    package_type        ENUM('SMALL','MEDIUM','LARGE','FRAGILE','PERISHABLE') NOT NULL,
    priority            ENUM('STANDARD','EXPRESS','OVERNIGHT') NOT NULL,
    predicted_time_hours FLOAT,
    actual_time_hours   FLOAT,
    model_used          VARCHAR(30),
    prediction_error    FLOAT GENERATED ALWAYS AS (
                            ABS(predicted_time_hours - actual_time_hours)
                        ) STORED,
    created_at          DATETIME     DEFAULT CURRENT_TIMESTAMP,
    delivered_at        DATETIME,
    INDEX idx_origin    (origin_city),
    INDEX idx_dest      (destination_city),
    INDEX idx_created   (created_at),
    INDEX idx_traffic   (traffic_level),
    INDEX idx_weather   (weather_condition)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------
-- prediction_logs: Every real-time prediction request
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS prediction_logs (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    request_id          VARCHAR(36)  NOT NULL COMMENT 'UUID',
    origin              VARCHAR(255) NOT NULL,
    destination         VARCHAR(255) NOT NULL,
    distance_km         FLOAT,
    traffic_duration_min FLOAT,
    traffic_level       VARCHAR(20),
    weather_condition   VARCHAR(30),
    temperature_celsius FLOAT,
    wind_speed_kmh      FLOAT,
    precipitation_mm    FLOAT,
    package_weight_kg   FLOAT,
    package_type        VARCHAR(20),
    priority            VARCHAR(20),
    predicted_xgboost   FLOAT,
    predicted_rf        FLOAT,
    predicted_lr        FLOAT,
    recommended_model   VARCHAR(30),
    recommended_hours   FLOAT,
    api_response_ms     INT,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_request   (request_id),
    INDEX idx_created   (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------
-- model_metrics: Saved evaluation metrics per training run
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS model_metrics (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    model_name  VARCHAR(30)  NOT NULL,
    rmse        FLOAT        NOT NULL,
    mae         FLOAT        NOT NULL,
    r2          FLOAT        NOT NULL,
    trained_on  INT          NOT NULL COMMENT 'Number of training samples',
    trained_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_current  TINYINT(1) DEFAULT 1,
    INDEX idx_model (model_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
