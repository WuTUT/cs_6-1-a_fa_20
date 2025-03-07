(define (over-or-under num1 num2)
  (if (< num1 num2) 
      -1
      (if (= num1 num2)
          0
          1
      )
  )
)

;;; Tests
(over-or-under 1 2)
; expect -1
(over-or-under 2 1)
; expect 1
(over-or-under 1 1)
; expect 0


(define (make-adder num)
  (
    lambda (inc) 
      (+ num inc)
    
  )
)

;;; Tests
(define adder (make-adder 5))
(adder 8)
; expect 13


(define (composed f g)
  (lambda (x)
    (
      f (g x)
    )
  )
)


(define lst
  (cons (cons 1 nil) 
        (cons 2 (cons  
                  (cons 3 (cons 4 nil))
                  (cons 5 nil)
                )
        )
  )
)


(define (remove item lst)
  (
    if (null? lst) 
      lst
      (
        if (= item (car lst))
          (remove item (cdr lst))
          (cons (car lst) (remove item (cdr lst)))
      )
    
  )
)


;;; Tests
(remove 3 nil)
; expect ()
(remove 3 '(1 3 5))
; expect (1 5)
(remove 5 '(5 3 5 5 1 4 5 4))
; expect (3 1 4 4)

