---
title: "Lunchtime Hack - Lets Run Science"
date: 2015-02-27
slug: ""
description: ""
keywords: []
draft: false
tags: []
math: false
toc: false
---

Possibly part 1.

Who else likes visiting science museums? All those old apparatus – bits of the radio telescope that first saw pulsars, longitude prize clocks, jury-rigged ingenious devices that captured the first glimpse of something new and exciting. One day the LHC will be dismantled, carved up and shipped to museums around the world. For a lunchtime hack I’m going to go and have a look at something along those lines, but software.

Climate records have been collected in one form or another for hundreds of years ([here are some](http://www.realclimate.org/index.php/data-sources/#Climate_data_raw))
and we can get proxies going back [way further](http://www.ncdc.noaa.gov/data-access/paleoclimatology-data/datasets). Collecting this data has been the sort of heroic grunt-work of real science.

But if you thought the sales data you’re trying to analyse is a mess, you lead a sheltered life! One of the apparatus that has really made a scientific and social impact over the last few decades has been methods, implemented in code, for pulling these data sets into something that can show whether or not the earth’s temperature is changing, and with a bit more work, why. So let’s go and visit one of these devices and take it for a spin.

There are a few of these things to choose from. [Berkeley Earth](http://berkeleyearth.org/land-and-ocean-data) is a recent one but it’s all in matlab which I don’t have installed, so move on. [GISTEMP](http://data.giss.nasa.gov/gistemp/) from NASA is another major look at surface temperature. Ahh, it has downloadable code and data that looks mostly python and a bit of fortran. Let’s see what we can get running.

I’m expecting (and found) bitrot. Docker seems like it would be a useful way of preserving these sorts of projects, because it can manage the runtime dependencies, so I’m going to build a docker image of my work (and a `run.sh`) as I go. You can get it [here](https://github.com/jbu/gistemp-docker). Build this container, run it (and be dropped into the shell) with `./build.sh`. Then run `./gistemp.sh`. You’ll need `docker` and `docker-machine`.

So, the readmees are pretty clear. Some data needs to be fetched and some of the URLs have changed slightly but it’s easy enough to track down. It takes in data from GHCNv3 (Global Historical Climate Network from NOAA) and Antarctic SCAR (Scientific Committee on Antarctic Research) data.

Step 0, which merges the sources:

```bash
$ do_comb_step0.sh
reformatting to v2 format
Bringing Antarctic tables closer to v2.mean format
collecting surface station data
... and autom. weather stn data
... and australian data
replacing '-' by -999.9, blanks are left alone at this stage
adding extra Antarctica station data to input_files/v3.mean
created v2.meanx from v2_antarct.dat and input_files/v3.mean

GHCN data:
 removing data before year   1880.00000
created v2.meanz from v2.meanx
replacing Hohenspeissenberg data in v3.mean by more complete data (priv.comm.)
disregard pre-1880 data:

created v3.mean_comb
move files from temp_files/. to ../STEP1/temp_files/.
and execute in the STEP1 directory the command:
   do_comb_step1.sh v3.mean_comb
```

Now, Step 1 ‘eliminates some dubious records’. It has some python extensions that need to be compiled – In fact I end up patching it slightly and moving to setup.py. But then

```bash
Creating v3.mean_comb.bdb
reading v3.mean_comb
reading v3.inv
writing v3.mean_comb.bdb
Dropping strange data
reading Ts.strange.RSU.list.IN
reading v3.mean_comb.bdb
writing v3.mean_comb.strange.bdb
reading v3.mean_comb.strange.bdb
creating v3.mean_comb.strange.txt
1000
2000
...
created Ts.txt
move this file from STEP1/temp_files to STEP2/temp_files
and execute in the STEP2 directory the command:
   do_comb_step2.sh last_year_with_data
```

Step 2: Splitting into zonal sections and homogenization. This compares rural and urban stations to remove any effect of the urban environment.

```bash
converting text to binary file
 last year with data:        2013  LightGl=           1
        1000 processed so far
        2000 processed so far
        3000 processed so far
        4000 processed so far
        5000 processed so far
        6000 processed so far
        7000 processed so far
 number of station ids:        7354
 ...
 created Ts.GHCN.CL.* files
move them from STEP2/temp_files to STEP3/temp_files
and execute in STEP3 do_comb_step3.sh
```

and then

Step 3 : Gridding and computation of zonal means

...

gives us a file `SBBX1880.Ts.GHCN.CL.PA.1200` which is a nasty fortran blob that apparently contains the grid of surface temperature anomalies. Great! Let’s plot that! There are some files at nasa (linked in the build/run scripts here) that can convert this `SBBX` file to a `NetCDF` file that can be viewed. Problem is, the programs supplied take some memory. In fact, a few random checks suggest 10s of Gigs, which is beyond my macbook. So let’s leave it here… But what we were shooting for was

![Geo plot](/lets-run-science.gif)

So there you are. Just like repeating a cloud-chamber experiment in school physics we haven’t actually learned anything that hasn’t already been published and pored over. We haven’t actually looked at the code to really see what it’s doing.

But, I now have a major bit of science history (from NASA!) running (mostly) on my laptop. That’s at least a bit cool.

Also, docker has more uses than you think.



(Originally http://web.archive.org/web/20161006160845/http://www.lshift.net/blog/2015/02/27/lunchtime-hack-lets-run-science/)