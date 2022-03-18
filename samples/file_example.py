from fetchbim import File

# fl = File.pick_file("FamilyImageLarge")
files = File.search(key="MaterialLibrary", name="PNC")
_file = files[0]
# print(_file.name, _file.key)
# response = _file.attach_to_families(
#     ["52607912-488f-450d-b1bc-9332c03e89a5", "bbda77a5-7ea8-4439-aa6a-bf7f347e277b"]
# )
response = _file.get_mappings()
print(response)

all_mappings = File.get_all_mappings()
for mapping in all_mappings:
    print(mapping)
