#lang racket/base

(require net/url
         html-parsing
         sxml
         racket/date
         threading)

(define (scrape category)
  (define html
    (~>>
     (format "https://news.cts.com.tw/~a/index.html" category)
     (string->url)
     (get-pure-port)
     (html->xexp)))
  (define article-nodes
    ((sxpath
      '(// (div (@ (equal? (class "newslist-container flexbox")))) a))
     html))
  (for/list ((n article-nodes))
    (sxml:attr n 'href)))

(define categories
  '("politics" "international" "society" "life" "money"))

(for ((name categories))
  (define d (current-date))
  (define timestamp (format "~a-~a-~a" (date-year d) (date-month d) (date-day d)))
  (define filename (format "urls/cts-~a-urls-~a.txt" name timestamp))
  (printf "Parsing urls in category ~a...\n" name)
  (with-output-to-file filename
    (lambda ()
      (for ((l (scrape name)))
        (write-string l)
        (newline)))))
