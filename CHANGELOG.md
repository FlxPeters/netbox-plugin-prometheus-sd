# CHANGELOG

<!-- version list -->

## v1.3.0-pre.1 (2026-03-17)

### Bug Fixes

- Remove further netbox 3.x feature flag
  ([`15f8b0f`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/15f8b0fca0b94e2ddfd6cdbf844f275e4c09bbf3))

### Chores

- Update netbox version in example to 4.4.10
  ([`86397eb`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/86397eb7a68f46776ad91f1f05331bcb9a62f3b9))

- **config**: Configure Python Semantic Release
  ([`458e8aa`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/458e8aa7c10a404294968eba8b24609044d156d5))

- **deps**: Bump tar and npm
  ([`1140fa0`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/1140fa0c8fc7cd2cd79e4f56bdcd070d9bbc88e2))

- **deps-dev**: Bump lodash-es from 4.17.21 to 4.17.23
  ([`d804fae`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/d804faec3b3104ed5895f494ea6a0774db5692ab))

### Continuous Integration

- Update release pipeline
  ([`cc2492b`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/cc2492b33069629195122b489d2e43a6704e5062))

### Features

- Remove netbox 3.x version checks
  ([`06237b6`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/06237b67b14c9e7ff5ffd0ad4657446bf6f69e50))

### Refactoring

- **ci**: Remove nodejs dependecies and use semantic version in python
  ([`bcd7cf5`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/bcd7cf5240ddf083b6774a379f8c8e3b63a074d8))


## v1.2.1 (2026-03-17)

### Bug Fixes

- Adapt tests for netbox 4.2+
  ([`ba360d2`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/ba360d2c2323141e1619d240b39f58f68fd8afb5))

- Backwards compatibility for tests
  ([`23aa662`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/23aa662fd7e8c9bffd80e748e356ed86544aedea))

### Chores

- Refactor invoke to testcontainers in order to remove docker compose dependency
  ([`b49708a`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/b49708a5ce8d9a7a058ce4cc5cac68fa4954e053))

- Remove stale bot
  ([`5ec126b`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/5ec126bbc33ba5ac01653f078d7ca55b492ea8b4))

- Update README.md to match new testcontainers setup
  ([#246](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/pull/246),
  [`b417a63`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/b417a63a5d11a6084525aa712f337e6bc6f8ce09))

- **deps**: Bump actions/cache from 4 to 5
  ([`4ab16e8`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/4ab16e81e7ab478256a1e680d4e89fb14dc47a35))

- **deps**: Bump actions/setup-python from 2 to 6
  ([`edf04c0`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/edf04c0ac739be9c78e2ded67e1067db2514193d))

- **deps-dev**: Bump minimatch from 5.1.6 to 5.1.9
  ([`9d9f22f`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/9d9f22fcacfce0f8af5df2b7eec0e5396e406c5d))

- **docs**: Update login information
  ([#246](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/pull/246),
  [`b417a63`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/b417a63a5d11a6084525aa712f337e6bc6f8ce09))

### Continuous Integration

- Add current latest versions of minor versions to ci
  ([`e067b54`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/e067b544c6c16b26d0e4c332e96457881d2e7d21))

- Add latest supported netbox versions
  ([`23aa662`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/23aa662fd7e8c9bffd80e748e356ed86544aedea))

- Adjust ci to new invoke tasks
  ([`4a5f47c`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/4a5f47c9c2cedd9acc2db7c333d6d1fc6e9e11a9))

- Adjust ci to supported versions
  ([`92dd624`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/92dd624975850189bfe8ee4a35b0978b08feec4a))

- Cache docker images
  ([`a3b64d1`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/a3b64d113d9e2f6f2e2c5c10016719fec574096f))

- Fix docker context restrictions
  ([`430c2f9`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/430c2f97e576b18d9f0c8cefae51fad0c35b958a))

### Documentation

- Adjust readme
  ([`7537958`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/7537958d44897063e01c55af6b3dddfa63de2f27))

### Testing

- Fix broken test utils
  ([`4e13c74`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/4e13c74708596a252ee92ac193ffdedf7d86d78b))


## v1.2.0 (2025-03-25)

### Bug Fixes

- :bug: Fix pip in Dockerfile
  ([`b3e52e8`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/b3e52e86dcee391bef6f17cc4a805a99d6400388))

- Make plugin backwards compatible with pre Netbox 4.2
  ([`b3e52e8`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/b3e52e86dcee391bef6f17cc4a805a99d6400388))

- Netbox 4.2 migrat site => scope for virtual machine clusters
  ([`b3e52e8`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/b3e52e86dcee391bef6f17cc4a805a99d6400388))

### Features

- Upgrade to 4.2 compatibility
  ([`b3e52e8`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/b3e52e86dcee391bef6f17cc4a805a99d6400388))

### Testing

- :white_check_mark: Fix tests and add missing ones for new virtual machine cluster structure
  ([`b3e52e8`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/b3e52e86dcee391bef6f17cc4a805a99d6400388))


## v1.1.2 (2025-03-09)

### Bug Fixes

- Bugfix version to trigger new relase on PyPi
  ([`6d6aa2b`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/6d6aa2b80dcd9159e81867d0a6a5a3463f16e64d))

### Chores

- Adjust version in netbox plugin definiton
  ([`81523b2`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/81523b2374f6f481706a7d7f046bcdde231676c5))

- Remove old pylint annotations
  ([`cc51489`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/cc51489a20d872829e02207a908f9b7e729c35f8))

- Remove pylint and move linter (black, flake8) to pre-commit
  ([`fbec68d`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/fbec68dd57e24530e75195be26c3e687f61feec5))

- **deps-dev**: Bump pylint from 3.1.1 to 3.2.6
  ([`a9ee408`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/a9ee408ac77960d355d525e2bfaf255816523a7c))

- **test**: Remove pylint from invoke tasks
  ([`3f6eb6b`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/3f6eb6bed8c3fbdcc46ba0acdd3f6f41d7f9e483))

### Continuous Integration

- Add netbox versions to ci matrix where test have been broken
  ([`f0cbd02`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/f0cbd027ce0530a1c05a861d9093367299963e27))

- Add the abilty to release on demand
  ([`3ef6264`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/3ef6264f2e4429c4e871ad7e7b020c90dba849cd))

- Add weekly cron schedule
  ([`584dff3`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/584dff3b37cc37d294148f7a91ea784942f3dc50))

- Adjust release pipeline
  ([`cc73d10`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/cc73d10c012ccd33f3fdc954e9360e6875854128))

- Adjust to latest netbox versions
  ([`7ab44ad`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/7ab44ad427eca996c1b0a40aff789dc252d7dde1))

- Adjust version to a placeholder for semantic release
  ([`af91ff1`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/af91ff1039e04b4810025faeaf4aa89f064b4994))

- Fix commitlint action
  ([`6290332`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/62903322523aad48472057f5e019a851aa55766f))

- Move conventional commit checkt to ci pipeline
  ([`1820a8d`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/1820a8ddbb768b1a6ba38cd64875e7fa89ec1e31))

- Refactor semantic-release to pakage.json and add replace plugin
  ([`cbfdea1`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/cbfdea1d93ee15f673d69bc108f05dc119615a11))

### Refactoring

- Apply black rules for code style
  ([`c9e16ef`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/c9e16efbd66fef50ecac7a71289b2ba98e15f3c2))

- Remove bloat from build and test steps
  ([`ef2b36c`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/ef2b36cea1374b90db13683ba8c37d87dffe4ee0))

- **test**: Replace assertDictContainsSubset with local funtion
  ([`632cd8d`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/632cd8d89e9a604dfaca9905dcb1aeade67712d2))

### Testing

- Drop test support for netbox 3.x
  ([`e6af40d`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/e6af40d36787cb1eedeb36ba5b85684531aae5e9))

- Fix docker compose binary path
  ([`c4d44b0`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/c4d44b03c23b86c2e10cecc8616af80c899c237c))


## v1.1.1 (2024-09-17)

### Bug Fixes

- Udate utils.py force rack_u_position to string value.
  ([`20e7e25`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/20e7e25d59fc3b3a670e71a73a9af6b7706a0b1d))

### Continuous Integration

- Enable stale pr and issue bot
  ([`d05857f`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/d05857f35e77bcad8aafd9762d5763cf1f2ae068))

- Trigger pypi publish on tags
  ([`c0b4074`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/c0b4074973cdb89a3aa1cd497b2d75692d6a91ad))


## v1.1.0 (2024-05-23)

### Chores

- Tune commit message on dependabot
  ([`9f29cf6`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/9f29cf63a5e350e777531760664dc9182e6ab6d1))

- **deps**: Bump actions/setup-node from 3 to 4
  ([`68df170`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/68df1706feb910aedcd25d5f10f228ef48bbcf10))

- **deps**: Bump actions/stale from 5 to 9
  ([`2315d1d`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/2315d1d56a2a47daac704dc9db571199ccf0cdd9))

- **deps-dev**: Bump pylint from 3.1.0 to 3.1.1
  ([`b473236`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/b473236a3eab50a2889caa86c5b66d3c1acf3816))

### Continuous Integration

- Add netbox 4.0.2 and latest to ci matrix
  ([`f4dc1ee`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/f4dc1eef24f7164089b0ebe1823594722cbdc59e))

- Remove dry run on relase workflow
  ([`9c12062`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/9c120628646fb2be6b91a1f8acff98b497d32912))

### Features

- Add netbox 4.0 compatible imports
  ([`20606ac`](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/commit/20606aca6cf93709bae203cd1196bf0d1d91913f))


## v1.0.0 (2024-05-08)

- Initial Release
