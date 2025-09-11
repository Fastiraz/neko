---
title: "AS_REP Roasting"
date: 2020-03-19 07:10:06
author: "Pixis"
layout: post
permalink: /kerberos-asrep-roasting/
redirect_from:
  - "/kerberos-asrep-toasting"
  - "/kerberos-asrep-toasting/"
disqus_identifier: 0000-0000-0000-00a8
cover: assets/uploads/2019/02/asreqroast_no_auth.png
description: "When asking for a TGT, a user has to preauthenticate himself to the domain controller in order to get a response. If preauthentication is disabled, this account is vulnerable to as_rep roasting attack."
tags:
  - "Active Directory"
  - Windows
translation:
  fr: 
---

When asking for a TGT, by default, a user has to authenticate himself to the domain controller in order to get a response. Sometimes, no authentication is asked before returning a TGT for specific account, allowing an attacker to abuse this configuration.

<!--more-->

## Preamble

When we talk about TGT it's often a language abuse, because we are talking about the [KRB_AS_REP](/kerberos/#krb_tgs_rep) which contains the TGT (encrypted by the domain controller's secret) and the session key (encrypted with the user account secret).

In this article, the TGT notion will refer to the TGT contained in the [KRB_AS_REP](/kerberos/#krb_tgs_rep) response.

## Pre-authentication

When we talked about how [Kerberos works](/kerberos), it was highlighted that during the first exchange ([KRB_AS_REQ](/kerberos/#krb_tgs_req) - [KRB_AS_REP](/kerberos/#krb_tgs_rep)), the client must first authenticate himself to the domain controller, before obtaining a TGT. A part of the response of the domain controller being encrypted with the client's account secret (the session key), it is important that this information is not accessible without authentication. Otherwise, anyone could ask for a TGT for a given account, and try to decrypt the encrypted part of the response [KRB_AS_REP](/kerberos/#krb_tgs_rep) in a brute-force way in order to recover the password of the targeted user.

[![KRB_AS_REP](/assets/uploads/2018/05/asrep.png)](/assets/uploads/2018/05/asrep.png)

That's why the user, in his [KRB_AS_REQ](/kerberos/#krb_tgs_req) request, must send an authenticator encrypted with his own secret in order for the domain controller to decrypt it and send back the [KRB_AS_REP](/kerberos/#krb_tgs_rep) if it is successful. If an attacker asks for a TGT with an account he does not have control over, he won't be able to encrypt the authenticator correctly, therefore the domain controller will not return the desired information.

[![Authentication Required](/assets/uploads/2019/02/asreqroast_auth.png)](/assets/uploads/2019/02/asreqroast_auth.png)

This is the default behavior, it protects the accounts against this offline attack.

## KRB_AS_REP Roasting

However, for some strange reason (dark one though), it is possible to disable the pre-authentication prerequisite for one or more account(s).

[![Preauthentication Setting](/assets/uploads/2019/02/preauthsettings.png)](/assets/uploads/2019/02/preauthsettings.png)

For example in [this article](https://laurentschneider.com/wordpress/2014/01/the-long-long-route-to-kerberos.html), the author states that in order to benefit from SSO on a database hosted on a Unix server, he has to disable the pre-authentication for the user. It remains a very rare case, and even [cptjesus](https://twitter.com/cptjesus) and [Harmj0y](https://twitter.com/harmj0y) don't really have an answer.

> cptjesus > As far as why its disabled, I couldn't tell you

> Harmj0y > I honestly don’t really know why it would be disabled, just have heard from a people about the linux/"old" angle.

Anyway, if this option is disabled, anyone could ask for a TGT in the name of one of these accounts, without sending any authenticator, and the domain controller will send back a [KRB_AS_REP](/kerberos/#krb_tgs_rep).

[![Authentication Required](/assets/uploads/2019/02/asreqroast_no_auth.png)](/assets/uploads/2019/02/asreqroast_no_auth.png)

This can be done with the [ASREPRoast](https://github.com/HarmJ0y/ASREPRoast) tool of [@Harmj0y](https://twitter.com/harmj0y) or more recently with [Rubeus](https://github.com/GhostPack/Rubeus#asreproast) using `asreproast` functionnality.

[![ASREPRoast](/assets/uploads/2019/02/attackasrep.png)](/assets/uploads/2019/02/attackasrep.png)

There is also impacket [GetNPUsers.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/GetNPUsers.py) tool that can perform this operation.

Once in possession of the domain controller response [KRB_AS_REP](/kerberos/#krb_tgs_rep), the attacker can try to find out the victim's clear text password offline, by using John The Ripper with the `krb5asrep` mode, or with hashcat for example.

## Conclusion

This technique, also described in an [article](https://www.harmj0y.net/blog/activedirectory/roasting-as-reps/) wrote by [Harmj0y](https://twitter.com/harmj0y), is a way to retrieve a clear text password within an Active Directory environment **when you don't have any foothold**. But if you don't have any account yet, it can be difficult to find out this information as you are not able to talk with the domain controller. An OSINT phase can be useful to enumerate as many valid account as possible, and try this attack on every account you found.

If any account is set up so that it does not need a pre-authentication, an attacker could simply ask for a TGT for this account and try to recover its password. With powerful machine, the cracking speed can be really huge. However, you should be aware that accounts without the necessary pre-authentication required are pretty rare. They can exist for historical reason, but [kerberoasting](/kerberoasting) is still more widespread.
