from __future__ import annotations

import base64
import tkinter
import httpx
import json

from enum import Enum
from typing import Optional
from tkinter import filedialog
from uuid import UUID

from pydantic import BaseModel, Field, FilePath
from fetchbim import client
from .utils import to_camel


class MissingFileError(Exception):
    """Raised when file data is empty"""

    pass


class FileKey(str, Enum):
    REVIT = "FamilyRevitFile"
    REVIT_15 = "FamilyRevitFile2015"
    REVIT_16 = "FamilyRevitFile2016"
    REVIT_17 = "FamilyRevitFile2017"
    REVIT_18 = "FamilyRevitFile2018"
    REVIT_19 = "FamilyRevitFile2019"
    REVIT_20 = "FamilyRevitFile2020"
    REVIT_21 = "FamilyRevitFile2021"
    REVIT_22 = "FamilyRevitFile2022"
    IMAGE_LG = "FamilyImageLarge"
    IMAGE_MD = "FamilyImageMedium"
    IMAGE_SM = "FamilyImageSmall"
    RENDER_LG = "FamilyRenderingLarge"
    RENDER_MD = "FamilyRenderingMedium"
    RENDER_SM = "FamilyRenderingSmall"
    CSI_SPEC = "DOC-CSISpec"
    WARRANTY = "PDF-Warranty"
    SUSTAIN = "PDF-Sustainability"
    SPEC_MANUAL = "PDF-SpecManual"
    FINISHES = "PDF-FinishOptions"
    DRAWING = "PDF-Drawing"
    GENERIC_1 = "PDF-Generic1"
    GENERIC_2 = "PDF-Generic2"
    GENERIC_3 = "PDF-Generic3"
    GENERIC_4 = "PDF-Generic4"
    GENERIC_5 = "PDF-Generic5"
    MATERIAL = "MaterialLibrary"
    GALLERY_1 = "FamilyGalleryLarge1"
    GALLERY_2 = "FamilyGalleryLarge2"
    GALLERY_3 = "FamilyGalleryLarge3"
    GALLERY_4 = "FamilyGalleryLarge4"
    GALLERY_5 = "FamilyGalleryLarge5"
    GALLERY_6 = "FamilyGalleryLarge6"
    GALLERY_7 = "FamilyGalleryLarge7"
    GALLERY_8 = "FamilyGalleryLarge8"
    GALLERY_9 = "FamilyGalleryLarge9"
    GALLERY_10 = "FamilyGalleryLarge10"
    GALLERY_11 = "FamilyGalleryLarge11"
    GALLERY_12 = "FamilyGalleryLarge12"
    GALLERY_13 = "FamilyGalleryLarge13"
    GALLERY_14 = "FamilyGalleryLarge14"
    GALLERY_15 = "FamilyGalleryLarge15"

    def __str__(self):
        return self.value


class FamilyFile(BaseModel):
    id: int = Field(default=None, alias="FamilyFileId")
    family_id: UUID | str
    file_id: int = Field(..., repr=False)

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class SharedFileMapping(BaseModel):
    id: int = Field(default=None, alias="SharedFileId")
    file_id: int

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class File(BaseModel):
    id: int = Field(default=None, alias="FileId")
    name: str = Field(None, alias="FileName")
    extension: str = Field(None, alias="FileExtension")
    deleted: bool = False
    key: Optional[str] = Field(
        None,
        alias="FileKey",
    )
    data: Optional[str] = Field(None, alias="FileData", repr=False)
    path: Optional[FilePath] = Field(None, alias="FilePath", repr=False)
    family_file_ids: Optional[list[FamilyFile]] = None
    shared_file_ids: Optional[list[SharedFileMapping]] = []

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        use_enum_values = True

    def file_from_path(self) -> None:
        try:
            with open(self.path, "rb") as file:
                byteform = base64.b64encode(file.read())
                self.data = byteform.decode("utf-8")
        except TypeError as e:
            print(f"File path is incorrect: {e}")

    @classmethod
    def pick_file(cls, key: str) -> File:
        """Returns a file object based on file selector dialog

        Args:
            file_key (str):
                File key represented as a string. File key designates how the
                file will be treated in app. Example: "FamilyRevitFile"

        Returns:
            File: File object based on local file.
        """
        root = tkinter.Tk()
        root.withdraw()

        file_path = filedialog.askopenfilename()
        file_ext = file_path.split(".")[-1]
        file_name = file_path.split("/")[-1].split(".")[0]
        c = cls(
            FilePath=file_path,
            FileExtension=file_ext,
            FileName=file_name,
            FileKey=key,
            FileId=0,
            FileData=None,
        )
        c.file_from_path()
        return c

    @classmethod
    def from_id(cls, id: int) -> File:
        """Returns a new File instance based on the file id.

        Args:
            id (int): File Id.

        Returns:
            File: File object with corresponding id
        """
        return File.search(id=id)[0]

    def create(self) -> dict:
        path = "/Files"
        if self.data is None:
            if self.path:
                self.file_from_path()
            else:
                self.pick_file(self.key)
        if self.data is None:
            raise MissingFileError
        else:
            response = client.post(
                path,
                timeout=None,
                json=self.dict(
                    by_alias=True,
                    include={"name", "extension", "data", "key"},
                ),
            )
            return response.json()

    def update(self, field_names: list[str]) -> dict:
        path = "/File"
        field_names.append("id")
        data = self.dict(by_alias=True, include=set(field_names))
        response = client.patch(path, json=data)
        return response.json()

    def delete(self):
        self.deleted = True
        return self.update(field_names=["deleted"])

    def restore(self):
        self.deleted = False
        return self.update(field_names=["deleted"])

    def replace(self) -> httpx.Response:
        """Replaces file of given FileId with base64 FileData binary file.
        Optional parameters will default to existing values for given FileId.
        Updates any existing Family <-> File mappings.
        Updates any shared file references.

        Returns:
            dict: Response dictionary containing newly created file
        """
        path = f"/File/{self.id}"
        data = {}
        if self.data is None:
            if self.path:
                self.file_from_path()
            else:
                self.pick_file(self.key)
        if self.data is None:
            raise MissingFileError
        else:
            response = client.put(
                path, json=self.dict(by_alias=True, exclude={"path"}), timeout=None
            )
            return response.json()

    def get_mappings(self):
        path = "/FamilyFiles"
        response = client.get(path, params=self.dict(by_alias=True, include={"id"}))
        print(response.url)
        return response.json()

    # def get_family_ids(self):
    #     response = self.get_mappings()
    #     return [mapping["FamilyId"] for mapping in response]

    @staticmethod
    def get_all_mappings():
        path = "/FamilyFiles"
        response = client.get(path)
        return response.json()

    @staticmethod
    def search(
        name: Optional[str] = None,
        key: Optional[str] = None,
        extension: Optional[str] = None,
        id: Optional[int] = None,
        deleted: Optional[bool] = False,
    ) -> list[File]:
        """Returns list of Files by searching database based on search criteria

        Args:
            name (Optional[str], optional): Name of file - Contains string. Defaults to None.
            key (Optional[str], optional): File key - Exact match. Defaults to None.
            extension (Optional[str], optional): File extension - Exact match. Defaults to None.
            id (Optional[str], optional): File id - Exact match. Defaults to None.

        Returns:
            list[File]: List of File objects
        """
        path = "/Files"
        params = {}
        if name:
            params["FileName"] = name
        if key:
            params["FileKey"] = key
        if extension:
            params["FileExtension"] = extension
        if id:
            params["fileId"] = id
        params["Deleted"] = deleted
        response = client.get(path, params=params, timeout=60.0)
        return [File(**_file) for _file in response.json()]

    def attach_to_families(self, family_ids: list[str]) -> dict:
        path = "/FamilyFiles"
        data = [{"FamilyId": family_id, "FileId": self.id} for family_id in family_ids]
        response = client.post(path, json=data)
        return response.json()

    def remove_from_families(self) -> None:
        for fam_file in self.fam_file_ids:
            path = f"/FamilyFiles/{self.fam_file.id}"
            response = client.delete(path)
            # return response.json()

    def get_shared_file_ids(self) -> str | None:
        if self.shared_file_ids:
            return ",".join(set(str(mapping.id) for mapping in self.shared_file_ids))

    def get_family_ids(self) -> str | None:
        if self.family_file_ids:
            return ",".join(
                set(str(family_file.family_id) for family_file in self.family_file_ids)
            )
