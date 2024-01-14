#!/usr/bin/env python3
import sys
with open(sys.argv[1], "w") as fp:
    fp.write("import json\nfrom jsonschema import RefResolver, Draft7Validator\n\n")
    fp.write("# DO NOT EDIT THIS FILE - IT IS AUTO-GENERATED BY build.py\n")
    fp.write("# TO CHANGE A SCHEMA, EDIT THE CORRESPONDING .schema FILE\n")
    fp.write("# AND RUN make schemas OR make all IN THE src DIRECTORY.\n")
    for schemaFname in sys.argv[2:]:
        fp.write("_" + schemaFname + 'Schema = json.loads("""')
        with open("schema/" + schemaFname + ".schema", "r") as sfp:
            for line in sfp:
                fp.write(' ' + line.strip() + ' ')
        fp.write('""")\n')
        fp.write("_" + schemaFname + "Schema['$id'] = 'https://example.com/"
                 "schemas/" + schemaFname + "'\n")
    fp.write("_schemaStore = {")
    for schemaFname in sys.argv[2:]:
        fp.write("_{0:s}Schema['$id']: _{0:s}Schema,".format(schemaFname))
    fp.write('}\n')

    for schemaFname in sys.argv[2:]:
        fp.write(("_{0:s}Resolver = RefResolver.from_schema("
                 "_{0:s}Schema, store=_schemaStore)\n").format(schemaFname))
    fp.write("\n\n")
    for schemaFname in sys.argv[2:]:
        fp.write("{0:s} = Draft7Validator(_{0:s}Schema, resolver=_{0:s}Resolver)\n".format(
                 schemaFname))
    fp.write("schemaMap = {")
    for schemaFname in sys.argv[2:]:
        fp.write('"{0:s}": {0:s},'.format(schemaFname))
    fp.write('}\n')