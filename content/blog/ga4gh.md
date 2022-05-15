---
title: "Ga4gh"
date: 2015-08-11
slug: ""
description: ""
keywords: []
draft: false
tags: []
math: false
toc: false
---

Gene sequencing has been diving in cost:

![Fall of genome sequencing cost](http://web.archive.org/web/20140124114906im_/http://cdni.wired.co.uk/1920x1280/a_c/cost_per_genome_apr.jpg)

It’s no longer in the wild ride of 2008, but still the cost is now low enough that genome data is piling up in research centres the world over. It’s been realised that a lot of the really interesting research questions can only be answered by sampling a wide range of data from a wide range of research centres. Unfortunately, they all store the data in custom formats, with individual access policies, processes, procedures and protocols, so some of the most promising medical research is being slowed or prevented by an inability to share data.

[The Global Alliance for Genomics & Health](http://genomicsandhealth.org/) (GA4GH) works to overcome this by defining interoperable standards, sort of like the [W3C](http://www.w3.org/) of genomics.

The [Data Working Group](http://ga4gh.org/#/) is developing an [API](http://ga4gh.org/#/documentation) and [reference implementation](https://github.com/ga4gh/server) of a server for sharing genomic data, and approached LShift to help with a few bits and bobs; adding OpenID Connect support so that sensible authentication can be configured, a sphinx plugin for documenting apache avro schemas, and some performance improvements. It was a short project, but great fun working with an excellent and committed global team on a solid codebase, and contributing good plumbing to some of the most important science going on. We enjoyed it so much we [joined](http://www.lshift.net/about/news/lshift-joins-ga4gh/), and look forward to contributing more in the future.

(Originally http://web.archive.org/web/20161006152309/http://www.lshift.net/blog/2015/08/11/global-alliance-for-genomics-and-health/)