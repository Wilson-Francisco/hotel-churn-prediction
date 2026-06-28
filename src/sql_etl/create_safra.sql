--DROP TABLE IF EXISTS tb_books_user;

WITH target_safra AS (
    
    SELECT 
        t1.user_id,
        '{date}' AS ref_date,
    
        CASE 
            -- SE NÃO EXISTIR nenhuma linha na tabela reviews para este user em 2024 -> Churn (1)
            WHEN NOT EXISTS (
                SELECT 1 
                FROM reviews AS t2 
                WHERE t2.user_id = t1.user_id 
                    AND t2.review_date > '{date}'
                    AND t2.review_date <= date('{date}', '+ 365 days')
            ) THEN 1
            -- SE EXISTIR pelo menos uma linha -> Ativo (0)
        ELSE 0
        END AS target_churn
    FROM users AS t1
    
    )

SELECT 
    t1.*,
    t2.target_churn

FROM tb_books_user AS t1
LEFT JOIN target_safra AS t2 ON t1.user_id = t2.user_id



