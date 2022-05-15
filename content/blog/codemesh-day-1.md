---
title: "Codemesh Day 1"
date: 2014-11-28
slug: ""
description: ""
keywords: []
draft: false
tags: []
math: false
toc: false
---

I was at day 1 of CodeMesh this year (you can see Tim’s report on day 2 [here](http://web.archive.org/web/20161006151917/http://www.lshift.net/blog/2014/11/06/codemesh-2014-day-2/)). A quick recap:

> **QOTD**: There are 3 fire exits as marked, but we’re confident that Erlang programmers who die will be restarted.


## Keynote: complexity is outside the code
### Jessica Kerr & Dan North
A good, entertaining talk that covered a lot of ground (and thankfully, someone else has a gist of better notes, so you can read [them](https://gist.github.com/philandstuff/f9f95030acff9a14fa76)), But my main takeaways were:

We have architectures, Boxes and arrows, or layering, messaging, modularity but complexity is never defeated because it arises from difficult cross-cutting problems like performance, security, monitoring, etc. Each requires a different skill set. A Solution: Master a few, hope the broader team cover the rest.

Research is different from a spike. Cost of a bad design is a long-tail distribution (unbounded). A spike leads to the choice of quickest-to-hello-world solution. Research can be bounded (spend 2 days, or fund a research star and team) but has long-tail payoff.

Lots of ground on estimation and how underestimating accumulates debt which conflicts with the overall the goal to “sustainably minimize lead time to business impact” and it’s the sustainably that brings in the harder to sell aspects of a solid development approach.

And a lot more, but probably the best thing to do is read [the slides](https://www.slideshare.net/jessitron/complexity-is-outside-the-code). [video](https://www.infoq.com/presentations/complexity-simplicity-esb/)

## The F♯ approach to relaxation
### Don Syme
This sold F# really well.

The great disputes of computer science should be struggled with. They are chances to make a better, simpler, more relaxed world as much as create opposing camps. thesis, antithesis, synthesis. but you can take it too far, e.g [Integrating time and food with a mustard watch](http://girard.perso.math.cnrs.fr/mustard/article.html)

F# has a history of trying to integrate things

Functional languages ⇔ interop.

* FN languages used to have standalone vms and relied on com, corba, etc for interop.
* New approach (also scala, swift, clojure, etc) => embrace runtime and extend with FP needs so language can run on them. F# type providers do even better by making the language extensible. – Not everything is perfect cf higher kinded type parameters, functors, …

Enterprise ⇔ Openness.

* F# is open, cross platform, independent, accepting contributions. F# foundation non-profit fsharp.org. Cross platform is with mono/xamarin. Community very ‘self-empowered’
* Different from ‘usual windows/ms communities’. Codeplex and github repos will be merged but right now codeplex is used by ms to feed into their industrial strength release process.
* F# compiler service (sf IFSharp, emacs, vim plugins)
* Language design at fslang.uservoice.com
* Enterprise quality + openness + community + tooling + ecosystem = goodness

Functional ⇔ Objects

* Embrace objects. Not full object-orientation, but functional first.
* Data point. same app, 350k lines C# vs 30K F#. Faster and more features (parallel etc) with F#
* So Hindley-Milner type inference sort of clashes a bit with OO, but F# gets quite a long way. You have to resort to type annotations at some point. Currying and method overloading clash.
* Circularities and modularity in the wild. Mixed style languages have won, and swift and Java8 have lambdas and function types. But, Inheritance is everywhere, nulls are everywhere, circularities are everywhere (cyclic dependencies). Files in C# assembly are mutually referential. F# has a file ordering (with breakout within object system if needed). In the wild F# inter component dependencies are fewer. Circular dependencies are virtually nil. Microsoft Entity Framework called out as particularly frightening anti-example.

Pattern matching ⇔ Abstraction.

* Pattern matching everywhere in F#. But patterns have their problems. You really want to name, abstract and parametrize patterns, otherwise you have to break abstraction boundaries to get the convenience. => Active patterns.

Code ⇔ Data

* Type providers. Bring type info into the language. Strongly typed csv file reader FTW.

units ⇔ units-of-measure

* TIL F# will do unit analysis.

gpu ⇔ cpu

* Apparently good stuff at alea gpu. F# quotations help here.

REPL ⇔ distribution and scale

* Unsolved. github.com/nessos/Vagrant mentioned. And mbrace

[page](https://www.codemesh.io/codemesh2014/don-syme)

## Functional programming in data sciences
### Richard Minerich

Richard is from Bayard Rock, an anti-money laundering co. They use a pairwise entity resolution process. (Fellegi-Sunter circa 1969) matching, datasets, customer (10e6) and list (2e6). pairs of somehow similar records, then scoring, then blocking a transaction based on the result. Scoring is done through a big social pagerank of risk. How likely is this person to be laundering money, given their relationships?

Some points:

* Data science is mostly about data munging.
* Every client (s data) is awful in a completely different way
* Working with bank (systems) is a pain
* Wrote the thing in F#, using quotations
* Produced FSharpWEbIntellisense for Ace
* And IFsharp notebook
* And barb (http://github.com/Rickasarus/barb) which is an end-user data mining language
* Also: MITIE looks interesting (mit) – semantic interpretation of raw text.

Also, Combined regression and ranking, a paper from Google (D. Sculley). In regression, you’re trying to guess a number and only distance matters – may do bad job at ordering. But for ranking, you are trying to figure out order.

[page](https://www.codemesh.io/codemesh2014/richard-minerich)

## Categories for the working programmer
### Jeremy Gibbons
Jeremy has a [blog](http://patternsinfp.wordpress.com/)

Overall point: Category theory is good for library design, and I can’t really argue with that. TIL I need to know more about category theory.

He started with `sum`, and how it’s a generalisation of `foldr`, and `foldr` is nice and generic. In particular you can separate out the data ‘shape’ from type recursion – eg for list

```Haskell
data ListS a b - MilS | ConsS a b
data Fix s a = In (s a (Fix s a))
or data Fix s a = In {out :: s a (Fix s a)}
type List a - Fix ListS a
bimap :: (a -> a’) -> (b -> b’) -> ListS a b -> ListS a’ b’
```

Now we can define `foldr` on List

```Haskell
foldList :: (ListS a b -> b) List a -> b
foldList f= f . bimap id (foldList f) . out
eg foldLIst add :: List Integer -> Integer, where
add :: ListS Integer Integer -> Integer
add NilS = 0
add (ConsS m n) = m + n
```

For datatype genericity, a typemap Bifunctor can be used. So, think of a bifunctor, S. It is also a functor in each argument separately.
An algebra for functor S A is a pair (B, f) where f :: S A B -> B
A homomorphism between (B, f) and (C,g) is a function h :: B -> C such that h.f=g.bimap id h
Algebra (B, F) is initial if there is a unique homomorphism to each (C, g)
eg, (List Integer, In) and (Integer, add) are both algebras for ListS Integer:

```Haskell
In :: ListS Integer (LIst Integer) -> List Integer
add:: ListS Integer Integer -> Integer
```

and `sum::List Integer -> Integer` is a homomorphism. The initial algebra is (List Integer, In), and the unique homomorphism to (C,G) is fold g.

I need to meditate on this (or ask someone here to educate me).

[page](https://www.codemesh.io/codemesh2014/jeremy-gibbons)

## Social Code
### Garret Smith
Coding is social (C.F. github).
Social coding is a dynamic in programming that respects a communication line from one person to another. The talk became a tutorial in how to write software to express yourself to other coders (or yourself later). Be respectful to the maintainer. I find that my colleges at LShift are already on top of this, so left early and went to:

[page](https://www.codemesh.io/codemesh2014/garrett-smith)

## MariaDB
### Michael Widenius
Stuck around long enough to find out that 10.1 has multimaster mesh. And the foundation structure should keep the project in the open regardless of who buys what.

## Type-directed Development
### Clement Delafargue
* Scala is not really typesafe, or has untypesafe features.
* But if you don’t do anything untypesafe, then if it type checks it’s good.
* Haskell type syntax is the way to talk about types.
* You can use too many animated gifs in a talk.

[page](https://www.codemesh.io/codemesh2014/clement-delafargue)

## Lightning fast cluster computing with spark and cassandra
### Pitor Kolaczkowski

* Cassandra stores data in Tables. There is a partition key, a primary key, and data columns
* Spark model is differently. It uses distributed collections (the Resilient Distributed Dataset) modelled on (similar to?) scala collections so you can map, filter, reduce. Like scala collections they are immutable, iterable, serializable, distributed, parallel. But you don’t get random access
* Pitor had an open source bridge between the two.

[video](https://www.infoq.com/presentations/spark-cassandra/) 

It became a tutorial which was not what I was interested in at that moment, so dropped into:

## Beyond Shady AI with OpenCL: Massively Parallel Algorithms on GPGPUs
### Alex Champandard
Ideas for doing AI on the GPU. TL;DR you have to rethink your algorithm choice a bit because it’s highly parallel and you don’t want to coordinate.

[video](https://vimeo.com/113485431)


Programming and testing a distributed database
Reid Draper
Had to go early but found out that RPC was actually the RFC before TCP! The early thrust of the talk was that we’ve been trying to figure out distribution for a looong time. Go look at some history and we may learn something. I imagine he got onto what we have learned, so a pity I had to go.

Remarks
Overall a good day. Talks were videoed but most of the ones I went to are not up (yet?). Lunch was great. Perhaps more of those little tables for people to gather and eat at to encourage mingling. Joe Armstrong is not how I imagined him.

(Originally http://web.archive.org/web/20161006151917/http://www.lshift.net/blog/2014/11/28/codemesh-2014-day-1/)