---
title: "Expanding Reducers"
date: 2013-07-31
slug: ""
description: ""
keywords: []
draft: false
tags: []
math: false
toc: false
---

When playing with a new bit of language, it can be helpful to restrict the problem space to an old, well understood algorithm. For me at least, learning one thing at a time is easier! For this post, It’ll be prime sieves, and I’ll be exploring clojure reducers.

A quick recap, the sieve of eratosthenes is a not-maximally-non-optimal way of finding primes. It’s usually expressed as follows:


To find primes below n: generate a list of n integers greater than 1 
```
while the list is not empty: 
  take the head of the list: 
    add it to the output 
    remove all numbers evenly divisible by it from the list
```

In clojure, something like:

```clojure
(defn sieve 
    ([n] (sieve [] (range 2 n))) 
    ([primes xs]
        (if-let [prime (first xs)] 
            (recur (conj primes prime)
                   (remove #(zero? (mod % prime)) xs))
            primes
        )
    )
) 

(sieve 10)
;= [2 3 5 7]
```
Which is fine, but I’d like it lazy so I only pay for what I use, and I can use as much as I’m willing to pay for. Let’s look at lazy sequences. Luckily for us, there is an example of exactly this on the lazy-seq documentation, which we slightly modify like so:

```clojure
(defn lazy-sieve [s] 
  (cons (first s) 
    (lazy-seq 
      (lazy-sieve (remove #(zero? (mod % (first s))) (rest s))))))
(defn primes [] 
  (lazy-seq (lazy-sieve (iterate inc 2))))

(take 5 (primes)) 
;= (2 3 5 7)
```
So now we have a nice generic source of primes that grows only as we take more. But is there another way?

A few months ago Rich Hickey introduced reducers. By turning the concept of ‘reducing’ inside out the new framework allows a parallel reduce (fold) in some circumstances. Which doesn’t apply here. But let’s see if we can build a different form of sieve using the new framework. First a quick overview (cribbing from the original blog post):

> Collections are now _reducible_, in that they implement a `reduce` protocol. `Filter`, `map`, etc are implemented as functions that
can be applied by a reducible to itself to return another reducible, but lazily, and possibly in parallel. So in the example
below we have a reducible (a vector), that maps inc to itself to return a reducible that is then wrapped with a filter on
`even?` which returns a further reducible, that reduce then collects with `+`.

```clojure
(require '[clojure.core.reducers :as r])
; We’ll be referring to r here and there – just remember it’s the clojure.core.reducers namespace

(reduce + (r/filter even? (r/map inc [1 1 1 2])))
;= 6
```
These are composable, so we can build ‘recipes’.

```clojure
;;red is a reducer awaiting a collection
(def red (comp (r/filter even?) (r/map inc)))
(reduce + (red [1 1 1 2]))
;= 6
```
`into` uses reduce internally, so we can use it to build collections instead of reducing:
```clojure
(into [] (r/filter even? (r/map inc [1 1 1 2])))
;= [2 2 2]
```
So here’s the core of ‘reducer’, which 
> Given a reducible collection, and a transformation function `xf`, returns a reducible collection, where any supplied reducing **fn** will be transformed by `xf`. `xf` is a function of reducing **fn** to reducing **fn**.

```clojure
(defn reducer ([coll xf] 
  (reify clojure.core.protocols/CollReduce 
    (coll-reduce [_ f1 init] (clojure.core.protocols/coll-reduce coll (xf f1) init)))))
```
And we can then use that to implement mapping as so:
```clojure
(defn mapping [f] 
  (fn [f1] (fn [result input] (f1 result (f input))))) 
  
(defn rmap [f coll] (reducer coll (mapping f))) 
(reduce + 0 (rmap inc [1 2 3 4]))
;= 14
```
Fine. So what about sieves? One thought is we could build up a list of composed filters, built as new primes are found (see the `lazy-seq` example above). But there’s no obvious place to do the building, as applying the reducing functions is left to the reducible implementation. Another possibility is to introduce a new type of reducing function, the ‘progressive-filter’, which keeps track of past finds and can filter against them.
```clojure
(defn prog-filter [f] 
    (let [flt (atom [])] 
        (fn [f1] (fn [result input]
            (if (not-any? #(f input %) @flt)
                (do (swap! flt conj input) 
                    (f1 result input))
                result)))))

(defn progressive-filter [f coll] 
    (reducer coll (prog-filter f)))
```
And we then reduce with a filtering function that is a function of the current candidate and one of the list of found primes (see the `#(f input %)` bit above)
```clojure
(into [] (progressive-filter #(zero? (mod %1 %2)) (range 2 10)))
;= [2 3 5 7]
```
It’s nicely lazy, so we can use iterate to generate integers, and take only a few (`r/take`, as it’s operating on a reducer):
```clojure
(into [] (r/take 5 (progressive-filter #(zero? (mod %1 %2)) (iterate inc 2)))) 
;= [2 3 5 7 11]
```
Or even
```clojure
(def primes 
    (progressive-filter #(zero? (mod %1 %2)) (iterate inc 2)))

(into [] (r/take 5 primes))
;= [2 3 5 7 11]
```
You get the idea.


(Originally http://web.archive.org/web/20161006154511/http://www.lshift.net/blog/2013/07/31/expanding-reducers/)