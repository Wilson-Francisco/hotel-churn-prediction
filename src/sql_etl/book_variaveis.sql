
WITH tb_variaveis AS (

    SELECT
        '{date}' AS ref_date,
        t1.review_date,
        t1.user_id,
        t2.hotel_name,
        t2.city,
        t2.country,

        -- Dias entre a data da safra e a última review do utilizador
        (julianday('{date}') - julianday(MAX(t1.review_date))) AS ultima_review,

        -- Visão para isolar a volumetria e frequência do utilizador
        COUNT(t1.review_id) as freq_total_reviews,
        SUM(CASE WHEN t1.review_date >= date('{date}', '-90 days') THEN 1 ELSE 0 END) AS freq_reviews_ultimos_90_dias,
        SUM(CASE WHEN t1.review_date >= date('{date}', '-180 days') THEN 1 ELSE 0 END) AS freq_reviews_ultimos_180_dias,
        SUM(CASE WHEN t1.review_date >= date('{date}', '-365 days') THEN 1 ELSE 0 END) AS freq_reviews_ultimos_365_dias,

        -- Médias de satisfação do utilizador
        AVG(t1.score_overall) AS sat_media_score_overall,
        AVG(t1.score_cleanliness) AS sat_media_score_limpeza,
        AVG(t1.score_comfort) AS sat_media_score_conforto,
        AVG(t1.score_facilities) AS sat_media_score_comodidades,

        -- Diversidade de consumo
        COUNT(DISTINCT t1.hotel_id) AS div_hoteis_diferentes,
        COUNT(DISTINCT t2.city) AS div_cidades_diferentes,
        AVG(t2.star_rating) AS div_media_estrelas_hoteis,
        AVG(t2.value_for_money_base) AS media_custo_beneficio,

        -- Tempo de hospedagem do utilizador no hotel até à data da safra
        (julianday('{date}') - julianday(MIN(t1.review_date))) AS temp_dias_desde_primeira_review


    FROM reviews as t1
    JOIN hotels AS t2 ON t1.hotel_id = t2.hotel_id
    WHERE t1.review_date BETWEEN date('{date}', '-365 days') AND '{date}'
    GROUP BY t1.user_id
)
    
SELECT

    t2.*,
    t1.user_gender,
    t1.age_group,
    t1.traveller_type

FROM users AS t1
LEFT JOIN tb_variaveis AS t2 ON t1.user_id = t2.user_id
WHERE t2.review_date BETWEEN date('{date}', '-365 days') AND '{date}'
GROUP BY t1.user_id

