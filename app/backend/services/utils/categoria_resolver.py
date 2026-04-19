from difflib import SequenceMatcher
from app.backend.services.bases import (
    proteinasKG, proteinasUN, carboidratos,
    carboidratosCF, frutas, legumes, cereais,
    massas, molhos, liquidos, farinhas
)

from app.backend.services.utils.base_dinamica import montar_base_dinamica
from app.backend.services.core.normalizacao import normalizar

