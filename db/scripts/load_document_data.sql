LOAD DATA LOCAL INFILE '../source/ftf-all-filings.tsv'
  INTO TABLE document
  COLUMNS TERMINATED BY '\t'
  IGNORE 1 LINES
  (id, filing_type, contract_number, url, committee, agency, callsign, dc_slug, thumbnail_url, gross_amount_usd, market_id, upload_date);
