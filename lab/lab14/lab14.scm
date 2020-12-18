(define (split-at lst n)
  
  (if (= n 0) 
      (cons nil lst) 
      (if (null? lst) 
          (cons lst nil)
          (
           let ((rec (split-at (cdr lst) (- n 1) )))
               (cons (cons (car lst) (car rec)) (cdr rec) ) 
              
          )
      )
    
  
  )
)

(define (compose-all funcs)
  (if (null? funcs) (lambda (x) x)  (lambda (x) 
                                            ( 
                                              (compose-all (cdr funcs))
                                               ((car funcs) x) 
                                            ) 
                                    )
  )
)

