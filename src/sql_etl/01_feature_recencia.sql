SELECT

    t1.user_id,
    (julianday('2023-12-31') - julianday(MAX(t1.review_date))) AS ultima_review

FROM reviews as t1

WHERE t1.review_date <= '2023-12-31'
GROUP BY t1.user_id
LIMIT 10;