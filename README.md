# TSS Operations & Automation Platform

> A multi-service operations platform for Gmail workflows, email and DNS diagnostics, domain and IP management, browser automation, and live process reporting.

TSS brings a collection of practical operations tools into one web application. Instead of switching between separate scripts and dashboards, teams can work from a unified interface, run long-lived tasks, follow progress as it happens, and download useful results.

This project also demonstrates how a Python web application can connect browser-based workflows, email services, DNS lookups, JavaScript interfaces, and operational controls in one system.

## What the platform includes

### Gmail and email workflows
<img width="1908" height="915" alt="image" src="https://github.com/user-attachments/assets/27d97a9a-9ee1-4221-8ef4-00b4834c7c38" />

- View Gmail accounts and email folders through IMAP.
- Search, filter, and inspect messages, with live updates for supported views.
- Extract email content in full-source, plain-text, or HTML formats.
- Analyze message headers, sender IP addresses, and SPF, DKIM, and DMARC indicators.
- Manage separate Gmail accounts for email and news workflows.

### Domain, DNS, and deliverability tools

- Look up MX, TXT, SPF, DMARC, and A records.
- Run bulk checks with parallel lookups, live progress, and downloadable results.
- Generate SPF and DNS record output from supplied domains, IPs, A records, and include records.
- Check IP and domain reputation against configured blocklists.
- Analyze SPF include and A-record relationships, search SPF data, and check whether an IP is authorized.
- Discover subdomains and manage reusable, entity-scoped domain lists.
- Check domain availability through the domain-finder workflow.

### Browser and content automation

- Use Playwright-powered browser workflows for supported registration and subscription tasks.
- Run the Quality Seeds Helper to gather image and PDF materials from search terms and organize generated results.
- Track automation progress and manage individual processes from the web interface.

### IP and operational management

- Organize servers, CIDR classes, and IP addresses.
- Search IPs and record status events, including custom event types and event history.
- Start, pause, resume, stop, and review supported background processes.
- View centralized process status and download process results where available.
- Manage warmup lists, warmup history and reports, proxy-warmup data, desktop status files, and TSSW reports.
- Share browser extensions through a library with version history and downloads.

### User and access administration

- Manage users, roles, permissions, and per-user process or domain quotas.
- Control which tools are available to each role or user.
- Configure optional IP-based login restrictions and exempt users.
- Invalidate active sessions and require users to sign in again.

## Automation, APIs, and interface

The application combines Flask pages with JavaScript-driven interactions. The browser interface uses JSON endpoints for actions such as account and list management, user administration, process control, and IP operations. Server-Sent Events (SSE) provide live progress for supported email, DNS, blacklist, and account workflows.

Background threads and worker pools run supported jobs without holding a page request open. Several workflows support process history and controls such as pause, resume, stop, or restart recovery. CSV, ZIP, and text downloads are available in the services that produce exportable results.

## Security and deployment note

The application includes login and session management with Flask-Login, role- and permission-based access controls, optional IP allowlisting, session invalidation, and administrative user controls. These are application features, not a claim of a security audit or certification.

**Do not publish the imported project as-is.** The current project files include sensitive credentials and account/configuration data, and credentials are also embedded in source code. Before pushing to GitHub—especially a public repository—remove live credentials, user and account data, private exports, and operational files; move secrets into environment variables or a secrets manager; rotate any credentials that have been present in the project; and check the repository history for previously committed secrets. A clean README does not make the rest of the repository safe to publish.

## Technology

- **Backend:** Python 3.11+, Flask, Flask-Login
- **Frontend:** HTML, CSS, and JavaScript
- **Browser automation:** Playwright
- **Email:** Gmail IMAP
- **Domain and network lookups:** DNS resolver tooling and SPF analysis
- **Data and integrations:** JSON/file-backed operational data and a MySQL connector
- **Live updates:** Server-Sent Events and asynchronous background workers

## Screenshots

No sanitized screenshots were included with the imported project. Before sharing this repository with clients, add screenshots captured from a demo account with sample data—for example, the Services dashboard, Domain Checker results, and Processes Management view. Do not include real email addresses, credentials, customer data, or operational IPs in screenshots.

## Project showcase

This platform is a practical example of full-stack product development across backend services, browser automation, API design, interactive JavaScript interfaces, and role-managed operations. It is built to make repetitive workflows easier to run and easier to understand.

For a project discussion, collaboration, or a walkthrough of the implementation, reach out through the contact details on my GitHub profile.
