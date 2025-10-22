from typing import Annotated,  Literal
from pydantic import BaseModel, Field, ConfigDict

class HospitalNoMeta(BaseModel):
    model_config = ConfigDict(extra='ignore')
    hospital_id:        str
    hospital_capacity:  Annotated[int, Field(ge=4, le=99)]
    icu_beds:            Annotated[float, Field(ge=-1, le=14)]
    er_beds:            Annotated[float, Field(ge=-1, le=25)]	

class Hospital(HospitalNoMeta):
    hospital_area:      Literal['충주시','안성시','이천시','제천시','원주시','보은군','단양군','영동군','괴산군','음성군','청주시','옥천군','증평군','진천군']	
    is_24h:             bool
    has_er:             bool 									    
    is_regional_center: bool
    specialist_oncall:  bool


