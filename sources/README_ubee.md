# UPC UBEE WPA2 generator proof-of-concept

Proof of concept code for generating default WPA2 passwords for 
UPC UBEE EBW3226 router with MAC prefix `64:7c:34` and for SSIDs of the form `UPC1234567` (7 digits).

- Proof of concept generator code is [ubee_keys.c](https://github.com/yolosec/upcgen/blob/master/ubee_keys.c) file in C.

## Building it
`gcc -O3 -o ubee_keys ubee_keys.c -lcrypto`

For technical writeup see our [blog post](https://deadcode.me/blog/2016/07/01/UPC-UBEE-EVW3226-WPA2-Reversing.html)
