# coding: utf-8
import settings

dlmis = "dlmis" if settings.dbTypeName.lower() == "oracle" else ""
dlhist = "dlhist" if settings.dbTypeName.lower() == "oracle" else ""
dlsys = "dlsys" if settings.dbTypeName.lower() == "oracle" else ""
umstat = "umstat" if settings.dbTypeName.lower() == "oracle" else ""
dlmis_ = "dlmis." if settings.dbTypeName.lower() == "oracle" else ""
dlhist_ = "dlhist." if settings.dbTypeName.lower() == "oracle" else ""
dlsys_ = "dlsys." if settings.dbTypeName.lower() == "oracle" else ""
umstat_ = "umstat." if settings.dbTypeName.lower() == "oracle" else ""