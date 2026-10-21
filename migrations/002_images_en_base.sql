-- Les photos importees sont conservees en base et plus seulement sur le
-- disque de l'instance : sur une instance cloud, le disque local est
-- efface a chaque redemarrage.

ALTER TABLE property_images ADD COLUMN IF NOT EXISTS image_data BYTEA;
ALTER TABLE property_images ADD COLUMN IF NOT EXISTS mime_type VARCHAR(80);
ALTER TABLE property_images ADD COLUMN IF NOT EXISTS file_name VARCHAR(255);
