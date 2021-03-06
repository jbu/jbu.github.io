---
title: "The Life Changing Magic of Refactoring"
date: 2015-10-30
slug: ""
description: ""
keywords: []
draft: false
tags: []
math: false
toc: false
---

I’m really a unix guy, but I have to admit, the whole .NET/SQLserver stack is hugely empowering. An average employee can take it, and with next to no knowledge or experience, but with a lot of determination and time, can write enough code to underpin an entire company. You start with a windows form, place a control, it generates an event handler for you, you stick in a bit of sql, and off you go, and it works! (for a sufficiently broad understanding of ‘works’). And the creator becomes the company hero because whenever something blows up or catches fire, you can go to them and they can make things work again!

The code becomes a broad expanse of event handlers randomly wired together. You and I might have a few laugh out loud moments when examining it, and trying to actually understand it is a trip into the dark nightmares of a tormented soul. Reliving the time they discovered database triggers, or misunderstood a blog post about a design pattern.

**This sort of code runs the world.**

Anyway, just say the one person team who developed the whole shebang is no longer available, and you’re called in to help keep things going or even make it better. You have a choice, you can rewrite or refactor. Now your instinct is to drive a stake through the dark heart of the abomination, burn it with fire, and write a clean new system in Haskell (or perhaps Rust, given the chatter around the office today).
I completely understand, but just hold on for a moment! If you rewrite, then you’re committing to supporting the current version (which is prone to conflagration), while at the same time transferring every undocumented feature and assumption into the new system, and then seamlessly migrating data, and operations teams, across, which is more tricky than you think. At the same time, whenever there is a lean time it’s the new hotness that’s for the chopper, because the old and busted is what’s actually running the company. So chances are you’re never going to get to finish your new hotness, and you’re stuck supporting the old and busted indefinitely. Welcome to a special circle of hell. [1]
The harder but less risky option is to face the old and busted, like Hercules faced the Aegean Stables, and start cleaning. But how? Where to start? There are many books on refactoring and removing technical debt. And my new favourite is ‘The Life-Changing Magic of Tidying: A simple, effective way to banish clutter forever’ by [Marie Kondo](https://konmari.com)

For those of you who missed the pop culture storm this book created when published a year or so ago, it’s a how-to for tidying your home. But more than that, the ‘Konmari’ method can become a lifestyle change, and to some facebook groups, a religion. Flame wars about how to arrange socks! Who knew? Anyway, I quite like the konmari method, and I’ve started to look at how it can be used to clean even the most cluttered home^h^h^h^h codebase, identifying transformations that can be applied to turn mess into something manageable.
For those of you who haven’t been exposed, the Konmari method may be summarised as:

* Pick a category (clothes, books, dvds, kitchen things, paperwork, etc). She has a preferred order to work in.
* Get **everything** in that category into one place, where you can see it (search the garage, loft, basement, parent’s house, etc and make sure you get it **all**).
* Find the things that ‘spark joy’, and **throw the rest away**. Or give, recycle, whatever. Just get it out of your life.
* Put the remainder in a deliberately chosen place, in such a way that you can see them (so they get used!). She has suggestions for this.
* Keep it up (but it’s easy once you do the first big clean)
* Enjoy your new life where you are in control of your stuff!

I propose that this applies to code. I’ve long held that the best broad metric for technical debt is lines of code, and aggressively getting rid of code is often the most productive thing you can do. That said, you have no idea what you can get rid of until you can get an overview of everything that relates. So, here are some early thoughts of ‘categories’ in code, and how ‘getting everything into one place’ might look.

A **database table** might be a category. Getting it all into one place would mean reducing any related stored procedures, sql functions or triggers to minimum and transferring the logic to your client language where it can be refactored as a whole. You might find that you need to introduce some sort of wrapper that contains the common code found among all the various interactions with the table, which is a win. You may also find that huge swathes of the code are just not used. Get rid of it!

**UI**: Log every time a form opens (yay the ELK stack!). If after a month or so you find that there are forms that are not used, you know what to do!

**Integrations**: Sometimes links to other systems are not over a well defined bridge, but through random API calls thorough your system. Build a bridge. Centralise the integration. Refactor *all* the code to use the bridge. This might allow you to, say, use a queue in the bridge to solve a performance problem, or do something helpful with a network where you couldn’t before.

**Business crown jewels**: Is there a process, reporting system, large calculation, that is business critical but not in a well specified and defined location in the code? Make it so! Capture it in a well designed module (and keep it safe).

Often each of these can be set up as a project that delivers something concrete and useful to the customer, even if it’s reduced risk or support costs. That makes it far easier to justify and support. You get to move from win to win until (eventually) you end up with the new hotness, just by a different path.

[![Konmari all the things!](https://memegenerator.net/img/instances/62502463.jpg)](http://memegenerator.net/instance/62502463)



(Originally http://web.archive.org/web/20161006162129/http://www.lshift.net/blog/2015/10/30/the-life-changing-magic-of-refactoring/)