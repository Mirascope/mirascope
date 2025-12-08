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

**id:** `str` — Organization ID
    
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

