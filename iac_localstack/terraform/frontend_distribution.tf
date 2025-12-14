# --- CLOUDFRONT (CDN) ---

# Distribuzione CloudFront
# Questa risorsa crea la CDN che si posiziona davanti al bucket S3.
resource "aws_cloudfront_distribution" "s3_distribution" {
  
  # ORIGINE: Da dove prende i file?
  # Puntiamo all'endpoint del sito web configurato nel file storage.tf.
  # Usiamo una configurazione "Custom Origin" perché stiamo puntando all'endpoint
  # del sito statico (che gestisce i redirect) e non al bucket grezzo.
  origin {
    domain_name = aws_s3_bucket_website_configuration.frontend_config.website_endpoint
    origin_id   = "S3-Frontend-Origin"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only" # L'endpoint S3 Website è in HTTP
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html" # Il file che viene servito se chiami la root /

  # COMPORTAMENTO DELLA CACHE (Default Behavior)
  # Come deve comportarsi CloudFront con le richieste standard?
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-Frontend-Origin"

    # Forwarding dei valori: per un sito statico non inoltriamo cookie o query string
    # complessi per massimizzare la cache.
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https" # Forza sempre HTTPS per sicurezza
    min_ttl                = 0
    default_ttl            = 3600  # Cache di 1 ora
    max_ttl                = 86400 # Cache massima di 1 giorno
  }

  # RESTRIZIONI GEOGRAFICHE
  # Possiamo bloccare o permettere paesi specifici. Qui apriamo a tutti.
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # CERTIFICATO SSL
  # Usiamo il certificato di default di CloudFront (*.cloudfront.net).
  # In produzione si usa un certificato ACM col tuo dominio reale.
  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name = "Frontend CDN Distribution"
  }
}

# --- OUTPUTS ---

output "cloudfront_domain_name" {
  description = "L'URL pubblico della tua applicazione (es. d1234.cloudfront.net)"
  value       = aws_cloudfront_distribution.s3_distribution.domain_name
}

output "cloudfront_id" {
  description = "L'ID della distribuzione (utile per invalidare la cache dopo un deploy)"
  value       = aws_cloudfront_distribution.s3_distribution.id
}


/*
Questo file configura l'ultimo miglio della consegna dei contenuti verso l'utente finale.
La risorsa principale è aws_cloudfront_distribution,che definisce l'intera configurazione della CDN.

Il blocco origin è il punto di collegamento con lo storage. Qui specifichiamo il domain_name recuperandolo
direttamente dalla risorsa aws_s3_bucket_website_configuration che abbiamo creato nel file storage.tf.
È importante notare che stiamo trattando l'origine come un custom_origin_config con protocollo http-only.
Questo perché l'endpoint "Website Hosting" di S3 non supporta HTTPS nativamente; CloudFront si occuperà di
crittografare la connessione con l'utente (HTTPS), ma parlerà con S3 in HTTP "dietro le quinte".
Questa configurazione preserva le regole di routing (come i redirect per le Single Page Application) gestite da S3.

Il blocco default_cache_behavior è colui che decide come servire i contenuti. Abbiamo impostato
viewer_protocol_policy = "redirect-to-https", che è una best practice di sicurezza fondamentale:
se un utente digita http://mia-app.com, verrà immediatamente reindirizzato alla versione sicura https.
Le impostazioni di TTL (Time To Live) definiscono per quanto tempo i file rimangono nei server di CloudFront
prima di essere riscaricati da S3. Impostando forwarded_values su none per query string e cookie,
ottimizziamo drasticamente le prestazioni, dicendo alla CDN che la pagina index.html è identica per
tutti gli utenti, permettendole di servirla istantaneamente dalla cache.

Infine, il blocco viewer_certificate è impostato su true per il certificato di default.
Questo significa che la tua applicazione sarà accessibile tramite un dominio generato da
AWS (qualcosa come d111111abcdef8.cloudfront.net). In uno scenario di produzione reale, qui
collegheremmo un certificato ACM (AWS Certificate Manager) per usare il dominio personalizzato
(es. www.mia-app.com).
*/