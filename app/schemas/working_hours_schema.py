from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Dict, Any # Any pode ser útil para o model_validator, Dict para a estrutura

# Não precisamos mais de 're' para regex diretamente no Field, Pydantic usa 'pattern'

# Schema para um único dia de trabalho
class DayWorkingHours(BaseModel):
    is_active: bool = False
    start_time: Optional[str] = Field(default=None, pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$") # Formato HH:MM
    end_time: Optional[str] = Field(default=None, pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")   # Formato HH:MM
    lunch_break_start_time: Optional[str] = Field(default=None, pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    lunch_break_end_time: Optional[str] = Field(default=None, pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")

    # Validador para permitir strings vazias como None (roda antes da validação de tipo do Pydantic)
    @field_validator('start_time', 'end_time', 'lunch_break_start_time', 'lunch_break_end_time', mode='before')
    @classmethod
    def allow_empty_string_as_none(cls, value: Optional[str]) -> Optional[str]:
        if value == "":
            return None
        return value

    # Validador para checar a lógica dos horários (roda depois dos validadores de campo individuais)
    @model_validator(mode='after')
    def check_times_logic(self) -> 'DayWorkingHours':
        # Verifica se o horário de término é depois do horário de início do expediente
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValueError('Horário de término do expediente deve ser após o horário de início.')
        elif self.is_active and (self.start_time or self.end_time): # Se ativo e um foi fornecido, o outro também deve ser
             if not (self.start_time and self.end_time):
                 raise ValueError('Se o dia está ativo e um horário (início ou fim) é fornecido, o outro também deve ser.')


        # Verifica a lógica da pausa para almoço
        if self.lunch_break_start_time and self.lunch_break_end_time:
            if self.lunch_break_end_time <= self.lunch_break_start_time:
                raise ValueError('Horário de término da pausa deve ser após o horário de início da pausa.')
            
            # Validação adicional: pausa para almoço deve estar dentro do horário de trabalho
            if self.start_time and self.end_time: # Garante que temos horário de trabalho definido para comparar
                if not (self.start_time <= self.lunch_break_start_time and \
                        self.lunch_break_start_time < self.lunch_break_end_time and \
                        self.lunch_break_end_time <= self.end_time):
                    raise ValueError('A pausa para almoço deve estar completamente dentro do horário de trabalho (início_exp < início_pausa < fim_pausa < fim_exp).')
            else:
                # Se não há horário de expediente definido, não deveria haver pausa
                raise ValueError('Não é possível definir pausa para almoço sem definir o horário de expediente (início e fim).')

        elif self.lunch_break_start_time or self.lunch_break_end_time:
            # Se um horário da pausa foi fornecido, o outro também deve ser
            raise ValueError('Se uma pausa para almoço for definida, tanto o horário de início quanto o de término da pausa devem ser fornecidos.')
            
        return self

# Schema para a configuração completa dos horários de atendimento
class WorkingHoursConfig(BaseModel):
    # Usar default_factory para garantir que uma nova instância de DayWorkingHours seja criada para cada dia como default
    monday: DayWorkingHours = Field(default_factory=DayWorkingHours)
    tuesday: DayWorkingHours = Field(default_factory=DayWorkingHours)
    wednesday: DayWorkingHours = Field(default_factory=DayWorkingHours)
    thursday: DayWorkingHours = Field(default_factory=DayWorkingHours)
    friday: DayWorkingHours = Field(default_factory=DayWorkingHours)
    saturday: DayWorkingHours = Field(default_factory=DayWorkingHours)
    sunday: DayWorkingHours = Field(default_factory=DayWorkingHours)
    appointment_interval_minutes: Optional[int] = Field(default=30, gt=0) # Default 30 min, e deve ser > 0

    class Config:
        validate_assignment = True # Garante que validações rodem ao reatribuir valores aos campos
"""
Explicação dos Novos Schemas:
- DayWorkingHours: Define a estrutura para cada dia da semana.
    - is_active: Se o estabelecimento funciona no dia.
    - start_time, end_time, etc.: Horários no formato "HH:MM". Usamos Field(None, regex=...) para tornar o campo opcional (default None) e para adicionar uma validação de formato usando expressão regular.
    - allow_empty_string_as_none: Um validador que permite que o frontend envie uma string vazia para os campos de hora opcionais, e o Pydantic a converterá para None. Isso pode facilitar o manuseio de formulários no frontend.
    - check_end_time_after_start_time: Um validador para garantir que o horário de término seja depois do horário de início (tanto para o expediente quanto para a pausa).
- WorkingHoursConfig: Contém um campo para cada dia da semana (do tipo DayWorkingHours, com valores default para um dia inativo) e o appointment_interval_minutes.
    - Field(30, gt=0): Para appointment_interval_minutes, define um valor default de 30 minutos e garante que seja maior que zero.
    - validate_assignment = True: Boa prática para garantir que as validações rodem mesmo se você modificar um campo após a criação do objeto.
"""