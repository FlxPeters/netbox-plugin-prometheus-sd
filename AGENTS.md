# AGENTS.md

## What this is

A NetBox plugin that exposes devices, virtual machines, services, and IP addresses
through a Prometheus HTTP service discovery (`http_sd`) compatible API.

## Design principle: reuse NetBox, don't reimplement it

The plugin is a thin layer on top of NetBox's own REST API stack:

- `netbox_prometheus_sd/api/views.py` reuses NetBox's own ViewSets, filtersets, and
  querysets (`Device.objects`, `VirtualMachine.objects`, `Service.objects`,
  `IPAddress.objects`) instead of defining new views or filtering logic. Any filter
  that works on the core NetBox API also works on these endpoints.
- `netbox_prometheus_sd/api/serializers.py` adds Prometheus-shaped serializers
  (`targets` + `labels`) on top of those querysets — this is the only real "new"
  layer the plugin owns.
- `netbox_prometheus_sd/api/utils.py` holds small `extract_*(obj, labels)` helpers,
  one per label group (tenant, cluster, tags, contacts, custom fields, ...), shared
  across the Device/VM/Service/IPAddress serializers.
- `netbox_prometheus_sd/filtersets.py` is the one deliberate exception: it subclasses
  NetBox's `ServiceFilterSet` to add first-level tenancy filtering, which core
  NetBox doesn't offer for services.
- Pagination is disabled on all endpoints (`pagination_class = None`) because
  Prometheus expects the full target list in one response.
- Auth/permissions are NetBox's own object-permission model — no plugin-specific
  auth.

## NetBox version compatibility

The plugin supports the NetBox `4.x` line only (see `.github/workflows/ci.yml` for
the tested matrix). NetBox `3.x` is not supported and new `3.x` fallback code
should not be added.

NetBox's models still change between 4.x minors, so compatibility within the line
is handled two ways:

- **At class-definition time** (queryset construction), via the parsed-version
  constants in `api/utils.py` (`NETBOX_RELEASE_CURRENT`, `NETBOX_RELEASE_41`, ...)
  or a field-existence check.
- **At runtime** (label extraction), via `try`/`except AttributeError`/`FieldError`
  in the `extract_*` helpers and test fixtures.

Known differences that are already shimmed:

- `Cluster.site` became a generic `scope` relation in 4.2 — `extract_cluster()`
  emits `scope`/`scope_slug` labels on 4.2+ and `site`/`site_slug` below that;
  the queryset path differs too (`cluster__scope` vs `cluster__site`).
- `Service.device`/`Service.virtual_machine` became a single generic
  `Service.parent` in 4.3.

Detecting 4.3+ deserves a warning: **`hasattr(Service, "device")` is always true
on every NetBox version** and cannot be used as the check. Device and
VirtualMachine declare `services = GenericRelation(..., related_query_name=...)`,
so `Service.device` always resolves to a read-only reverse accessor. Check
`hasattr(Service, "parent_object_type")` instead, which only exists once `parent`
is a real GenericForeignKey.

When touching model field access, assume any 4.x release may hit the code path,
and check field existence rather than assuming a version.

## Performance

Because pagination is off, a single request serializes the entire device/VM/
service/IP inventory. Query efficiency dominates response time here — an
unprefetched relation touched inside a serializer's `get_labels()` becomes an N+1
across every row, which is what made these endpoints take minutes on real
inventories (issue #265).

Rules of thumb when editing `views.py`:

- Adding a label that reads a related object means adding the matching
  `select_related` (single-valued FKs, one JOIN) or `prefetch_related`
  (reverse/m2m/generic relations, one extra query).
- `Device`/`VirtualMachine` querysets must keep `.annotate_config_context_data()`.
  Without it, `get_config_context()` — called for every row by
  `SDConfigContextDuplicateSerializer` — issues a query per row.
- A GenericForeignKey (`cluster__scope`, `Service.parent`) cannot be
  `select_related`; use `prefetch_related` / `GenericPrefetch`.

## Testing

NetBox plugins can't be tested standalone. Tests are Django unit tests
(`netbox_prometheus_sd/tests/`) executed inside a real NetBox container, spun up
by [testcontainers](https://testcontainers.com/?language=python) from `tasks.py`.
The same tests run locally and in CI — there is no separate integration layer.

```bash
invoke test        # build the image and run the whole suite
invoke build_dev   # start a dev NetBox on http://localhost:8000 and keep it up
```

`NETBOX_VER` selects the NetBox image tag (default `latest`), e.g.
`NETBOX_VER=v4.6.5 invoke test`. Each run builds a throwaway container, so
switching versions needs no manual cleanup.

Note that `assertDictContainsSubset` was removed from `unittest` in Python 3.12;
`tests/utils.py` provides a `dictContainsSubset(subset, fullset)` helper instead.

Every feature or fix needs a test. Fixtures live in
`netbox_prometheus_sd/tests/utils.py` (`build_device_full`, `build_vm_full`, ...)
and should be extended rather than duplicated. Fixture builders that persist
objects take an `ip_octet` argument — pass a unique value per object when a test
creates several, since `primary_ip4`/`primary_ip6` are unique one-to-one fields.

## Commits and releases

This repository follows Conventional Commits, and releases are fully automated by
[python-semantic-release](https://python-semantic-release.readthedocs.io/) — see
`[tool.semantic_release]` in `pyproject.toml` and `.github/workflows/release.yaml`.

That means commit messages directly determine the released version, so they are
not cosmetic:

- `fix:` → patch release
- `feat:` → minor release
- a `BREAKING CHANGE:` footer (or `!` after the type) → major release

The version is written back to `pyproject.toml` and to `__VERSION__` in
`netbox_prometheus_sd/__init__.py` by the release job — don't bump either by hand.
Branches matching `pre/*` publish prereleases.
