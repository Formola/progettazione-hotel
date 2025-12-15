# --- CLOUDFRONT (CDN) ---

# Distribuzione CloudFront
# Questa risorsa crea la CDN che si posiziona davanti al bucket S3.
resource "aws_cloudfront_distribution" "s3_distribution" {
  
  origin {
    # Usiamo il dominio regionale del bucket (non l'endpoint del sito web)
    # Questo è un indirizzo che LocalStack e AWS risolvono correttamente sempre.
    domain_name = aws_s3_bucket.frontend_bucket.bucket_regional_domain_name
    origin_id   = "S3-Frontend-Origin"

    # Usiamo s3_origin_config invece di custom_origin_config
    s3_origin_config {
      origin_access_identity = "" # In LocalStack/Public bucket possiamo lasciarlo vuoto o ometterlo
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-Frontend-Origin"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  # GESTIONE SPA (Single Page App) ---
  # Se riceve un 404 (file non trovato), servi index.html con status 200".
  
  custom_error_response {
    error_code            = 403 # S3 spesso ritorna 403 invece di 404 per file mancanti
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

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
La risorsa principale è aws_cloudfront_distribution, che definisce l'intera configurazione della CDN.

1. ORIGIN (S3 REST API):
non usiamo l'endpoint "Website Hosting" di S3, 
ma trattiamo S3 come un semplice storage di oggetti (`s3_origin_config`). 
Questo approccio è più sicuro e standard per le Single Page Application (SPA), poiché permette 
a CloudFront di autenticarsi direttamente col bucket (in produzione tramite OAI/OAC) senza dover 
rendere il bucket pubblicamente accessibile via HTTP.

2. GESTIONE SPA (Single Page Application):
Poiché non usiamo più la "Website Configuration" di S3 per i redirect, abbiamo introdotto i blocchi
`custom_error_response`. Quando un utente visita un percorso lato client (es. /dashboard), 
S3 non troverà quel file fisico e restituirà un errore 403 o 404. CloudFront intercetta 
questi errori e restituisce invece il file `index.html` con uno status 200 OK. 
Questo permette al router Javascript (SvelteKit/React/Vue) di caricarsi e mostrare la pagina corretta.

3. CACHE E PERFORMANCE:
Il blocco default_cache_behavior decide come servire i contenuti.
- viewer_protocol_policy = "redirect-to-https": Forza sempre la connessione sicura.
- forwarded_values (cookies/query_string = none): Massimizza la cache dicendo alla CDN che 
  il contenuto statico non cambia in base ai cookie dell'utente.

4. SSL:
Il blocco viewer_certificate usa il certificato di default (*.cloudfront.net) per semplicità.
In produzione, qui verrebbe collegato un certificato ACM per il dominio personalizzato.
*/