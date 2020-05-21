CREATE DATABASE `deepform`;

USE `deepform`;

CREATE TABLE `document` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `dc_slug` varchar(256) DEFAULT NULL,
  `filing_type` varchar(256) DEFAULT NULL,
  `contract_number` int(11) DEFAULT NULL,
  `url` varchar(256) DEFAULT NULL,
  `committee` varchar(256) DEFAULT NULL,
  `agency` varchar(256) DEFAULT NULL,
  `callsign` varchar(10) DEFAULT NULL,
  `thumbnail_url` varchar(256) DEFAULT NULL,
  `market_id` int(11) DEFAULT NULL,
  `upload_date` datetime DEFAULT NULL,
  `gross_amount_usd` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_dc_slug` (`dc_slug`)
) ENGINE=InnoDB AUTO_INCREMENT=68175 DEFAULT CHARSET=latin1;

CREATE TABLE `token` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `dc_slug` varchar(256) DEFAULT NULL,
  `page` float DEFAULT NULL,
  `x0` double DEFAULT NULL,
  `y0` double DEFAULT NULL,
  `x1` double DEFAULT NULL,
  `y1` double DEFAULT NULL,
  `token` varchar(256) DEFAULT NULL,
  `gross_amount` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `origin_document` (`dc_slug`)
) ENGINE=InnoDB AUTO_INCREMENT=14024491 DEFAULT CHARSET=latin1;
