---
title: "Nfrs Considered Harmful"
date: 2020-08-27
slug: ""
description: ""
keywords: []
draft: false
tags: []
math: false
toc: false
---

[![I’ll make this short: Defining Non-Functional Requirements (NFRs) is dangerous. That’s the tweet.](/nfrs-considered-harmful-tweet.png)](https://twitter.com/hemul/status/1365359887996379136)

An NFR is broadly defined as a ‘quality’ of the software, rather than what it ‘does’. So ‘the software shall add two numbers’ is a functional requirement, while ‘the software shall run within two minutes’ or ‘the software shall be maintainable’, or ‘scalable’, or whatever, is deemed ‘non-functional’. I submit that this is a dangerous distinction to make when running a software project.

In the large, everything is functional (This has been formalised into [Hyrum’s Law](https://www.hyrumslaw.com): _“With a sufficient number of users of an API, it does not matter what you promise in the contract: all observable behaviours of your system will be depended on by somebody.”_)

[![There are probably children out there holding down spacebar to stay warm in the winter! YOUR UPDATE MURDERS CHILDREN.](https://imgs.xkcd.com/comics/workflow.png)](https://xkcd.com/1172/)

I’ve noticed that if you call something ‘non-functional’ it immediately becomes deprioritised, a tier two requirement. What people hear is _“this would be nice to have but we don’t think anyone important actually cares much about it.”_

As an example from [Wikipedia](https://en.wikipedia.org/wiki/Non-functional_requirement), take performance requirements. They say that ‘software shall run in time X’ is a non-functional requirement. Well, it’s not important until it is. If there are no deadlines, there is no problem. Is it even a requirement? But if your software has to process a bank’s worth of securities in two hours, it is a requirement. ‘Non-functional’, my horse.

The *danger* of reflexively saying ‘it’s performance, that’s non-functional’ is the team doesn’t pay attention to it until too late. Just eliminate the category.

(originally version - http://web.archive.org/web/20201023212029/https://tech.labs.oliverwyman.com/blog/2020/08/27/nfrs-considered-harmful/)