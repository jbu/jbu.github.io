---
title: "In Defence of Breaking Change"
date: 2020-10-02
slug: ""
description: ""
keywords: []
draft: false
tags: []
math: false
toc: false
---

> Is nuance absolutely awesome, or simply rubbish? -_The news quiz, 103:2_

For the purposes of this post let’s assume it’s simply rubbish.

Received wisdom is that breaking changes to supporting software (OS, libraries, services, etc) is bad. This makes intuitive sense. An API is a contract, and contracts are to be honoured.

We have [SemVer](https://semver.org/) to attempt to manage changes. Rich Hickey thinks that SemVer is wrong, and you should [just accrete](https://www.youtube.com/watch?v=oyLBGkS5ICk). Platform providers go to great lengths to let you keep running your broken software. Here’s some Microsoft [war stories](http://ptgmedia.pearsoncmg.com/images/9780321440303/samplechapter/Chen_bonus_ch01.pdf). And of course, Linus has [an opinion](https://lkml.org/lkml/2012/12/23/75) (and is working on expressing his opinions in a more constructive way).

But there’s a hold out. Recently Steve Yegge had a [rant](https://medium.com/@steve.yegge/dear-google-cloud-your-deprecation-policy-is-killing-you-ee7525dc05dc) about how google keeps ignoring this sensible consensus. And we all know that’s true. Just try saying ‘google reader’ to a bunch of engineers and feel the wave of unresolved loss, and that’s for a free service, not a paid and supported API. But why does Google do that? Now, the first law of software engineering is “You are not Google”. You do not have a magic money machine in the basement and a good percentage of engineering talent working for you (If you do, DM me). It turns out that internally they use that money and talent to do things the hard, right way (sometimes).

_“God is change”_ says the prophet in _“Parable of the Sower”_[1]. Google faced the fact that things change, and that _“Software Engineering is Programming integrated over time”_. Getting a program to run once is programming. Getting it to keep running when the OS gets upgraded, the team changes, requirements change, dependencies are upgraded, laws change, businesses change, […] is engineering. For good software to remain good software into the future the code must be malleable and deployable.

Let’s narrow this to managing dependencies. Managing versioning between modules is a problem that scales quadratically, and is worse than you think given [Hyrum’s law](https://www.hyrumslaw.com/) that in the limit there is no such thing as a private interface. In the Google case, it’s their code and they can tackle the problem at the root. Their solution seems to be ‘live at head’. It ideally goes something like this:

* everything is comprehensively covered by automated testing
* a module is published (and it’s all public interface, see Hyrum’s Law)
* it becomes widely used
* a new version is published. It breaks a test somewhere.
* a decision is made whether to fix the module, or fix the consumer
* if many consumers will break, and they all need to be fixed, a tool is shipped to automate the fix
given it’s all in an obsessively tested monorepo the change is shipped when ‘google works with this change’
* the tail of supported versions is therefore very short, if it exists at all
* A relatively recent presentation “Live at Head“: gives a far more authoritative view. 

In essence, the contract changes from _“We will not break the contract”_ to _“We might break the contract but will provide good tools/docs (perhaps API credits?) to assist migration.”_

Now the point of the Yegge rant above is that Google is **not** doing this reliably in the public APIs. It’s hard! But let’s assume the utopia. What would a software project that uses these ‘live at head’ APIs look like? There seem to be a few things that are necessary:

* the engineering is live, as in there is institutional memory about how to make changes and get them into production
* the code is well provisioned with automated tests
* there is a live CI system that speculatively upgrades dependencies
* if a test breaks because of a dependency upgrade there is someone who can step in to investigate
* the step above is much simpler if the code is regular enough to allow automated upgrade tools to work. Newer languages like ‘Go’ are designed with this in mind

This is not a big investment, and well worth it. But it is a change of mindset. A software project from an enterprise would not just hand over a binary. They wouldn’t even just hand over a service and a monthly AWS bill. The project would involve setting up and leaving behind (or maintaining – for a reasonable consideration) the engineering capability listed above. In return, the customer would have software that has all the latest security patches, performance improvements, and so forth, and whoever is running the service would have the capability to optimise runtime platforms etc. That’s a win/win from where I’m standing.

(1) [“In the ongoing contest over which dystopian classic is most applicable to our time […] Butler’s novel […] may be unmatched.”](https://www.newyorker.com/books/second-read/octavia-butlers-prescient-vision-of-a-zealot-elected-to-make-america-great-again)

(Originally in http://web.archive.org/web/20201113035100/https://tech.labs.oliverwyman.com/blog/2020/10/02/breaking-changes/)