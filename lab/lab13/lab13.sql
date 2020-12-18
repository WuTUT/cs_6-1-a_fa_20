.read data.sql


CREATE TABLE average_prices AS
  SELECT category,sum(MSRP)/count(*)  as average_price FROM products GROUP BY category ;


CREATE TABLE lowest_prices AS
  SELECT  store,name,min(price) FROM inventory,products WHERE name = item GROUP BY name ;


CREATE TABLE shopping_list AS
  SELECT a.name,store FROM products as a,lowest_prices as b WHERE a.name = b.name GROUP BY a.category HAVING min(a.MSRP/a.rating) ;


CREATE TABLE total_bandwidth AS
  SELECT sum(b.Mbs) FROM shopping_list as a,stores as b WHERE a.store = b.store ;

