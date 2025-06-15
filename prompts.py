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


one_shot_prompt = """Here is an example of a Git diff and its SECOM-compliant commit message.

Git Diff:
```diff
@@ -18,7 +18,7 @@
 $report = new ElggReportedContent();
 $report->url = get_input('url');
 $report->title = get_input('title');
-$report->description = get_input('description');
+$report->description = htmlspecialchars(get_input('description'), ENT_QUOTES, 'UTF-8');
 $report->address = get_input('address');
 $report->reported_by_guid = elgg_get_logged_in_user_guid();
 $report->time_created = time();
```

SECOM Commit Message:
vuln-fix: Sanitize description in report form to prevent XSS (GHSA-2xw8-j43j-5vxp)

The report submission form failed to sanitize user-supplied descriptions before rendering them.  
This allowed malicious users to inject HTML or JavaScript, leading to potential Cross-site Scripting (XSS) attacks.  
The patch escapes the description input using `htmlspecialchars` to safely encode special characters.

Weakness: CWE-79  
Severity: Medium  
CVSS: 5.4

Use:
Vulnerability ID: {vuln_id}
CWE: {cwe_id}
Commit Author: {author}
Commit Date: {commit_datetime}
Commit Message: {commit_message}
Co-authors: {coauthors}
Only include optional metadata fields (Reported-by, Reviewed-by, Co-authored-by, Signed-off-by, Bug-tracker, Resolves, See also) if and only if they are explicitly present in the provided metadata.
Do not fabricate, infer, or insert placeholders for missing fields.
Git Diff:
```diff
{code_diff}
```
"""