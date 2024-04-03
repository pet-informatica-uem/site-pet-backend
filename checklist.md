# OWASP Web Application Security Testing Checklist
- Available in [PDF](OWASP/OWASP%20Web%20Application%20Security%20Testing%20Checklist.pdf) or [Docx](OWASP/OWASP%20Web%20Application%20Security%20Testing%20Checklist.docx) for printing
-  [Trello Board to copy yours](https://trello.com/b/zTSkJPkL/owasp-web-checklist)

## Table of Contents

* [Information Gathering](#Information)
* [Configuration Management](#Configuration)
* [Secure Transmission](#Transmission)
* [Authentication](#Authentication)
* [Session Management](#Session)
* [Authorization](#Authorization)
* [Data Validation](#Validation)
* [Denial of Service](#Denial)
* [Business Logic](#Business)
* [Cryptography](#Cryptography)
* [Risky Functionality - File Uploads](#File)
* [Risky Functionality - Card Payment](#Card)
* [HTML 5](#HTML)

-------
### <a name="Information">Information Gathering</a>
- [x] Manually explore the site
- [ ] Check for files that expose content, such as robots.txt, sitemap.xml, .DS_Store
- [ ] Check the caches of major search engines for publicly accessible sites
- [ ] Check for differences in content based on User Agent (eg, Mobile sites, access as a Search engine Crawler)
- [ ] Perform Web Application Fingerprinting
- [x] Identify technologies used
- [x] Identify user roles
- [x] Identify application entry points
- [x] Identify all hostnames and ports


### <a name="Configuration">Configuration Management</a>

- [x] Check for commonly used application and administrative URLs
- [x] Check for old, backup and unreferenced files
- [x] Check HTTP methods supported and Cross Site Tracing (XST)
- [x] Test file extensions handling
- [x] Test for security HTTP headers (e.g. CSP, X-Frame-Options, HSTS)
- [x] Check for sensitive data in client-side code (e.g. API keys, credentials)


### <a name="Transmission">Secure Transmission</a>

- [x] Check SSL Version, Algorithms, Key length
- [ ] Check for Digital Certificate Validity (Duration, Signature and CN)
- [ ] Check credentials only delivered over HTTPS
- [ ] Check that the login form is delivered over HTTPS
- [ ] Check session tokens only delivered over HTTPS
- [ ] Check if HTTP Strict Transport Security (HSTS) in use



### <a name="Authentication">Authentication</a>
- [x] Test for user enumeration
- [x] Test for authentication bypass
- [x] Test for bruteforce protection
- [x] Test password quality rules
- [x] Test password reset and/or recovery
- [x] Test password change process
- [ ] Test for logout functionality presence
- [ ] Test for user-accessible authentication history
- [ ] Test for out-of channel notification of account lockouts and successful password changes



### <a name="Session">Session Management</a>
- [x] Check session termination after a maximum lifetime
- [x] Check session termination after relative timeout
- [x] Check session termination after logout
- [x] Test to see if users can have multiple simultaneous sessions
- [x] Test session cookies for randomness
- [x] Confirm that new session tokens are issued on login, role change and logout



### <a name="Authorization">Authorization</a>
- [ ] Test for path traversal
- [x] Test for horizontal Access control problems (between two users at the same privilege level)
- [x] Test for missing authorization


### <a name="Validation">Data Validation</a>
- [ ] Test for Reflected Cross Site Scripting
- [ ] Test for Stored Cross Site Scripting
- [ ] Test for DOM based Cross Site Scripting
- [ ] Test for Cross Site Flashing
- [ ] Test for HTML Injection
- [ ] Test for IMAP/SMTP Injection
- [ ] Test for Format String
- [x] Test for incubated vulnerabilities
- [x] Test for NoSQL injection
- [x] Test for HTTP parameter pollution
- [x] Test for auto-binding
- [x] Test for Mass Assignment
- [x] Test for NULL/Invalid Session Cookie

### <a name="Denial">Denial of Service</a>
- [ ] Test for anti-automation
- [ ] Test for account lockout
- [ ] Test for HTTP protocol DoS


### <a name="Business">Business Logic</a>
- [ ] Test for feature misuse
- [ ] Test for lack of non-repudiation
- [ ] Test for trust relationships
- [ ] Test for integrity of data
- [ ] Test segregation of duties


### <a name="Cryptography">Cryptography</a>
- [ ] Check if data which should be encrypted is not
- [ ] Check for wrong algorithms usage depending on context
- [ ] Check for weak algorithms usage
- [ ] Check for proper use of salting
- [ ] Check for randomness functions


### <a name="File">Risky Functionality - File Uploads</a>
- [X] Test that acceptable file types are whitelisted
- [ ] Test that file size limits, upload frequency and total file counts are defined and are enforced
- [ ] Test that file contents match the defined file type
- [ ] Test that all file uploads have Anti-Virus scanning in-place.
- [ ] Test that unsafe filenames are sanitised
- [ ] Test that uploaded files are not directly accessible within the web root
- [ ] Test that uploaded files are not served on the same hostname/port
- [ ] Test that files and other media are integrated with the authentication and authorisation schemas

### <a name="HTML">HTML 5</a>
- [ ] Test Web Messaging
- [ ] Test for Web Storage SQL injection
- [ ] Check CORS implementation
- [ ] Check Offline Web Application

Source: [OWASP](https://www.owasp.org/index.php/Web_Application_Security_Testing_Cheat_Sheet)