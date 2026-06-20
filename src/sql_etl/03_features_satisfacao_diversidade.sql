SELECT 
    t1.user_id,
     -- Médias de satisfação do utilizador
    AVG(t1.score_overall) AS sat_media_score_overall,
    AVG(t1.score_cleanliness) AS sat_media_score_limpeza,
    AVG(t1.score_comfort) AS sat_media_score_conforto,
    AVG(t1.score_facilities) AS sat_media_score_comodidades,

    -- Diversidade de consumo
    COUNT(DISTINCT t1.hotel_id) AS div_hoteis_diferentes,
    COUNT(DISTINCT t2.city) AS div_cidades_diferentes,
    AVG(t2.star_rating) AS div_media_estrelas_hoteis,

    -- Tempo de hospedagem do utilizador no hotel até à data da safra
    (julianday('2023-12-31') - julianday(MIN(t1.review_date))) AS temp_dias_desde_primeira_review


FROM reviews as t1
JOIN hotels AS t2 ON t1.hotel_id = t2.hotel_id
WHERE t1.review_date <= '2023-12-31'
GROUP BY t1.user_id
LIMIT 10;