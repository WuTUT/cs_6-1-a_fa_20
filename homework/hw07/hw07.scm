(define (filter-lst fn lst)
  (
    if (null? lst)
    lst
    (if (fn (car lst))
      
      (cons (car lst) 
            (filter-lst fn (cdr lst))
      )
      (filter-lst fn (cdr lst))
    )

  )
  
)

;;; Tests
(define (even? x)
  (= (modulo x 2) 0))
(filter-lst even? '(0 1 1 2 3 5 8))
; expect (0 2 8)


(define (interleave first second)
  (cond 
      ((and (null? first) (null? second)) nil)
      ((and (null? first) (not (null? second))) second)
      ((and (not (null? first)) (null? second)) first)
      (else (cons (car first) (cons (car second) (interleave (cdr first) (cdr second)))) )

  
  )
)

(interleave (list 1 3 5) (list 2 4 6))
; expect (1 2 3 4 5 6)

(interleave (list 1 3 5) nil)
; expect (1 3 5)

(interleave (list 1 3 5) (list 2 4))
; expect (1 2 3 4 5)


(define (accumulate combiner start n term)
  (if (= n 1)
      (combiner start (term 1))
      (combiner (term n) (accumulate combiner start (- n 1) term))
  )
)


(define (no-repeats lst)
  
  (
    if (null? lst)
      lst
      (cons (car lst) (filter (lambda (x) (not (= x (car lst)))) (no-repeats (cdr lst))))
  )
  
  
  
)

