from pytest import fixture
from fetchbim import Family, client, BIM_HEADERS


@fixture
def fam_keys():
    """Responsible only for returning the test data"""
    return [
        "Id",
        "ReferenceId",
        "Name",
        "Version",
        "FriendlyName",
        "CategoryName",
        "ThumbnailUrl",
        "FamilyObjectType",
        "GroupedFamilies",
        "Files",
        "FamilyTypes",
        "Properties",
        "Deleted",
        "IsFavorite",
        "Private",
        "Parameters",
        "HasFamilyChanges",
        "Sort",
        "LoadMethod",
        "Status",
        "ListPrice",
        "InstanceCount",
        "UpdatedRevitFile",
        "HasUpdate",
        "RevitFileVersion",
        "TitleHeader",
        "TitleSubheader",
        "DownloadFamilyFile",
    ]


import vcr


@vcr.use_cassette("tests/vcr_cassettes/family-from-id.yml")
def test_family_from_id():
    """Tests an API call to get a Family's from it's GUID"""
    id = "b3d9f8ca-2564-4c1b-b192-3ac22fcdb86d"
    client.base_url = "https://www.ssgbim.com/api/"
    client.headers = BIM_HEADERS
    fam = Family.from_id(id)
    assert isinstance(fam, Family)
    assert fam.id == id, "The ID should be in the response"
