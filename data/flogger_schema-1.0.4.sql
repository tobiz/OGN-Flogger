-- SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
-- SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
-- SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
-- USE `mydb` ; 
 
--
-- 20150825 Corrected schema for AUTOINCREMENT primary keys
-- 20150826 Corrected flights table: set aircraft_id, users_id, launch_type,launch_types_idlaunch_types to INT NULL DEFAULT NULL
-- 20150908 Added fields for concatenating tracks for a flight when processing a group
-- 

-- -----------------------------------------------------
-- Table `mydb`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `users` ;      
 
CREATE TABLE IF NOT EXISTS users (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `first_name` TEXT NULL DEFAULT NULL,
  `surname` TEXT NULL DEFAULT NULL,
  `phone` TEXT NULL DEFAULT NULL,
  `email` TEXT NULL DEFAULT NULL,
  `password` TEXT NULL DEFAULT NULL);


-- -----------------------------------------------------
-- Table `mydb`.`aircraft`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `aircraft` ;

CREATE TABLE IF NOT EXISTS `aircraft` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `registration` TEXT NULL DEFAULT NULL,
  `type` TEXT NULL DEFAULT NULL,
  `model` TEXT NULL DEFAULT NULL,
  `owner` TEXT NULL DEFAULT NULL,
  `airfield` TEXT NULL DEFAULT NULL,
  `flarm_id` TEXT NULL DEFAULT NULL);

-- -----------------------------------------------------
-- Table `mydb`.`flight_log`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `flight_log` ;

CREATE TABLE IF NOT EXISTS `flight_log` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `sdate` TEXT NULL DEFAULT NULL,
  `stime` TEXT NULL DEFAULT NULL,
  `edate` TEXT NULL DEFAULT NULL,
  `etime` TEXT NULL DEFAULT NULL,
  `duration` TEXT NULL DEFAULT NULL,
  `src_callsign` TEXT NULL DEFAULT NULL,
  `max_altitude` TEXT NULL DEFAULT NULL,
  `speed` TEXT NULL DEFAULT NULL,
  'registration' TEXT NULL DEFAULT NULL,
  'flight_no' INTEGER NULL DEFAULT NULL); 
  
-- -----------------------------------------------------
-- Table `mydb`.`flight_log2`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `flight_log2` ;

CREATE TABLE IF NOT EXISTS `flight_log2` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `sdate` TEXT NULL DEFAULT NULL, 
  `stime` TEXT NULL DEFAULT NULL,
  `edate` TEXT NULL DEFAULT NULL,
  `etime` TEXT NULL DEFAULT NULL,
  `duration` TEXT NULL DEFAULT NULL,
  `src_callsign` TEXT NULL DEFAULT NULL,
  `max_altitude` TEXT NULL DEFAULT NULL,
  `speed` TEXT NULL DEFAULT NULL,
  'registration' TEXT NULL DEFAULT NULL);


-- -----------------------------------------------------
-- Table `mydb`.`flight_group`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `flight_group` ;

CREATE TABLE IF NOT EXISTS `flight_group` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `groupID` TEXT NULL DEFAULT NULL,
  `sdate` TEXT NULL DEFAULT NULL,
  `stime` TEXT NULL DEFAULT NULL,
  `edate` TEXT NULL DEFAULT NULL,
  `etime` TEXT NULL DEFAULT NULL,
  `duration` TEXT NULL DEFAULT NULL,
  `src_callsign` TEXT NULL DEFAULT NULL,
  `max_altitude` TEXT NULL DEFAULT NULL,
  'registration' TEXT NULL DEFAULT NULL,
  'flight_no' INTEGER NULL DEFAULT NULL);


-- -----------------------------------------------------
-- Table `mydb`.`launch_types`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `launch_types` ; 

CREATE TABLE IF NOT EXISTS `launch_types` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `aero_tow` VARCHAR(45) NULL,
  `winch` VARCHAR(45) NULL,
  `self_launch` VARCHAR(45) NULL);
--ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`flights` 
-- 20160907 	Added tug registration and max altitude if
-- 				flight launched by tug 
-- -----------------------------------------------------
DROP TABLE IF EXISTS `flights` ;

CREATE TABLE IF NOT EXISTS `flights` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `sdate` TEXT NULL DEFAULT NULL,
  `stime` TEXT NULL DEFAULT NULL,
  `edate` TEXT NULL DEFAULT NULL,
  `etime` TEXT NULL DEFAULT NULL,
  `duration` TEXT NULL DEFAULT NULL,
  `src_callsign` TEXT NULL DEFAULT NULL,
  `max_altitude` TEXT NULL DEFAULT NULL,
  'registration' TEXT NULL DEFAULT NULL,
--  `aircraft_id` INT NOT NULL,
--  `users_id` INT NOT NULL,
--  `launch_type` INT NOT NULL,
--  `launch_types_idlaunch_types` INT NOT NULL
  `aircraft_id` INT NULL DEFAULT NULL,
  `users_id` INT NULL DEFAULT NULL,
  `launch_type` INT NULL DEFAULT NULL,
  `launch_types_idlaunch_types` INT NULL DEFAULT NULL,
  'flight_no' INTEGER NULL DEFAULT NULL,
  'track_file_name' TEXT NULL DEFAULT NULL,
  'tug_registration' TEXT NULL DEFAULT NULL,
  'tug_altitude' TEXT NULL DEFAULT NULL,
  'tug_model' TEXT NULL DEFAULT NULL);
		

-- -----------------------------------------------------
-- Table `mydb`.`flight_log_final`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `flight_log_final` ;

CREATE TABLE IF NOT EXISTS `flight_log_final` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `sdate` TEXT NULL DEFAULT NULL,
  `stime` TEXT NULL DEFAULT NULL,
  `edate` TEXT NULL DEFAULT NULL,
  `etime` TEXT NULL DEFAULT NULL,
  `duration` TEXT NULL DEFAULT NULL,
  `src_callsign` TEXT NULL DEFAULT NULL,
  `max_altitude` TEXT NULL DEFAULT NULL,
  `speed` TEXT NULL DEFAULT NULL,
  `registration` TEXT NULL DEFAULT NULL,
  'flight_no' INTEGER NULL DEFAULT NULL,
  'land_out' TEXT NULL DEFAULT NULL);
  
-- -----------------------------------------------------
-- Table `mydb`.`track`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `track` ;

CREATE TABLE IF NOT EXISTS `track` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `flight_no` INT NULL DEFAULT NULL,
  `track_no` INT NULL DEFAULT NULL,
  `latitude` DECIMAL NULL DEFAULT NULL,
  `longitude` DECIMAL NULL DEFAULT NULL,
  `altitude` DECIMAL NULL DEFAULT NULL,
  `course` DECIMAL NULL DEFAULT NULL,
  `speed` DECIMAL NULL DEFAULT NULL,
  `timeStamp` TIMESTAMP NULL DEFAULT NULL);
  
-- -----------------------------------------------------
-- Table `mydb`.`trackFinal`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `trackFinal` ;

CREATE TABLE IF NOT EXISTS `trackFinal` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `flight_no` INT NULL DEFAULT NULL,
  `track_no` INT NULL DEFAULT NULL,
  `latitude` DECIMAL NULL DEFAULT NULL,
  `longitude` DECIMAL NULL DEFAULT NULL,
  `altitude` DECIMAL NULL DEFAULT NULL,
  `course` DECIMAL NULL DEFAULT NULL,
  `speed` DECIMAL NULL DEFAULT NULL,
  `timeStamp` TIMESTAMP NULL DEFAULT NULL);
  
-- -----------------------------------------------------
-- Table `mydb`.`flarm_db` 
-- -----------------------------------------------------
DROP TABLE IF EXISTS `flarm_db` ;
  
CREATE TABLE IF NOT EXISTS `flarm_db`(
 	`id` INTEGER PRIMARY KEY AUTOINCREMENT, 
 	`type` TEXT NULL DEFAULT NULL,
 	`flarm_id` TEXT NULL DEFAULT NULL, 
 	`airport` STRING NULL DEFAULT NULL, 
 	`aircraft_model` TEXT NULL DEFAULT NULL, 
 	`registration` TEXT NULL DEFAULT NULL, 
 	`radio` TEXT NULL DEFAULT NULL,
 	`aircraft_type` TEXT NULL DEFAULT NULL); 
 	
CREATE UNIQUE INDEX `flarm_db_idx` ON `flarm_db`(`id`, `flarm_id`);

  




