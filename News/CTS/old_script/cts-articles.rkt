#lang racket/base

(require net/url
         html-parsing
         sxml
         racket/string
         json
         racket/system
         racket/file
         racket/date)

(define (scrape url category)
  (define html (html->xexp (get-pure-port (string->url url))))
  (define html->text (λ (path)
                       (string-trim (sxml:text ((sxpath path) html)))))
  (define title (html->text
                 '(// (h1 (@ (equal? (class "artical-title")))))))
  (define contents ((sxpath '(// (div (@ (equal? (class "artical-content"))))
                                 p)) html))
  (define author (sxml:text (car contents)))
  (define article-text (sxml:text (filter (λ (x)
                                            (null? (sxml:attr-list x)))
                                          (cdr contents))))
  (define datetime (html->text '(// (time (@ (equal? (class "artical-time")))))))
  (define tag-html ((sxpath
                     '(// (div (@ (equal? (class "news-tag flex-center-y")))) p a))
                    html))
  (define keywords (for/list ((a tag-html))
                     (sxml:text a)))
  (make-hash
   `((url      . ,url)
     (title    . ,title)
     (date     . ,datetime)
     (author   . ,author)
     (label    . ,category)
     (contents . ,article-text)
     (keywords . ,keywords))))

(define categories
  '(("政治" . "politics")
    ("國際" . "international")
    ("社會" . "society")
    ("生活" . "life")
    ("財經" . "money")))

(for ((i categories))
  (define label (car i))
  (define name (cdr i))
  (define d (current-date))
  (define timestamp (format "~a-~a-~a" (date-year d) (date-month d) (date-day d)))
  (define urls-file (format "urls/cts-~a-urls-~a.txt" name timestamp))
  (define urls (file->lines urls-file))
  (define tmp-file (format "json/cts-~a-tmp.json" name))
  (define out-file (format "json/cts-~a-~a.json" name timestamp))
  (printf "Beginning to parse category ~a...\n" name)
  (with-handlers ((exn:fail?
                   (λ (exn)
                     (printf "\nCould not parse ~a\n~a\n" url exn))))
    (call-with-output-file* tmp-file #:exists 'replace
      (λ (out)
        (for ((url urls))
          (printf "Parsing ~a...\r" url)
          (write-json (scrape url label) out)
          (newline out)))))
  (system (format "jq -s '.' ~a > ~a" tmp-file out-file))
  (delete-file tmp-file)
  (newline))
