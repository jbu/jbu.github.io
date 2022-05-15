---
title: "Lets Run Science Part Iota"
date: 2015-03-31
slug: ""
description: ""
keywords: []
draft: false
tags: []
math: false
toc: false
---

In our [last jaunt](lets-run-science.md), we had a look at code that take all the various measurements of temperature that have been taken over the last few hundred years, and pull them together into something we can usefully run stats on. The headline finding of all this is that on average, the planet has warmed over time. But why? To answer that, we need a model to play with.

A climate model (or [general circulation model](http://www.ipcc-data.org/guidelines/pages/gcm_guide.html)) attempts to model the physical processes of the earths climate. With one of these you can poke around and see what factors might be causing any changes we’re seeing. For instance, are changes in the sun causing the warming? Try running the model with constant sun and see if the temperature rise goes away. It doesn’t? Well, it’s not the sun. The tl;dr about the models is that:

1. They model the observed climate well (and are constantly getting better)
1. The observed warming is only replicated if you take the increase in human-generated CO2 into account.
We’re not going to get as far as showing that in this post because I’m short on supercomputers here, but let’s at least poke around with the technology.

Since I’m already playing around in the [GISS](http://www.giss.nasa.gov/) website, let’s see what we can dig out. For the joy of dusting off important historic technology, [Model II](http://www.giss.nasa.gov/tools/modelii/) would have been the one to pick, but it’s moved onto other pastures, and a quick check leaves me unsure if I have the appropriate compiler. So let’s try their current workhorse, [ModelE])(http://www.giss.nasa.gov/tools/modelE/).

To keep things sane, I’ve set up a gist [here](https://gist.github.com/jbu/ca44dbea0f72e77e627b) with scripts to build docker containers etc. You can run it with

```bash
$ curl https://gist.githubusercontent.com/jbu/ca44dbea0f72e77e627b/raw/modele.sh | bash
# cd modelE
# ./run.sh
```

Which should run ModelE, with completely generic parameters, from 1949/12/1 to 1950/12/2. It takes a while!

We end up with output in `/modelE/decks/my_run`. Given the length of the run there’s not much fun to be had here, so I won’t try drawing any 1-point graphs or anything. But if you’re interested there are tools for working with the output, documented in the HOWTO [here](https://github.com/addinall/GISS_climate_model/blob/master/doc/HOWTO.html#L1315).

If you want to try something more historic, `/modelE/templates/E_AR5_NINT_oR.R` is one of the the rundecks for the [CIMP5 runs](http://data.giss.nasa.gov/modelE/ar5/).

So, a few random observations about getting modelE going. It’s quite well documented! (see the `/modelE/docs` directory). `HOWTO.html` is a comprehensive guide that I’m sure a new post-grad at the group would be relieved to see.

It mostly consists modules (fortan) that can be assembled to configure a particular model.  The general work cycle seems to be to think of a way to model something (say, the albedo of surf on the sea, or clouds, or vegetation), write a module, and write a paper about how you modelled it and the effect it had (academic publications are the real documentation here). There are also publications about how particular runs were configured, listing modules used and the initial conditions ([example](http://pubs.giss.nasa.gov/docs/2014/2014_Schmidt_etal_3.pdf)).

The codebase has obviously been around for a while, so has vestigial traces of a number of generations of high performance computing libraries (libMP, MPI, etc) and the refactors between them are not complete, but it all seems well described. But what really strikes me is the ‘liveness’ of the code. It’s obviously been worked on heavily for decades, through a bunch of technology generations, with multiple owners and different team sizes, different thoughts on source code management, modularisation, and even languages (although fortran obviously is not going anywhere in this space). And a the end of it all, it is sensibly modularised, scales well, uses revision control well, has good documentation and from there looks like it has reasonable hackability. This almost never happens. I’m quietly impressed!

(http://web.archive.org/web/20161006164942/http://www.lshift.net/blog/2015/03/31/lets-run-science-part-iota/)