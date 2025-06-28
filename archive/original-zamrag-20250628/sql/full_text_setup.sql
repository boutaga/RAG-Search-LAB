-- Enable full-text search on the articles table
ALTER TABLE public.articles ADD COLUMN IF NOT EXISTS content_tsv tsvector;
UPDATE public.articles SET content_tsv = to_tsvector('english', content);
CREATE INDEX IF NOT EXISTS idx_articles_content_tsv ON public.articles USING GIN (content_tsv);
