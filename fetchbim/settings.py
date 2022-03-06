import os


DEV_KEY = os.environ.get("DEV_KEY")
BIMSERVICE_KEY = os.environ.get("BIMSERVICE_KEY")
NOTION_KEY = os.environ.get("NOTION_KEY")
BIM_KEY = os.environ.get("BIM_KEY")
TEAMS_WEBHOOK = os.environ.get("TEAMS_WEBHOOK")


# SSGBIM
BIM_BASE_URL = "https://www.ssgbim.com/api/"
POST_FAMILY = BIM_BASE_URL + "v2/Family/"
UPDATE_FAMILY = BIM_BASE_URL + "Family"
GET_FAMILY = BIM_BASE_URL + "Home/Family/{}"
GET_FULL_FAMILY = BIM_BASE_URL + "v2/Home/Family/{}"
DELETE_FAMILY = BIM_BASE_URL + "Family/{}"
RESTORE_FAMILY = BIM_BASE_URL + "/Family/{}/Restore"
ALL_SHARED_FILES = BIM_BASE_URL + "SharedFiles"
GET_SHARED_FILE = BIM_BASE_URL + "SharedFile/{}"
QUERY_FAMILIES = GET_SHARED_FILE.format("Families")

BIM_HEADERS = {
    "Authorization": "Bearer {}".format(BIM_KEY),
    "Content-Type": "application/json",
}

BOUNDING_BOX_ID = "8c7feebe-76c9-4374-a997-8c53bc1d13ef"
BOUNDING_BOX_TYPE_ID = "124b350f-f719-4ef3-81ab-da3423dca1eb"

# BIMSERVICE
BS_BASE_URL = "https://bimservice.ssgbim.com/api/"
BS_GET_ALL_FAMILIES = BS_BASE_URL + "Families/All"
BS_GET_PUBLIC_FAMILIES = BS_BASE_URL + "Families/"
BS_GET_PAGE = BS_BASE_URL + "Family/{}"

BS_HEADERS = {
    "Authorization": "Bearer {}".format(BIMSERVICE_KEY),
    "Content-Type": "application/json",
}

# DEV
DEV_BASE_URL = "https://fetch.devssg.com/api/"
DEV_UPDATE = DEV_BASE_URL + "Family"
DEV_POST_FAMILY = DEV_BASE_URL + "v2/Family/"
DEV_GET_FAMILY = DEV_BASE_URL + "Home/Family/{}"
DEV_GET_FULL_FAMILY = DEV_BASE_URL + "v2/Home/Family/{}"
DEV_GET_SHARED_FILES = DEV_BASE_URL + "SharedFiles"
DEV_GET_SHARED_FILE = DEV_BASE_URL + "SharedFile/{}"
DEV_QUERY_FAMILIES = DEV_GET_SHARED_FILE + "Families"
DEV_FAMILYFILES = DEV_BASE_URL + "FamilyFiles"
DEV_GET_FAMILIYFILE = DEV_FAMILYFILES + "?familyId={}"
DEV_GET_FILE = DEV_FAMILYFILES + "?fileId={}"
DEV_DELETE_FILE_MAP = DEV_BASE_URL + "FamilyFile/{}"

DEV_HEADERS = {
    "Authorization": "Bearer {}".format(DEV_KEY),
    "Content-Type": "application/json",
}

# NOTION
NOTION_BASE_URL = "https://api.notion.com/v1/"
NOTION_DATABASE = NOTION_BASE_URL + "databases/"
NOTION_PAGE = NOTION_BASE_URL + "pages/"

NOTION_HEADERS = {
    "Authorization": NOTION_KEY,
    "Content-Type": "application/json",
    "Notion-Version": "2022-02-22",
}

NOTION_DATABASE_IDS = {
    "Campaigns": "2b9338bdaa734510a9749309f39fc49c",
    "Content Calendar": "f56ac916a3f049dda2df0f864ca63c62",
    "Tasks": "0e928f7862ff402e80f18f66ec4ef32b",
    "Meeting Notes": "58c6d06af6194888907932d4870c6cab",
    "Documents": "1b2dcc8fb26345f4a14ae0bd4cee495a",
    "Objectives": "d8b17a29e9c44520bf1b6aec3fecf6df",
    "Key Results": "f405be3d063a47ebb4ef180052987bd6",
    "Manufacturers": "8ef28b92d8104e7faf2560198854d741",
    "Product Lines": "590eb948598444368da8f55c434dcd85",
    "Products": "9928138a4e474b61b4c65fd990d07957",
    "Markets": "a90eec8443aa463183c4da06b1a0bbc6",
    "Materials": "96bd0836e1244e7d94985c342282542f",
    "Revit Categories": "3fa7e9f3905f432eaa9c8645b1ce0f98",
    "Tags": "a95cf3a5003846f98def36818d5836d4",
    "BIMobject Categories": "30ee9042b5cb4ddfa41d6d82c3b7afff",
    "BIMobject Materials": "f564e7cd24e2401b9801fa21a0e8d0ee",
    "BIMobject Masterformat2014": "a1a8d1982a9b4dc8b8cca008b16ed986",
    "BIMobject Uniformat2": "09e15c47c13249f1b0a34f3734111151",
    "BIMobject Omniclass": "0effd533b8a74310a8e816802f4b4c4b",
    "BIMobject IFC": "3288117b879f450cb58b14580fe041ab",
    "Shared Rules": "fd52b1109cf04974b9a76f71a25afc18",
    "Shared Attributes": "b734013d16164030a941e07ff000d0a5",
    "Learning Resources": "a31f04fce2e44b8982fd15d1734cf17f",
}
