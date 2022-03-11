from pytest import fixture
from fetchbim import Family


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
def test_family_from_id(fam_keys):
    """Tests an API call to get a Family's from it's GUID"""
    guid = {"id": "b3d9f8ca-2564-4c1b-b192-3ac22fcdb86d"}
    fam = Family.from_id(guid)

    assert isinstance(fam, Family)
    assert fam.Id == guid, "The ID should be in the response"
    assert set(fam_keys).issubset(fam._json["BusinessFamilies"][0].keys()), "All keys should be in the response"
