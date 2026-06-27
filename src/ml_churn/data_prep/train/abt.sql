DROP TABLE IF EXISTS tb_abt_churn;
CREATE TABLE tb_abt_churn AS  

WITH tb_reviews_user AS (

    SELECT
        t1.review_id, 
        t1.review_date, 
        t1.user_id,
        t1.review_text, 
        1 AS ativo
    
    FROM reviews as t1
    GROUP BY t1.review_id, t1.user_id
 ) 

 SELECT   
    t1.*,
    t2.review_text,
    CASE 
            -- Se o ID da subquery veio VAZIO (NULL), o cliente NÃO viajou em 2021 -> Churn (1)
        WHEN t2.user_id IS NULL THEN 1 
            -- Se o ID veio preenchido, o cliente viajou em 2021 -> Ativo (0)
        ELSE 0 
    END AS target_churn
    

FROM tb_books_user AS t1

LEFT JOIN tb_reviews_user AS t2 ON t1.user_id = t2.user_id
AND t2.review_date BETWEEN t1.ref_date AND date(t1.ref_date, '+365 days')

WHERE t1.ref_date < '2026-12-31'
GROUP BY t1.review_id, t1.user_id
ORDER BY t1.ref_date ;