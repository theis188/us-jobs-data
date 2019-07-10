


SELECT o.name,v.year,v.value FROM value v
join series_code sc 
on v.series_code = sc.code
join occupation_code o
on o.code = sc.occupation_code
where sc.area_code='M0048140'
and sc.industry_code='000000'
and sc.occupation_code like '__0000'
order by 1 asc, 2 asc;


SELECT o.name,v.year,v.value FROM value v
join series_code sc 
on v.series_code = sc.code
join occupation_code o
on o.code = sc.occupation_code
where sc.area_code='M0048140'
and sc.industry_code='000000'
and sc.occupation_code like '__0000'
order by 1 asc, 2 asc;
