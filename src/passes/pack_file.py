"""pack_file pass: encrypt the WHOLE file, prepend a mini loader.

Output = loader stub + one encrypted blob. The stub decrypts (XOR-hex, key 0x5A)
and runs the code via Function(). Output is identified by the __forge_packed_v1 tag
so loaders can detect packed payloads and handle mustContain checks accordingly.

NOTE: markers hidden inside the blob are invisible to text scans. If a loader
checks mustContain on fetched text, it must unpack first (or check the tag).
Keep markers as identifiers in UNPACKED code; pack_file is always the LAST pass.
"""

TAG = "__forge_packed_v1"
STUB = ("//" + TAG + "\nvar __F=function(s){var o='',i=0;for(;i<s.length;i+=2)"
        "{o+=String.fromCharCode(parseInt(s.substr(i,2),16)^0x5A);}return o;};"
        "Function(__F(\"")


def run(code: str) -> str:
    if TAG in code:
        return code
    blob = "".join("%02x" % (ord(ch) ^ 0x5A) for ch in code)
    return STUB + blob + "\"))();\n"
