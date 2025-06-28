-- Example search comparing keyword, full-text and vector similarity
-- Replace the sample phrase as desired

-- A) Keyword search
SELECT id, title
FROM public.articles
WHERE content ILIKE '%biggest animal in the ocean%';

-- B) Full-text search
SELECT id, title,
       ts_rank_cd(content_tsv, plainto_tsquery('english', 'biggest animal in the ocean')) AS rank
FROM public.articles
WHERE content_tsv @@ plainto_tsquery('english', 'biggest animal in the ocean')
ORDER BY rank DESC
LIMIT 5;

-- C) Vector similarity search
SELECT id, title, content_vector <-> (
    SELECT content_vector FROM public.articles WHERE title ILIKE '%Blue Whale%' LIMIT 1
) AS distance
FROM public.articles
WHERE content_vector IS NOT NULL
ORDER BY content_vector <-> (
    SELECT content_vector FROM public.articles WHERE title ILIKE '%Blue Whale%' LIMIT 1
)
LIMIT 5;
