#lang racket/base

(require net/url
         html-parsing
         sxml
         racket/string
         racket/list
         racket/match
         gregor
         threading)

(define (scrape category page acc)
  (printf "Parsing page ~a...\r" page)
  (define html
    (~>> "https://www.ftvnews.com.tw/tag/~a/~a"
         (format _ category page)
         (string->url)
         (get-pure-port)
         (html->xexp)))
  (define article-nodes
    ((sxpath '(// (ul (@ (equal? (class "row")))))) html))
  (define (valid-date? node)
    (in-last-month?
     (sxml:text
      ((sxpath '(// (div (@ (equal? (class "time")))))) node))))
  (define links
    (for/list ((n ((sxpath '(// li a)) article-nodes))
               #:when (valid-date? n))
      (string-append "https://www.ftvnews.com.tw"
                     (sxml:attr n 'href))))
  (define new-acc (append acc links))
  (if (null? links)
      new-acc
      (scrape category (add1 page) new-acc)))

(define (in-last-month? timestr)
  (define day (first (string-split timestr)))
  (match-define (list y m d)
    (map string->number (string-split day "/")))
  (define article-date (date y m d))
  (define 1month-ago (-months (today) 1))
  (date>=? article-date 1month-ago))

(define categories
  '(("政治" . "politics")
    ("國際" . "world")
    ("生活" . "life")
    ("健康" . "health")
    ("財經" . "finance")))

(for ((i categories))
  (match-define (cons label name) i)
  (define timestamp (date->iso8601 (today)))
  (define filename (format "urls/ftv-~a-urls-~a.txt" name timestamp))
  (printf "\nParsing urls in category ~a...\n" name)
  (call-with-output-file* filename #:exists 'replace
    (lambda (out)
      (for ((l (scrape label 1 '())))
        (write-string l out)
        (newline out)))))
