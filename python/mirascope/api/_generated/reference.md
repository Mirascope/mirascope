# Reference
## health
<details><summary><code>client.health.<a href="src/mirascope/health/client.py">check</a>()</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.health.check()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## traces
<details><summary><code>client.traces.<a href="src/mirascope/traces/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope
from mirascope.api._generated.traces import (
    TracesCreateRequestResourceSpansItem,
    TracesCreateRequestResourceSpansItemScopeSpansItem,
    TracesCreateRequestResourceSpansItemScopeSpansItemSpansItem,
)

client = Mirascope()
client.traces.create(
    resource_spans=[
        TracesCreateRequestResourceSpansItem(
            scope_spans=[
                TracesCreateRequestResourceSpansItemScopeSpansItem(
                    spans=[
                        TracesCreateRequestResourceSpansItemScopeSpansItemSpansItem(
                            trace_id="traceId",
                            span_id="spanId",
                            name="name",
                            start_time_unix_nano="startTimeUnixNano",
                            end_time_unix_nano="endTimeUnixNano",
                        )
                    ],
                )
            ],
        )
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**resource_spans:** `typing.Sequence[TracesCreateRequestResourceSpansItem]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.traces.<a href="src/mirascope/traces/client.py">search</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.traces.search(
    start_time="startTime",
    end_time="endTime",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**start_time:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**end_time:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**query:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**input_messages_query:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**output_messages_query:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**fuzzy_search:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**trace_id:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**span_id:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**model:** `typing.Optional[typing.Sequence[str]]` 
    
</dd>
</dl>

<dl>
<dd>

**provider:** `typing.Optional[typing.Sequence[str]]` 
    
</dd>
</dl>

<dl>
<dd>

**function_id:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**function_name:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**span_name_prefix:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**has_error:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**min_tokens:** `typing.Optional[float]` 
    
</dd>
</dl>

<dl>
<dd>

**max_tokens:** `typing.Optional[float]` 
    
</dd>
</dl>

<dl>
<dd>

**min_duration:** `typing.Optional[float]` 
    
</dd>
</dl>

<dl>
<dd>

**max_duration:** `typing.Optional[float]` 
    
</dd>
</dl>

<dl>
<dd>

**attribute_filters:** `typing.Optional[typing.Sequence[TracesSearchRequestAttributeFiltersItem]]` 
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[float]` 
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[float]` 
    
</dd>
</dl>

<dl>
<dd>

**sort_by:** `typing.Optional[TracesSearchRequestSortBy]` 
    
</dd>
</dl>

<dl>
<dd>

**sort_order:** `typing.Optional[TracesSearchRequestSortOrder]` 
    
</dd>
</dl>

<dl>
<dd>

**root_spans_only:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.traces.<a href="src/mirascope/traces/client.py">gettracedetail</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.traces.gettracedetail(
    trace_id="traceId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**trace_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.traces.<a href="src/mirascope/traces/client.py">getanalyticssummary</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.traces.getanalyticssummary(
    start_time="startTime",
    end_time="endTime",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**start_time:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**end_time:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**function_id:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.traces.<a href="src/mirascope/traces/client.py">listbyfunctionhash</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.traces.listbyfunctionhash(
    hash="hash",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**hash:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[NumberFromString]` 
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[NumberFromString]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.traces.<a href="src/mirascope/traces/client.py">searchbyenv</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.traces.searchbyenv(
    organization_id="organizationId",
    project_id="projectId",
    environment_id="environmentId",
    start_time="startTime",
    end_time="endTime",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**environment_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**start_time:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**end_time:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**query:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**input_messages_query:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**output_messages_query:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**fuzzy_search:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**trace_id:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**span_id:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**model:** `typing.Optional[typing.Sequence[str]]` 
    
</dd>
</dl>

<dl>
<dd>

**provider:** `typing.Optional[typing.Sequence[str]]` 
    
</dd>
</dl>

<dl>
<dd>

**function_id:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**function_name:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**span_name_prefix:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**has_error:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**min_tokens:** `typing.Optional[float]` 
    
</dd>
</dl>

<dl>
<dd>

**max_tokens:** `typing.Optional[float]` 
    
</dd>
</dl>

<dl>
<dd>

**min_duration:** `typing.Optional[float]` 
    
</dd>
</dl>

<dl>
<dd>

**max_duration:** `typing.Optional[float]` 
    
</dd>
</dl>

<dl>
<dd>

**attribute_filters:** `typing.Optional[typing.Sequence[TracesSearchByEnvRequestAttributeFiltersItem]]` 
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[float]` 
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[float]` 
    
</dd>
</dl>

<dl>
<dd>

**sort_by:** `typing.Optional[TracesSearchByEnvRequestSortBy]` 
    
</dd>
</dl>

<dl>
<dd>

**sort_order:** `typing.Optional[TracesSearchByEnvRequestSortOrder]` 
    
</dd>
</dl>

<dl>
<dd>

**root_spans_only:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.traces.<a href="src/mirascope/traces/client.py">gettracedetailbyenv</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.traces.gettracedetailbyenv(
    organization_id="organizationId",
    project_id="projectId",
    environment_id="environmentId",
    trace_id="traceId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**environment_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**trace_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## docs
<details><summary><code>client.docs.<a href="src/mirascope/docs/client.py">openapi</a>()</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.docs.openapi()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## organizations
<details><summary><code>client.organizations.<a href="src/mirascope/organizations/client.py">list</a>()</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organizations.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organizations.<a href="src/mirascope/organizations/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organizations.create(
    name="name",
    slug="slug",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name:** `str` — a string at most 100 character(s) long
    
</dd>
</dl>

<dl>
<dd>

**slug:** `str` — a string matching the pattern ^[a-z0-9][a-z0-9_-]*[a-z0-9]$
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organizations.<a href="src/mirascope/organizations/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organizations.get(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organizations.<a href="src/mirascope/organizations/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organizations.update(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — a string at most 100 character(s) long
    
</dd>
</dl>

<dl>
<dd>

**slug:** `typing.Optional[str]` — a string matching the pattern ^[a-z0-9][a-z0-9_-]*[a-z0-9]$
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organizations.<a href="src/mirascope/organizations/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organizations.delete(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organizations.<a href="src/mirascope/organizations/client.py">routerbalance</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organizations.routerbalance(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organizations.<a href="src/mirascope/organizations/client.py">createpaymentintent</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organizations.createpaymentintent(
    id="id",
    amount=1.1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**amount:** `float` — a positive number
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organizations.<a href="src/mirascope/organizations/client.py">subscription</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organizations.subscription(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organizations.<a href="src/mirascope/organizations/client.py">previewsubscriptionchange</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organizations.previewsubscriptionchange(
    id="id",
    target_plan="free",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**target_plan:** `OrganizationsPreviewSubscriptionChangeRequestTargetPlan` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organizations.<a href="src/mirascope/organizations/client.py">updatesubscription</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organizations.updatesubscription(
    id="id",
    target_plan="free",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**target_plan:** `OrganizationsUpdateSubscriptionRequestTargetPlan` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organizations.<a href="src/mirascope/organizations/client.py">cancelscheduleddowngrade</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organizations.cancelscheduleddowngrade(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## organization-invitations
<details><summary><code>client.organization_invitations.<a href="src/mirascope/organization_invitations/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organization_invitations.list(
    organization_id="organizationId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organization_invitations.<a href="src/mirascope/organization_invitations/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organization_invitations.create(
    organization_id="organizationId",
    recipient_email="recipientEmail",
    role="ADMIN",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**recipient_email:** `str` — a string matching the pattern ^[^ \t\n\r\f\v@]+@[^ \t\n\r\f\v@]+[.][^ \t\n\r\f\v@]+$
    
</dd>
</dl>

<dl>
<dd>

**role:** `OrganizationInvitationsCreateRequestRole` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organization_invitations.<a href="src/mirascope/organization_invitations/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organization_invitations.get(
    organization_id="organizationId",
    invitation_id="invitationId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**invitation_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organization_invitations.<a href="src/mirascope/organization_invitations/client.py">resend</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organization_invitations.resend(
    organization_id="organizationId",
    invitation_id="invitationId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**invitation_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organization_invitations.<a href="src/mirascope/organization_invitations/client.py">revoke</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organization_invitations.revoke(
    organization_id="organizationId",
    invitation_id="invitationId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**invitation_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organization_invitations.<a href="src/mirascope/organization_invitations/client.py">accept</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organization_invitations.accept(
    token="token",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**token:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## organization-memberships
<details><summary><code>client.organization_memberships.<a href="src/mirascope/organization_memberships/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organization_memberships.list(
    organization_id="organizationId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organization_memberships.<a href="src/mirascope/organization_memberships/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organization_memberships.delete(
    organization_id="organizationId",
    member_id="memberId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**member_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organization_memberships.<a href="src/mirascope/organization_memberships/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.organization_memberships.update(
    organization_id="organizationId",
    member_id="memberId",
    role="ADMIN",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**member_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**role:** `OrganizationMembershipsUpdateRequestRole` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## projects
<details><summary><code>client.projects.<a href="src/mirascope/projects/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.projects.list(
    organization_id="organizationId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.projects.<a href="src/mirascope/projects/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.projects.create(
    organization_id="organizationId",
    name="name",
    slug="slug",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — a string at most 100 character(s) long
    
</dd>
</dl>

<dl>
<dd>

**slug:** `str` — a string matching the pattern ^[a-z0-9][a-z0-9_-]*[a-z0-9]$
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.projects.<a href="src/mirascope/projects/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.projects.get(
    organization_id="organizationId",
    project_id="projectId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.projects.<a href="src/mirascope/projects/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.projects.update(
    organization_id="organizationId",
    project_id="projectId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — a string at most 100 character(s) long
    
</dd>
</dl>

<dl>
<dd>

**slug:** `typing.Optional[str]` — a string matching the pattern ^[a-z0-9][a-z0-9_-]*[a-z0-9]$
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.projects.<a href="src/mirascope/projects/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.projects.delete(
    organization_id="organizationId",
    project_id="projectId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## project-memberships
<details><summary><code>client.project_memberships.<a href="src/mirascope/project_memberships/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.project_memberships.list(
    organization_id="organizationId",
    project_id="projectId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.project_memberships.<a href="src/mirascope/project_memberships/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.project_memberships.create(
    organization_id="organizationId",
    project_id="projectId",
    member_id="memberId",
    role="ADMIN",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**member_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**role:** `ProjectMembershipsCreateRequestRole` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.project_memberships.<a href="src/mirascope/project_memberships/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.project_memberships.get(
    organization_id="organizationId",
    project_id="projectId",
    member_id="memberId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**member_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.project_memberships.<a href="src/mirascope/project_memberships/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.project_memberships.delete(
    organization_id="organizationId",
    project_id="projectId",
    member_id="memberId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**member_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.project_memberships.<a href="src/mirascope/project_memberships/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.project_memberships.update(
    organization_id="organizationId",
    project_id="projectId",
    member_id="memberId",
    role="ADMIN",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**member_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**role:** `ProjectMembershipsUpdateRequestRole` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## environments
<details><summary><code>client.environments.<a href="src/mirascope/environments/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.environments.list(
    organization_id="organizationId",
    project_id="projectId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.environments.<a href="src/mirascope/environments/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.environments.create(
    organization_id="organizationId",
    project_id="projectId",
    name="name",
    slug="slug",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — a string at most 100 character(s) long
    
</dd>
</dl>

<dl>
<dd>

**slug:** `str` — a string matching the pattern ^[a-z0-9][a-z0-9_-]*[a-z0-9]$
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.environments.<a href="src/mirascope/environments/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.environments.get(
    organization_id="organizationId",
    project_id="projectId",
    environment_id="environmentId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**environment_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.environments.<a href="src/mirascope/environments/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.environments.update(
    organization_id="organizationId",
    project_id="projectId",
    environment_id="environmentId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**environment_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — a string at most 100 character(s) long
    
</dd>
</dl>

<dl>
<dd>

**slug:** `typing.Optional[str]` — a string matching the pattern ^[a-z0-9][a-z0-9_-]*[a-z0-9]$
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.environments.<a href="src/mirascope/environments/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.environments.delete(
    organization_id="organizationId",
    project_id="projectId",
    environment_id="environmentId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**environment_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.environments.<a href="src/mirascope/environments/client.py">getanalytics</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.environments.getanalytics(
    organization_id="organizationId",
    project_id="projectId",
    environment_id="environmentId",
    start_time="startTime",
    end_time="endTime",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**environment_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**start_time:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**end_time:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## apiKeys
<details><summary><code>client.api_keys.<a href="src/mirascope/api_keys/client.py">api_keys_list_all_for_org</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.api_keys.api_keys_list_all_for_org(
    organization_id="organizationId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.api_keys.<a href="src/mirascope/api_keys/client.py">api_keys_list</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.api_keys.api_keys_list(
    organization_id="organizationId",
    project_id="projectId",
    environment_id="environmentId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**environment_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.api_keys.<a href="src/mirascope/api_keys/client.py">api_keys_create</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.api_keys.api_keys_create(
    organization_id="organizationId",
    project_id="projectId",
    environment_id="environmentId",
    name="name",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**environment_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — a string at most 100 character(s) long
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.api_keys.<a href="src/mirascope/api_keys/client.py">api_keys_get</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.api_keys.api_keys_get(
    organization_id="organizationId",
    project_id="projectId",
    environment_id="environmentId",
    api_key_id="apiKeyId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**environment_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**api_key_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.api_keys.<a href="src/mirascope/api_keys/client.py">api_keys_delete</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.api_keys.api_keys_delete(
    organization_id="organizationId",
    project_id="projectId",
    environment_id="environmentId",
    api_key_id="apiKeyId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**environment_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**api_key_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## functions
<details><summary><code>client.functions.<a href="src/mirascope/functions/client.py">list</a>()</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.functions.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.functions.<a href="src/mirascope/functions/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.functions.create(
    code="code",
    hash="hash",
    signature="signature",
    signature_hash="signatureHash",
    name="name",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**code:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**hash:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**signature:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**signature_hash:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**tags:** `typing.Optional[typing.Sequence[str]]` 
    
</dd>
</dl>

<dl>
<dd>

**metadata:** `typing.Optional[typing.Dict[str, typing.Optional[str]]]` 
    
</dd>
</dl>

<dl>
<dd>

**dependencies:** `typing.Optional[
    typing.Dict[str, typing.Optional[FunctionsCreateRequestDependenciesValue]]
]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.functions.<a href="src/mirascope/functions/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.functions.get(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.functions.<a href="src/mirascope/functions/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.functions.delete(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.functions.<a href="src/mirascope/functions/client.py">findbyhash</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.functions.findbyhash(
    hash="hash",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**hash:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.functions.<a href="src/mirascope/functions/client.py">getbyenv</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.functions.getbyenv(
    organization_id="organizationId",
    project_id="projectId",
    environment_id="environmentId",
    function_id="functionId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**environment_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**function_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.functions.<a href="src/mirascope/functions/client.py">listbyenv</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.functions.listbyenv(
    organization_id="organizationId",
    project_id="projectId",
    environment_id="environmentId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**environment_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## annotations
<details><summary><code>client.annotations.<a href="src/mirascope/annotations/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.annotations.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**otel_trace_id:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**otel_span_id:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**label:** `typing.Optional[AnnotationsListRequestLabel]` 
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[NumberFromString]` 
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[NumberFromString]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.annotations.<a href="src/mirascope/annotations/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.annotations.create(
    otel_span_id="otelSpanId",
    otel_trace_id="otelTraceId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**otel_span_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**otel_trace_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**label:** `typing.Optional[AnnotationsCreateRequestLabel]` 
    
</dd>
</dl>

<dl>
<dd>

**reasoning:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**metadata:** `typing.Optional[typing.Dict[str, typing.Optional[typing.Any]]]` 
    
</dd>
</dl>

<dl>
<dd>

**tags:** `typing.Optional[typing.Sequence[str]]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.annotations.<a href="src/mirascope/annotations/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.annotations.get(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.annotations.<a href="src/mirascope/annotations/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.annotations.update(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**label:** `typing.Optional[AnnotationsUpdateRequestLabel]` 
    
</dd>
</dl>

<dl>
<dd>

**reasoning:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**metadata:** `typing.Optional[typing.Dict[str, typing.Optional[typing.Any]]]` 
    
</dd>
</dl>

<dl>
<dd>

**tags:** `typing.Optional[typing.Sequence[str]]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.annotations.<a href="src/mirascope/annotations/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.annotations.delete(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## tags
<details><summary><code>client.tags.<a href="src/mirascope/tags/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.tags.list(
    organization_id="organizationId",
    project_id="projectId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.tags.<a href="src/mirascope/tags/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.tags.create(
    organization_id="organizationId",
    project_id="projectId",
    name="name",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — a string at most 100 character(s) long
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.tags.<a href="src/mirascope/tags/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.tags.get(
    organization_id="organizationId",
    project_id="projectId",
    tag_id="tagId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**tag_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.tags.<a href="src/mirascope/tags/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.tags.update(
    organization_id="organizationId",
    project_id="projectId",
    tag_id="tagId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**tag_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — a string at most 100 character(s) long
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.tags.<a href="src/mirascope/tags/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope

client = Mirascope()
client.tags.delete(
    organization_id="organizationId",
    project_id="projectId",
    tag_id="tagId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**organization_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**tag_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## token-cost
<details><summary><code>client.token_cost.<a href="src/mirascope/token_cost/client.py">calculate</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from mirascope.api._generated import Mirascope
from mirascope.api._generated.token_cost import TokenCostCalculateRequestUsage

client = Mirascope()
client.token_cost.calculate(
    provider="provider",
    model="model",
    usage=TokenCostCalculateRequestUsage(
        input_tokens=1.1,
        output_tokens=1.1,
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**provider:** `str` — a non empty string
    
</dd>
</dl>

<dl>
<dd>

**model:** `str` — a non empty string
    
</dd>
</dl>

<dl>
<dd>

**usage:** `TokenCostCalculateRequestUsage` 
    
</dd>
</dl>

<dl>
<dd>

**via_router:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

