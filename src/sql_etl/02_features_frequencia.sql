SELECT
    t1.user_id,
    -- Visão para isolar a volumetria e frequência do utilizador
    COUNT(t1.review_id) as freq_total_reviews,
    SUM(CASE WHEN t1.review_date >= date('2023-12-31', '-90 days') THEN 1 ELSE 0 END) AS freq_reviews_ultimos_90_dias,
    SUM(CASE WHEN t1.review_date >= date('2023-12-31', '-180 days') THEN 1 ELSE 0 END) AS freq_reviews_ultimos_180_dias,
    SUM(CASE WHEN t1.review_date >= date('2023-12-31', '-365 days') THEN 1 ELSE 0 END) AS freq_reviews_ultimos_365_dias


FROM reviews AS t1
WHERE t1.review_date <= '2023-12-31'
GROUP BY t1.user_id
LIMIT 10;