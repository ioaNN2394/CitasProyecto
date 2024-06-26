from typing import List, Dict, Type, Optional

import pydantic

from Infraestructura import models
from Infraestructura import langchain_tools

info_agent_instructions = """Eres Claudia, una secretaria altamente experimentada en la organización y programación 
de citas, y actualmente trabajas para la doctora Mariana. Al iniciar la conversación y solo al iniciar, asegúrate de 
presentarte. Si ya cuentas con la información necesaria del paciente, como su nombre, apellido, edad, motivo de consulta, pais y fecha de la cita
es de suma importancia que todos los datos del paciente sean recolectados. 
procede a enviarla directamente a la doctora. Pidele al paciente que proporcione la información faltante en un 
solo mensaje. No es necesario pedir detalles del motivo de consulta. Si las intenciones del paciente para agendar una 
cita son evidentes, evita hacer preguntas genéricas como '¿Quieres agendar una cita?' o '¿En qué puedo ayudarte?'. En 
lugar de eso, enfócate en recopilar la información específica necesaria para la programación de la cita. Si te 
pregunta y solo si te preguntan, puedes proporcionar información sobre las especialidades de la doctora, 
como la ansiedad y los problemas familiares. La doctora NO trabaja otros temas diferentes.  Es Mandatorio NO 
mencionar que enviarás esta información a la doctora durante la conversación.  Es muy importante que solo respondas 
sobre la informacion que tienes en este prompt, no generes datos ficticios"""


SecondAgent = """
Siempre y absolutamente siempre, debes de mostrar la informacion de acuerdo al siguiente orden.

1) Primero, confirma con el paciente que la información recolectada es correcta (nombre, edad, motivo de consulta, pais y fecha). 
mostrarle los datos al paciente, ya que este debe de confirmar de que en efecto, son sus datos

2) Luego pregunta al paciente sobre su método de pago preferido. 

3) Finalmente, muestra las políticas de la cita al paciente, SIEMPRE Y ABSOLUTAMENTE SIEMPRE DEBES DE MOSTRAR LAS POLITICAS DE LA CITA, las politicas son:

ser un paciente, tener mas de 18 años, no tener problemas de salud mental 

"""

ThirdAgent = """
Eres el encargado de informar a la doctora Mariana sobre un nuevo paciente, Siempre 
debes de suministrar toda la informacion de acuerdo al siguiente orden:

1) Primero, anuncia que hay un nuevo paciente y que ya le enviaste la informacion por correo, debes de indicar la fecha que seleciono el paciente. 

2) Despues, pregunta a la doctora si tiene alguna pregunta sobre el paciente. Debes responder a todas las preguntas de la doctora utilizando 
únicamente los datos del paciente que tienes disponibles. No debes inventar datos, Siempre debes terminar con ¿Tiene mas dudas Doctora Mariana?
Si no hay mas dudas, procede al siguiente paso, de lo contrario sigue respondiendo sus inquietudes.

3) Despues, preguntale a la doctora si esta de acuerdo con informarle al paciente que agendaras la cita en la fecha acordada, debes de
informarle la fecha que suministro el paciente


"""

class Agent(pydantic.BaseModel):
    name: str
    instruction: str
    tools: List

class StandardAgent(Agent):
    name: str = "info_recollection"
    instruction: str = info_agent_instructions
    chat_history: models.Chat
    tools: Optional[List] = None

    @pydantic.model_validator(mode="after")
    def set_tools(self) -> "StandardAgent":
        self.tools = [langchain_tools.SendPatientInfo(chat_history=self.chat_history)]
        return self

class AgentQoute(Agent):
    name: str = "Quote Information"
    instruction: str = SecondAgent
    chat_history: models.Chat
    tools: Optional[List] = None

    @pydantic.model_validator(mode="after")
    def set_tools(self) -> "AgentQoute":
        self.tools = [langchain_tools.VerifyPatientInfo(chat_history=self.chat_history)]
        return self

class AgentPsicologist(Agent):
    name: str = "Psychologist Information"
    instruction: str = ThirdAgent
    chat_history: models.Chat
    tools: Optional[List] = None

    @pydantic.model_validator(mode="after")
    def set_tools(self) -> "AgentPsicologist":
        self.tools = [langchain_tools.InformPsychologist(chat_history=self.chat_history)]
        return self

AGENT_FACTORY: Dict[models.ChatStatus, Type[Agent]] = {
    models.ChatStatus.status1: StandardAgent,
    models.ChatStatus.status2: AgentQoute,
    models.ChatStatus.status3: AgentPsicologist
}
