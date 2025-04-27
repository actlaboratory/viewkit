from configobj import ConfigObj
from .spec import Spec


class ConfigObjFactory:
    DEFAULT_INFILE: str = "data/settings.ini"
    
    def createConfigObj(cls, settingFilePath: str=None, specLines: list[str]=[]) -> ConfigObj:
        if settingFilePath == None:
            settingFilePath = cls.DEFAULT_INFILE
        spec = Spec.getSpec() + specLines
        return ConfigObj(infile=settingFilePath, configspec=spec, stringify=True)
