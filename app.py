import asyncio

from fastapi import FastAPI
from pydantic import BaseModel

from seleniumbase import SB


app = FastAPI()

class Document(BaseModel):
    nit: str

@app.post("/rut")
async def get_rut_data(document: Document):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, process, document.nit)
    return result

def process(nit):
    with SB(uc=True) as sb:
        url = "https://muisca.dian.gov.co/WebRutMuisca/DefConsultaEstadoRUT.faces"
        sb.activate_cdp_mode(url)
        sb.sleep(2)
        sb.uc_gui_click_captcha()
        sb.sleep(2)
        sb.type('#vistaConsultaEstadoRUT\\:formConsultaEstadoRUT\\:numNit', nit)
        
        sb.click('#vistaConsultaEstadoRUT\\:formConsultaEstadoRUT\\:btnBuscar')
        
        dv = sb.get_text("#vistaConsultaEstadoRUT\\:formConsultaEstadoRUT\\:dv")
        estado = sb.get_text("#vistaConsultaEstadoRUT\\:formConsultaEstadoRUT\\:estado")

        try:
            primer_apellido = sb.get_text("#vistaConsultaEstadoRUT\\:formConsultaEstadoRUT\\:primerApellido")
            segundo_apellido = sb.get_text("#vistaConsultaEstadoRUT\\:formConsultaEstadoRUT\\:segundoApellido")
            primer_nombre = sb.get_text("#vistaConsultaEstadoRUT\\:formConsultaEstadoRUT\\:primerNombre")
            segundo_nombre = sb.get_text("#vistaConsultaEstadoRUT\\:formConsultaEstadoRUT\\:otrosNombres")
            contributor_type = "NATURAL_PERSON"
            social_reason = ""
        except Exception as e:
            print(e)
            primer_apellido, segundo_apellido, primer_nombre, segundo_nombre = "", "", "", ""
            contributor_type = "JURIDICAL_PERSON"
            social_reason = sb.get_text("#vistaConsultaEstadoRUT\\:formConsultaEstadoRUT\\:razonSocial")
        
        return {
            "NIT": nit,
            "DV": dv,
            "State": estado,
            "ContributorType": contributor_type,
            "NaturalPerson": {
                "FirstName": primer_nombre,
                "MiddleName": segundo_nombre,
                "LastName": primer_apellido,
                "SecondLastName": segundo_apellido
            },
            "JuridicalPerson": {
                "SocialReason": social_reason
            }
        }
