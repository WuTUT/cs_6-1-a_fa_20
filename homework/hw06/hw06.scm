(define (cddr s)
  (cdr (cdr s))
)

(define (cadr s)
  (car (cdr s))
)

(define (caddr s)
  (car (cddr s))
)


(define (sign num)
  (cond 
    ((> 0 num) -1)
    ((< 0 num) 1)
    (else 0)
  )
)


(define (square x) (* x x))

(define (pow x y)
  (
    if (= y 0)
        1
        (if (= 0 (modulo y 2))
            (square 
              (pow x (quotient y 2))
            )
            (* x 
              (square 
                (pow x (quotient y 2))
              )
            )
        )
  )
)

