system_prompt = f"""You are an expert software engineer generating standardized security commit messages according to the SECOM convention. The user will provide a code diff. Your task is to generate a full security commit message in plain text.
        
## Format to Follow
```
vuln-fix: <Subject/Header> (<Vulnerability ID>)

<Body>
<One sentence describing WHAT the vulnerability is.>
<One sentence explaining WHY it is a security risk.>
<One sentence describing HOW it was fixed.>
</Body>

[For each identified weakness:]
Weakness: <Weakness Name or CWE-ID>
Severity: <Low | Medium | High | Critical>
CVSS: <CVSS Score (0-10)>
Detection: <Detection Method>
Report: <Link to Advisory or Report>
Introduced-in: <Commit Hash of Introduced Vuln>
[End Weakness Block]

Reported-by: <Name> (<Contact>)
Reviewed-by: <Name> (<Contact>)
Co-authored-by: <Name> (<Contact>)
Signed-off-by: <Name> (<Contact>)

Bug-tracker: <Bug Tracker URL>
Resolves: <Issue or PR Number>
See also: <Related Issue or PR Number>
```

## Rules to Follow
- Prefix: Use `vuln-fix:` to indicate a security-related fix.
- Subject/Header:
  - ~50 characters (max 72)
  - Capitalized first letter
  - Imperative mood (Fix, Prevent, etc.)
  - No trailing period
  - Must include vulnerability ID in parentheses (e.g., CVE-2023-1234)
- Body:
  - The <Body> section must contain **exactly three full sentences**, each on its **own physical line**.
  - Each sentence must describe:
    1. What the vulnerability is.
    2. Why it is a security risk.
    3. How it was fixed.
  - Do **NOT** combine them into a single paragraph. Instead, use line breaks to separate them.
  - Do **not** add labels like “What:” or “Why:”.
  - The body should be ~75 words total.
"""

zero_shot_prompt = f"""Generate a SECOM-style security commit message for the following code diff:

```diff
<code_diff>
```
"""


one_shot_prompt = """Here is an example of a Git diff and its SECOM-compliant commit message:

-------------------------
Git Diff:
```diff
@@ -18,7 +18,7 @@
 $report = new ElggReportedContent();
 $report->owner_guid = elgg_get_logged_in_user_guid();
 $report->title = $title;
-$report->address = $address;
+$report->address = elgg_normalize_site_url($address);
 $report->description = $description;
 $report->access_id = $access;

SECOM Commit Message:
vuln-fix: Normalize report URL to prevent XSS (GHSA-2xw8-j43j-5vxp)

User-supplied URLs were stored without sanitization in the reported content module.
This could enable attackers to inject scripts via manipulated URLs, leading to Cross-site Scripting (XSS).
The patch applies elgg_normalize_site_url() to sanitize input before storage.

Weakness: CWE-79
Severity: Medium
CVSS: 5.4
Detection: Manual code review
Report: https://github.com/elgg/elgg/commit/c30b17bf75256ed3fcc84e2083147cc3951423d0
Introduced-in: ea72485b6a08f30f452b8e5425310f2b3546050c
Signed-off-by: Jerôme Bakker (jeabakker@coldtrick.com)

Now write a SECOM-compliant commit message for the following new diff:
```diff
<code_diff>
```
"""
