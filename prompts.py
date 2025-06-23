system_prompt_short = f"""You are an expert software engineer generating standardized security commit messages according to the SECOM convention. The user will provide a code diff. Your task is to generate a full security commit message in plain text.

Only include fields if the required information is explicitly provided; otherwise avoid the data.
**Do not fabricate or assume values**. If uncertain, avoid including the data field.

## Format to Follow
```

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

```

## Rules to Follow
- Subject/Header:
  - ~50 characters (max 72)
  - Capitalized first letter
  - Imperative mood (Fix, Prevent, etc.)
  - No trailing period
  - Must include specific vulnerability ID for each case in parentheses 
- Body:
  - The <Body> section must contain **exactly three full sentences**, each on its **own physical line**.
  - Each sentence must describe:
    1. What the vulnerability is.
    2. Why it is a security risk.
    3. How it was fixed.
  - Do **NOT** combine them into a single paragraph. Instead, use line breaks to separate them.
  - Do **not** add labels like "What:" or "Why:".
  - The body should be ~75 words total.
"""

system_prompt = f"""You are an expert software engineer generating standardized security commit messages according to the SECOM convention. The user will provide a code diff. Your task is to generate a full security commit message in plain text.
Only include fields if the required information is explicitly provided; otherwise avoid the data.
**Do not fabricate or assume values**. If uncertain, avoid including the data field.
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
  - Must include specific vulnerability ID for each case in parentheses
- Body:
  - The <Body> section must contain **exactly three full sentences**, each on its **own physical line**.
  - Each sentence must describe:
    1. What the vulnerability is.
    2. Why it is a security risk.
    3. How it was fixed.
  - Do **NOT** combine them into a single paragraph. Instead, use line breaks to separate them.
  - Do **not** add labels like “What:” or “Why:“.
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
vuln-fix: Sanitize report address using site URL normalization (GHSA-2xw8-j43j-5vxp)

The reported content form previously accepted raw address input without sanitization or normalization.  
This could allow attackers to inject malicious or malformed URLs, potentially leading to security issues such as phishing or open redirects.  
The patch mitigates this by applying Elgg's built-in `elgg_normalize_site_url()` function to sanitize the address input.

Weakness: CWE-79  
Severity: Medium  
CVSS: 5.4


Only include optional metadata fields (Reported-by, Reviewed-by, Co-authored-by, Signed-off-by, Bug-tracker, Resolves, See also) if and only if they are explicitly present in the provided metadata.
Do not fabricate, infer, or insert placeholders for missing fields.
Git Diff:
```diff
{code_diff}
```
"""


few_shot_prompt = """Here are three examples of Git diffs and their corresponding SECOM-style commit messages.

Example 1
Git Diff:
```diff
@@ -87,7 +87,17 @@ class BinaryOp : public BinaryOpShared {

   void Compute(OpKernelContext* ctx) override {
     const Tensor& input_0 = ctx->input(0);
+    OP_REQUIRES(ctx, input_0.dtype() == DataTypeToEnum<Tin>::v(),
+                errors::InvalidArgument(
+                    "Expected tensor of type ",
+                    DataTypeString(DataTypeToEnum<Tin>::v()), " but got type ",
+                    DataTypeString(input_0.dtype())));
     const Tensor& input_1 = ctx->input(1);
+    OP_REQUIRES(ctx, input_1.dtype() == DataTypeToEnum<Tin>::v(),
+                errors::InvalidArgument(
+                    "Expected tensor of type ",
+                    DataTypeString(DataTypeToEnum<Tin>::v()), " but got type ",
+                    DataTypeString(input_1.dtype())));
     const Device& eigen_device = ctx->eigen_device<Device>();
```
Expected Output:
The binary operation function did not verify that input tensor types matched the expected type, allowing malformed SavedModel inputs to cause type confusion.
This led to runtime crashes via CHECK failures when mismatched types were interpreted incorrectly, resulting in denial-of-service scenarios.
The patch validates that both input tensors match the expected data type using TensorFlow's OP_REQUIRES and DataTypeToEnum checks.

Weakness: CWE-617
Severity: Medium
CVSS: 6.5

# CWE-617 is used because the patch prevents reachable assertion failures caused by inconsistent internal tensor states, a form of type confusion exploitable for denial of service.

Example 2
Git Diff:
```diff
@@ -18,7 +18,7 @@
 $report = new ElggReportedContent();
 $report->owner_guid = elgg_get_logged_in_user_guid();
 $report->title = $title;
-$report->address = $address;
+$report->address = elgg_normalize_site_url($address);
 $report->description = $description;
```
Expected Output:
The report submission form failed to sanitize user-supplied addresses before saving them.
This allowed attackers to inject malicious or malformed URLs for redirection or phishing.
The patch applies elgg_normalize_site_url to clean the input before storage.

Weakness: CWE-79
Severity: Medium
CVSS: 5.4

# CWE-79 is appropriate because unsanitized user input is injected into the web context,
# enabling potential cross-site scripting (XSS) attacks.

Example 3
Git Diff:
```diff
@@ -157,35 +157,37 @@ template <KernelType kernel_type, typename OpType>
 TfLiteStatus Eval(TfLiteContext* context, TfLiteNode* node) {
   OpContext op_context(context, node);
...
+  if (NumElements(op_context.input1) == 0 ||
+      NumElements(op_context.input2) == 0) {
+    return kTfLiteOk;
+  }
```
Expected Output:
The implementation did not check for empty input tensors before accessing their data.
This could cause out-of-bounds memory reads, leading to crashes or information leaks.
The patch short-circuits execution when any input tensor is empty.

Weakness: CWE-125
Severity: Low
CVSS: 2.5

# CWE-125 applies because the patch prevents reading beyond array/tensor bounds
# by checking if input arrays are empty.

Example 4
Git Diff:
```diff
@@ -152,6 +152,7 @@ public static function delete(int $id): void
     public static function deleteData(array $ids): void
     {
         $database = BackendModel::getContainer()->get('database');
+        $ids = array_map('intval', $ids);

         $database->delete('forms_data', 'id IN(' . implode(',', $ids) . ')');
         $database->delete('forms_data_fields', 'data_id IN(' . implode(',', $ids) . ')');
```
Expected Output:
The original implementation directly inserted raw input from the ids array into a SQL IN() clause.
This allowed attackers to inject malicious values via the URL or request body, potentially manipulating or leaking database records.
The patch mitigates this by sanitizing each ID using array_map('intval', $ids) to ensure only integers are passed into the query.

Weakness: CWE-89
Severity: High
CVSS: 7.5

# CWE-89 is used because the patch prevents SQL injection by converting untrusted array input into integers before embedding it into SQL.

Example 5
Git Diff:
```diff
@@ -341,6 +341,8 @@ public FormValidation doValidateProxy(
                 @QueryParameter("userName") String userName, @QueryParameter("password") String password,
                 @QueryParameter("noProxyHost") String noProxyHost) {

+            Jenkins.getInstance().checkPermission(Jenkins.ADMINISTER);
+
             if (Util.fixEmptyAndTrim(testUrl) == null) {
                 return FormValidation.error(Messages.ProxyConfiguration_TestUrlRequired());
             }
```
Expected Output:
The proxy validation method allowed any user to trigger server-side HTTP requests without restriction.
This enabled potential SSRF attacks by letting untrusted users probe internal systems or exfiltrate metadata via crafted test URLs.
The patch introduces a permission check to ensure only administrators can initiate proxy validation.

Weakness: CWE-918
Severity: Medium
CVSS: 5.3

# CWE-918 is used because the patch restricts internal server requests that could otherwise be controlled by external input — a classic server-side request forgery vector.


The above examples illustrate how to generate SECOM-style commit messages for different types of vulnerabilities.
Now, based on the following code diff, generate a new commit message that adapts to the specific weakness it addresses—even if it differs from the examples above. Use the same structure, but reason from the patch content and generate the appropriate vulnerability classification and risk summary.
Do not fabricate, infer, or insert placeholders for missing fields.
When generating your response, carefully analyze the vulnerability pattern in the code diff.
Choose the most appropriate CWE classification based on what the patch fixes.
Use this list of patterns and their CWE mappings to guide your choice:

When generating your response, analyze the code diff and infer the type of vulnerability the patch is addressing.
Use this guide to choose the correct CWE. 
CWE Mapping Reference:

- **CWE-617: Reachable Assertion / Denial of Service via Internal Checks**
  Use if the patch guards against **internal inconsistencies** or **undefined behavior**, not input.
  Examples:
  - Preventing `CHECK` or `assert` failures
  - Fixing crashes due to type mismatches (e.g. casting wrong tensor dtype)
  - Fixing race conditions between threads or users
  Do not use CWE-617 for simple input validation — use CWE-20 instead.

- **CWE-20: Improper Input Validation**  
  Use if the patch **adds checks that reject malformed, incomplete, or out-of-range user input**.  
  These are "front-door" filters that **prevent bad input from propagating** into internal logic.
  Examples:
  - Checking if a string is null or empty
  - Enforcing tensor shape or dimension requirements
  - Verifying a number falls within an allowed range
  Do not use CWE-20 if the patch handles type confusion or assertion failures in core logic.
  That would be CWE-617.

- **CWE-79: Cross-site Scripting (XSS)**  
  Use if the patch sanitizes or encodes **user-controlled content** that is rendered in HTML.  
  Examples: escaping `<script>`, `onerror=`, HTML encoding, using `htmlspecialchars()`.

- **CWE-89: SQL Injection**  
  Use if the patch prevents **user input from altering SQL queries**.  
  Examples: switching to parameterized queries, escaping input passed to SQL, sanitizing dynamic WHERE clauses.

- **CWE-125: Out-of-bounds Read**  
  Use if the patch prevents reading **outside valid array, buffer, or tensor bounds**.  
  Examples: validating index access, checking length before reading from memory.

- **CWE-787: Out-of-bounds Write**  
  Use if the patch prevents **writing past array or memory buffer bounds**.  
  Examples: size checks before memory copy, preventing buffer overflow writes.

- **CWE-203: Information Exposure Through Debug Messages**  
  Use if the patch **removes, redacts, or restricts verbose error messages or debug output**.  
  Examples: replacing stack traces or internal paths with generic messages.

- **CWE-311: Missing Encryption of Sensitive Data**  
  Use **only** if the patch **encrypts sensitive data** during storage or transmission.
  Examples:
  - Switching from HTTP to HTTPS
  - Encrypting API tokens, credentials, or session data
  - Adding TLS to database or network communication
  Do **not** use CWE-311 if the patch blocks or disables unauthorized endpoints or insecure ports — that's CWE-300.


- **CWE-285: Improper Authorization**  
  Use if the patch adds a **missing permission check unrelated to external requests or network access**.  
  Example use cases:
  - Access to admin pages
  - Role checks for deleting user data
  - Guarding sensitive internal resources

- **CWE-863: Incorrect Authorization**  
  Use if the patch **fixes broken or misapplied authorization logic**.  
  Examples: correcting the wrong role check, fixing logic that let unauthorized users access resources.

- **CWE-601: Open Redirect**  
  Use if the patch **prevents user input from controlling redirect URLs**.  
  Examples: patch introduces allowlist for redirect targets or replaces dynamic redirects with fixed values.

- **CWE-918: Server-Side Request Forgery (SSRF)**  
  Use if the patch **restricts access to server-side URL fetches or validations** that could be exploited by attackers.  
  Typical indicators:
  - Validation on proxy config, image fetch, or test URL handlers.
  - Protection against internal IP ranges or unauthenticated requests causing outgoing traffic.
  Even if the patch uses `checkPermission()` to restrict access to an SSRF vector, this is **still CWE-918**, not CWE-285, because the risk is due to **server-side request behavior**, not generic permission logic.

- **CWE-300: Channel Accessible by Non-Endpoint**  
  Use if the patch **prevents unauthorized or unintended communication channels** from being used.
  Examples:
  - Blocking plain TCP access to a backend-only port
  - Rejecting unencrypted connections entirely
  - Preventing access to control interfaces from external networks
  This CWE is about restricting **who can reach a communication channel**, not encrypting the data.
  Do **not** use CWE-311 unless the patch actually **adds encryption**.


If no CWE is evident from the patch, **omit** the Weakness block entirely.
Your goal is to match the structure shown in the examples and **accurately classify the vulnerability type based on patch intent and risk**.
Do not guess or fabricate. If the correct CWE is unclear, omit the Weakness block entirely.
Do not include additional # comments on why the weakness choice is appropiate as it does not follow the SECOM standard.
**Important**: Do not classify patches like this as CWE-20 unless they directly validate user-supplied input such as request parameters, external strings, or file formats.  
If the patch prevents type mismatch, assertion failure, or CHECK crash due to internal state assumptions, classify it as CWE-617 instead.

### CVSS & Severity Inference Guide

Estimate the **Severity** and **CVSS Score** based on the patch's context using these general principles from the CVSS v3.1 standard.

#### Attack Vector (AV)
- **Network (N)**: Input comes from HTTP/web, API, remote client
- **Local (L)**: Requires access to the server, file, or runtime
- **Physical (P)**: Requires physical device access

#### Attack Complexity (AC)
- **Low (L)**: No special setup — any attacker can trigger it
- **High (H)**: Requires specific timing, conditions, or crafted environment

#### Privileges Required (PR)
- **None (N)**: No login needed (e.g., web form)
- **Low (L)**: Requires user account
- **High (H)**: Requires admin/root

#### User Interaction (UI)
- **None (N)**: Exploit happens automatically
- **Required (R)**: Victim must click/link/do something

#### Scope (S)
- **Unchanged (U)**: Affects same system/component
- **Changed (C)**: Crosses privilege or system boundaries

#### Impact Ratings
- **Confidentiality (C)**: Can read data (L = partial, H = full)
- **Integrity (I)**: Can alter data or behavior
- **Availability (A)**: Can crash, slow down, or block service

### CVSS Score Interpretation

| Severity | Typical CVSS Range | Use When… |
|----------|---------------------|-----------|
| Low      | 0.1 – 3.9           | Minor info leaks, edge case DoS |
| Medium   | 4.0 – 6.9           | XSS, SSRF, validation issues |
| High     | 7.0 – 8.9           | SQLi, logic flaws, broken auth |
| Critical | 9.0 – 10.0          | RCE, full compromise, pre-auth |

### Instructions
- Carefully **infer the CVSS score and severity** by analyzing the impact and exploitability described by the patch.
- Do not guess or fabricate. Only assign high/critical if justified by the patch context (e.g., remote, unauthenticated, full control).
- If unsure, choose a **conservative (lower)** rating.


Git Diff:
```diff
{code_diff}
```
"""