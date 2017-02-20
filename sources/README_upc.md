# upc_keys.c with custom prefix support and Lambda sauce

This is Peter "blasty" Geissler's [original upc_keys.c](https://haxx.in/upc_keys.c), modified to support custom prefixes. The output is also more machine-readable. This is what powers my [passphrase recovery tool for `UPC1234567` devices](https://upc.michalspacek.cz/).

## Building it
`gcc -O3 -o upc_keys upc_keys.c -lcrypto`

## Using it
`upc_keys <ESSID> <PREFIXES>`

Where:

- `<ESSID>` should be in `UPCxxxxxxx` format
- `<PREFIXES>` should be a string of comma separated serial number prefixes
