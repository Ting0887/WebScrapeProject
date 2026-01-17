#lang racket/base

(require net/url
         html-parsing
         sxml
         racket/string
         json
         racket/file
         racket/system
         racket/match
         gregor)

(define (scrape url category)
  (define html (html->xexp (get-pure-port (string->url url))))
  (define (html->text path)
    (string-trim (sxml:text ((sxpath path) html))))
  (define title (html->text
                 '(// (h1 (@ (equal? (class "text-center")))))))
  (define summary (html->text
                   '(// (div (@ (equal? (id "preface")))) p)))
  (define contents (html->text
                    '(// (div (@ (equal? (id "newscontent")))) p)))
  (define datetime (html->text
                    '(// (li (@ (equal? (class "date")))))))
  (make-hash
   `((url      . ,url)
     (title    . ,title)
     (date     . ,datetime)
     (label    . ,category)
     (summary  . ,summary)
     (contents . ,contents))))

(define categories
  '(
    ("政治" . "politics")
    ("國際" . "world")
    ("生活" . "life")
    ("健康" . "health")
    ("財經" . "finance")))

(for ((i categories))
  (match-define (cons label name) i)
  (define timestamp (date->iso8601 (today)))
  (define urls-file (format "urls/ftv-~a-urls-~a.txt" name timestamp))
  (define urls (file->lines urls-file))
  (define tmp-file (format "json/ftv-~a-tmp.json" name))
  (define out-file (format "json/ftv-~a-~a.json" name timestamp))
  (printf "Beginning to parse category ~a...\n" name)
  (with-handlers ((exn:fail?
                   (lambda (e)
                     (printf "\nCould not parse ~a\n~a\n" url e))))
    (call-with-output-file* tmp-file #:exists 'replace
      (lambda (out)
        (for ((url urls))
          (printf "Parsing ~a...\r" url)
          (write-json (scrape url label) out)
          (newline out)))))
  (system (format "jq -s '.' ~a > ~a" tmp-file out-file))
  (delete-file tmp-file)
  (newline))
