ALTER TABLE token DISABLE KEYS;
BEGIN;
LOAD DATA LOCAL INFILE '../data/training.csv'
  INTO TABLE token
  COLUMNS TERMINATED BY ','
  IGNORE 1 LINES
  (dc_slug,page,x0,y0,x1,y1,token,gross_amount);
COMMIT;
ALTER TABLE token ENABLE KEYS;
