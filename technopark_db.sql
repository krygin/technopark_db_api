SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `technopark_db` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `technopark_db` ;

-- -----------------------------------------------------
-- Table `technopark_db`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `technopark_db`.`users` ;

CREATE TABLE IF NOT EXISTS `technopark_db`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(32) NULL,
  `email` VARCHAR(32) NOT NULL,
  `name` VARCHAR(32) NULL,
  `about` VARCHAR(256) NULL,
  `isAnonymous` TINYINT(1) NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC));


-- -----------------------------------------------------
-- Table `technopark_db`.`forums`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `technopark_db`.`forums` ;

CREATE TABLE IF NOT EXISTS `technopark_db`.`forums` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(128) NULL,
  `short_name` VARCHAR(128) NOT NULL,
  `user_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_Forums_Users1_idx` (`user_id` ASC),
  UNIQUE INDEX `short_name_UNIQUE` (`short_name` ASC),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  CONSTRAINT `fk_Forums_Users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `technopark_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `technopark_db`.`threads`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `technopark_db`.`threads` ;

CREATE TABLE IF NOT EXISTS `technopark_db`.`threads` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(128) NOT NULL,
  `date` DATETIME NULL,
  `message` TEXT NULL,
  `slug` VARCHAR(128) NULL,
  `isClosed` TINYINT(1) NULL DEFAULT false,
  `isDeleted` TINYINT(1) NULL DEFAULT 0,
  `user_id` INT NOT NULL,
  `forum_id` INT NOT NULL,
  `likes` INT NOT NULL DEFAULT 0,
  `dislikes` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`, `forum_id`),
  INDEX `fk_Thread_Users_idx` (`user_id` ASC),
  INDEX `fk_Thread_Forums1_idx` (`forum_id` ASC),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  CONSTRAINT `fk_Thread_Users`
    FOREIGN KEY (`user_id`)
    REFERENCES `technopark_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Thread_Forums1`
    FOREIGN KEY (`forum_id`)
    REFERENCES `technopark_db`.`forums` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `technopark_db`.`posts`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `technopark_db`.`posts` ;

CREATE TABLE IF NOT EXISTS `technopark_db`.`posts` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `date` DATETIME NOT NULL,
  `message` TEXT NULL,
  `isApproved` TINYINT(1) NOT NULL DEFAULT 0,
  `isHighlighted` TINYINT(1) NOT NULL DEFAULT 0,
  `isEdited` TINYINT(1) NOT NULL DEFAULT 0,
  `isSpam` TINYINT(1) NOT NULL DEFAULT 0,
  `isDeleted` TINYINT(1) NOT NULL DEFAULT 0,
  `post_id` INT NULL DEFAULT NULL,
  `user_id` INT NOT NULL,
  `thread_id` INT NOT NULL,
  `dislikes` INT NOT NULL DEFAULT 0,
  `likes` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`, `thread_id`),
  INDEX `fk_Post_Post1_idx` (`post_id` ASC),
  INDEX `fk_Post_Users1_idx` (`user_id` ASC),
  INDEX `fk_Post_Thread1_idx` (`thread_id` ASC),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  CONSTRAINT `fk_Post_Post1`
    FOREIGN KEY (`post_id`)
    REFERENCES `technopark_db`.`posts` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Post_Users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `technopark_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Post_Thread1`
    FOREIGN KEY (`thread_id`)
    REFERENCES `technopark_db`.`threads` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `technopark_db`.`followers`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `technopark_db`.`followers` ;

CREATE TABLE IF NOT EXISTS `technopark_db`.`followers` (
  `follower_id` INT NOT NULL,
  `followee_id` INT NOT NULL,
  `follows` TINYINT(1) NOT NULL DEFAULT false,
  INDEX `fk_Users_has_Users_Users2_idx` (`followee_id` ASC),
  PRIMARY KEY (`followee_id`, `follower_id`),
  CONSTRAINT `fk_Users_has_Users_Users1`
    FOREIGN KEY (`follower_id`)
    REFERENCES `technopark_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Users_has_Users_Users2`
    FOREIGN KEY (`followee_id`)
    REFERENCES `technopark_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);


-- -----------------------------------------------------
-- Table `technopark_db`.`subscribers`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `technopark_db`.`subscribers` ;

CREATE TABLE IF NOT EXISTS `technopark_db`.`subscribers` (
  `subscribed` TINYINT(1) NOT NULL DEFAULT false,
  `user_id` INT NOT NULL,
  `thread_id` INT NOT NULL,
  INDEX `fk_Subscriptions_Users1_idx` (`user_id` ASC),
  INDEX `fk_Subscriptions_Threads1_idx` (`thread_id` ASC),
  PRIMARY KEY (`user_id`, `thread_id`),
  CONSTRAINT `fk_Subscriptions_Users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `technopark_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Subscriptions_Threads1`
    FOREIGN KEY (`thread_id`)
    REFERENCES `technopark_db`.`threads` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
